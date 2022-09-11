from inspect import istraceback
import pandas as pd
import json
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table
from azure.kusto.data.data_format import DataFormat
from azure.kusto.ingest import QueuedIngestClient, IngestionProperties, FileDescriptor, BlobDescriptor, ReportLevel, ReportMethod

from app.server.models import DNSRecord
from app.server.modules.organization.Company import EmployeeShell
from app.server.modules.outbound_browsing.outboundEvent import OutboundEvent
from app.server.modules.endpoints.file_creation_event import FileCreationEvent
from app.server.modules.email.email import Email

from flask import current_app
#see https://github.com/Azure/azure-kusto-python/blob/master/azure-kusto-ingest/tests/sample.py


class LogUploader():
    def __init__(self, queue_limit=1000):
        # set Azure tenant config variables
        self.AAD_TENANT_ID =  current_app.config["AAD_TENANT_ID"] 
        self.KUSTO_URI =  current_app.config["KUSTO_URI"]  
        self.KUSTO_INGEST_URI =  current_app.config["KUSTO_INGEST_URI"]
        self.DATABASE =  current_app.config["DATABASE"] 
        self.CUSTOM_TYPES = [DNSRecord, EmployeeShell, OutboundEvent, FileCreationEvent, Email]
        # self.TABLE = "emailtest"

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

        # upload queue
        # this will allow us to upload multiple rows at once
        # self.queue will be in the format:
        # {
        #   "table_name": [dict, dict, dict],
        #   "table_name2": [dict, dict, dict]
        # }
        self.queue = {}  
        # how many records do we hold until submitting everything to kusto
        self.queue_limit = queue_limit


    def create_tables(self, reset:bool=False):
        """
        Create the tables that the logs will be uploaded to
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
            
        print("\n\n\n".join(drop_table_commands))
        print("\n\n\n".join(create_table_commands))

        # Execute the Kql commands
        for command in (drop_table_commands + create_table_commands):
            response = self.client.execute_mgmt(self.DATABASE, command)
            print(response)

    @staticmethod
    def create_table_command(table_name:str, table_options:dict) -> str:
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
        command_parts = [f"['{col}']:{val_type}" for col, val_type in table_options.items()]
        kql_command = kql_command + "(" + ",\n".join(command_parts) + ")"

        return kql_command


    def get_queue_length(self):
        """
        Get the number of records stored in the queue
        this does a sum of lengths for lists under each tablename key
        """
        return sum([len(val) for key, val in self.queue.items()])
        

    def send_request(self, data, table_name="emailtest"):
        """
        Data is ingested as JSON
        convert to a pandas dataframe and upload to KUSTO
        """
        # if table_name in ["FileCreationEvent", "OutboundBrowsingEvents"]:
        #     print(f"Would have sent some data to {table_name} in Azure")
        #     print(json.dumps(data, indent=4))

     
        # put data in a dataframe for ingestion
        if isinstance(data, list):
                data = data[0]

        if table_name in self.queue:
            self.queue[table_name].append(data)
        else:
            
            self.queue[table_name] = [data]


        if self.get_queue_length() > self.queue_limit:
            # reached the queue limit
            # submit all existing records and clear the queue
            for table_name, data in self.queue.items():
                self.ingestion_props = IngestionProperties(
                    database=self.DATABASE,
                    table=table_name,
                    data_format=DataFormat.CSV,
                    report_level=ReportLevel.FailuresAndSuccesses
                )
          
                # turn list of rows in a dataframe
                data_table_df = pd.DataFrame(self.queue[table_name])

                print(f"uploading data for type {table_name}")
                print(data_table_df.shape)
                result = self.ingest.ingest_from_dataframe(data_table_df, ingestion_properties=self.ingestion_props)
                print(result)
                print(f"....adding data to azure for {table_name} table")


            self.queue  = {}

        # print(json.dumps(self.queue, indent=4))
        # self.data = pd.DataFrame(data)  # data should be a json blob

        # # set ingestion properties
        # self.ingestion_props = IngestionProperties(
        #     database=self.DATABASE,
        #     table=table_name,
        #     data_format=DataFormat.CSV,
        #     report_level=ReportLevel.FailuresAndSuccesses
        # )

        