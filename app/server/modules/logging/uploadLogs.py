import pandas as pd
import json
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table
from azure.kusto.data.data_format import DataFormat
from azure.kusto.ingest import QueuedIngestClient, IngestionProperties, FileDescriptor, BlobDescriptor, ReportLevel, ReportMethod

from flask import current_app
#see https://github.com/Azure/azure-kusto-python/blob/master/azure-kusto-ingest/tests/sample.py


class LogUploader():


    def __init__(self):
        # authenticate using a registered APP
        self.AAD_TENANT_ID =  current_app.config["AAD_TENANT_ID"] 
        self.KUSTO_URI =  current_app.config["KUSTO_URI"]  
        self.KUSTO_INGEST_URI =  current_app.config["KUSTO_INGEST_URI"]
        self.DATABASE =  current_app.config["DATABASE"] 
        # self.TABLE = "emailtest"

        # In case you want to authenticate with AAD application.
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


    def create_tables(self):
        #TODO Create all the necessary tables
        # This should be done in the main controller during the init stage
        create_table_commands = [
        """.create table ['Email']  
            (['event_time']:string, 
            ['sender']:string, 
            ['reply_to']:string, 
            ['recipient']:string, 
            ['subject']:string, 
            ['accepted']:bool, 
            ['link']:string)""",

        """.create table ['CompanyInfo']  
            (['name']:string, 
            ['user_agent']:string, 
            ['ip_addr']:string, 
            ['email_addr']:string, 
            ['company_domain']:string)""",

        """.create table ['PassiveDNS']  
            (['ip']:string, 
            ['domain']:string)""",

        """.create table ['OutboundBrowsingEvents']  
            (['time']:string, 
            ['method']:string, 
            ['src_ip']:string, 
            ['user_agent']:string, 
            ['url']:string)
        """ ]
        # print(help(self.client))
        # command =  """.create table ['PassiveDNS'] (['ip']:string, ['domain']:string)"""
        # response = self.client.execute_mgmt(self.DATABASE, command)
        # print(response)

        for command in create_table_commands:
            response = self.client.execute_mgmt(self.DATABASE, command)
        print(response)


    def send_request(self, data, table_name="emailtest"):

        # put data in a dataframe for ingestion
        self.data = pd.DataFrame(data)  # data should be a json blob

        # set ingestion properties
        self.ingestion_props = IngestionProperties(
            database=self.DATABASE,
            table=table_name,
            data_format=DataFormat.CSV,
            report_level=ReportLevel.FailuresAndSuccesses
        )

        result = self.ingest.ingest_from_dataframe(self.data, ingestion_properties=self.ingestion_props)
        # print(result)
        print(f"....adding data to azure for {table_name} table")