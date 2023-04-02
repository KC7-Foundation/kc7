# Import external modules
from inspect import istraceback
from multiprocessing.dummy import Process
import pandas as pd
import json
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table
from azure.kusto.data.data_format import DataFormat
from azure.kusto.ingest import QueuedIngestClient, IngestionProperties, FileDescriptor, BlobDescriptor, ReportLevel, ReportMethod
from flask import current_app
from azure.kusto.data.helpers import dataframe_from_result_table

# Import internal modules
from app.server.modules.outbound_browsing.outboundEvent import OutboundEvent
from app.server.modules.endpoints.file_creation_event import FileCreationEvent
from app.server.modules.endpoints.processes import ProcessEvent
from app.server.modules.email.email import Email
from app.server.modules.infrastructure.DNSRecord import DNSRecord
from app.server.modules.organization.Company import Employee
from app.server.modules.authentication.authenticationEvent import AuthenticationEvent
from app.server.modules.inbound_browsing.inboundEvent import InboundBrowsingEvent
from app.server.modules.alerts.alerts import SecurityAlert


class LogUploader():
    """
    Object allows us to upload data to azure
    Logs are batched and uploaded to their corresponding table after queue is full
    First: ingestion properties are read from the flaks config in Config.py

    see: https://github.com/Azure/azure-kusto-python/blob/master/azure-kusto-ingest/tests/sample.py
    """

    def __init__(self, queue_limit=1000):
        # set Azure tenant config variables
        self.AAD_TENANT_ID = current_app.config["AAD_TENANT_ID"]
        self.KUSTO_URI = current_app.config["KUSTO_URI"]
        self.KUSTO_INGEST_URI = current_app.config["KUSTO_INGEST_URI"]
        self.DATABASE = current_app.config["DATABASE"]
        self.CUSTOM_TYPES = [
                                DNSRecord, Employee,
                                OutboundEvent, FileCreationEvent, 
                                Email, AuthenticationEvent, InboundBrowsingEvent, 
                                ProcessEvent, SecurityAlert]

        # Aauthenticate with AAD application.
        self.client_id = current_app.config["CLIENT_ID"]
        self.client_secret = current_app.config["CLIENT_SECRET"]

        # authentication for ingestion client
        kcsb_ingest = KustoConnectionStringBuilder.with_aad_application_key_authentication(self.KUSTO_INGEST_URI,
                                                                                           self.client_id, self.client_secret, self.AAD_TENANT_ID)

        # authentication for general client
        kcsb_data = KustoConnectionStringBuilder.with_aad_application_key_authentication(self.KUSTO_URI,
                                                                                         self.client_id, self.client_secret, self.AAD_TENANT_ID)

        self.ingest = QueuedIngestClient(kcsb_ingest)
        self.client = KustoClient(kcsb_data)

        # The queue will allow us to upload multiple rows at once
        # This allows the game to runs faster and enable us to make fewer API calls
        # self.queue will be in the format:
        # {
        #   "table_name": [dict, dict, dict],
        #   "table_name2": [dict, dict, dict]
        # }
        self.queue = {}
        # how many records do we hold until submitting everything to kusto
        self.queue_limit = queue_limit
        # this reflect the total sum of events that have been generated
        # similar to the queue but doesnt get reset
        self.tally = {}

    def create_tables(self, reset: bool = False) -> None:
        """
        Create the tables that the logs will be uploaded to in Kusto
        """
        # Get KQL representation of each Class object
        drop_table_commands = []
        create_table_commands = []

        for custom_type in self.CUSTOM_TYPES:
            table_name, kql_repr = custom_type.get_kql_repr()
            command = LogUploader.create_table_command(table_name, kql_repr)
            create_table_commands.append(command)
            if reset:
                drop_table_commands.append(
                    f".drop table {table_name} ifexists"
                )

        # print("\n\n\n".join(drop_table_commands))
        # print("\n\n\n".join(create_table_commands))

        if current_app.config["ADX_DEBUG_MODE"]:
            # If ADX_DEBUG_MODE is enabled, return early
            # This will prevent creating tables on the ADX cluster
            return

        # Execute the Kql commands
        for command in (drop_table_commands + create_table_commands):
            response = self.client.execute_mgmt(self.DATABASE, command)
            print(response)

    @staticmethod
    def create_table_command(table_name: str, table_options: dict) -> str:
        """
        Take in a dictionary of options
        Generate texts required to create a new table in Kusto

        Input dict: {
            "time": "string",
            "method":"string",
            "scr_ip":"string",
            "user_agent":"string",
            "url", "string"
        }
        Example:
        create table ['OutboundBrowsingEvents']  
            (['time']:string, 
            ['method']:string, 
            ['src_ip']:string, 
            ['user_agent']:string, 
            ['url']:string)
        """

        kql_command = f".create table ['{table_name}']\n"
        command_parts = [f"['{col}']:{val_type}" for col,
                         val_type in table_options.items()]
        kql_command = kql_command + "(" + ",\n".join(command_parts) + ")"

        return kql_command

    @staticmethod
    def _create_user_permission_command(user_string:str, database: str) -> str:
        """
        Take a user string of the following format:
        aaduser=user@contoso.com
        msauser=user@outlook.com
        """
        # Does the user_string contain one of the required identifiers?
        if not any(prefix in user_string for prefix in ['aaduser=','msauser=']):
            raise Exception("ERROR: The user identifier must be prefixed by either aaduser= or msauser=")
        return f".add database {database} viewers ('{user_string}')"

    def get_user_permissions(self) -> list:
        """
        Get a list of user permissions from ADX
        """
        show_permissions_command = f".show database {self.DATABASE} principals | distinct PrincipalDisplayName"
        response = self.client.execute_mgmt(self.DATABASE, show_permissions_command)

        # Handle errors from Kusto Client
        if response.get_exceptions():
            raise response.get_exceptions()

        return dataframe_from_result_table(response.primary_results[0])['PrincipalDisplayName'].unique().tolist()

    def add_user_permissions(self, user_string: str) -> None:
        permission_command = LogUploader._create_user_permission_command(user_string, self.DATABASE)
        response = self.client.execute_mgmt(self.DATABASE, permission_command)
        # Raise any errors that come back from 
        if response.get_exceptions():
            raise response.get_exceptions()

    def get_queue_length(self):
        """
        Get the number of records stored in the queue
        this does a sum of lengths for lists under each tablename key
        """
        return sum([len(val) for key, val in self.queue.items()])

    def update_tally(self):
        """
        Adds all the values in dict1 to the values in dict2 with the corresponding keynames.

        Args:
            dict1 (dict): The first dictionary.
            dict2 (dict): The second dictionary.

        Returns:
            dict: A dictionary with the same keys as dict2 and the values equal to the sum of the corresponding values in dict1 and dict2.
        """
        for key, value in self.queue.items():
            if key in self.tally.keys():
                self.tally[key] = len(value) + self.tally[key]
            else:
                self.tally[key] = len(value)
        


    def send_request(self, data: dict, table_name: str) -> None:
        """
        Data is ingested as JSON
        convert to a pandas dataframe and upload to KUSTO
        """

        # put data in a dataframe for ingestion
        if isinstance(data, list):
            data = data[0]

        # Add the data to the queue
        # Data is appended to a list under table_name key in self.queue
        # e.g. {
        #    "table_name": [data]
        # }
        if table_name in self.queue:
            self.queue[table_name].append(data)
        else:
            self.queue[table_name] = [data]

        # reached the queue limit
        # submit all existing records and clear the queue
        if self.get_queue_length() > self.queue_limit:
            self.submit_queue()
            # add queue to tally
            self.update_tally()
            # reset the quee
            self.queue = {}
        else:
            pass
            # print(f"======> Submission queue @ {self.get_queue_length()}")


    def submit_queue(self):
        """
        Submit everything in the qeue to ADX (or print in DEV)
        """
        for table_name, data in self.queue.items():
            self.ingestion_props = IngestionProperties(
                database=self.DATABASE,
                table=table_name,
                data_format=DataFormat.CSV,
                report_level=ReportLevel.FailuresAndSuccesses
            )

            # turn list of rows in a dataframe
            # TODO: sort by time before uploading -
            #   need to first standardize time columns accross tables
            data_table_df = pd.DataFrame(self.queue[table_name])
            
            try:
                # if possible sort value using the "timestamp" column
                data_table_df = data_table_df.sort_values("timestamp", ascending=True)
            except Exception as e:
                print(f"failed to sort rows: {e}")


            print(f"uploading data for type {table_name}")
            print(data_table_df.shape)

            if current_app.config["ADX_DEBUG_MODE"]:
                # If ADX_DEBUG_MODE is enabled, print JSON representation of data
                # Then, return early to prevent queueing and uploading to ADX
                print(f"Uploading to table {table_name}...")

                # uncomment this to print data add data
                # print(data_table_df.to_markdown())

                # uncomment this to print data generated a event type
                if table_name == "Email":
                    print(data_table_df.to_markdown())
            else:
                # submit logs to Kusto
                result =  self.ingest.ingest_from_dataframe(
                    data_table_df, ingestion_properties=self.ingestion_props)
                print(result)
                print(f"....adding {data_table_df.shape} to azure for {table_name} table")