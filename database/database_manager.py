from azure.kusto.data import KustoClient, KustoConnectionStringBuilder, DataFormat
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table
from azure.kusto.ingest import IngestionProperties, QueuedIngestClient
import pandas as pd
import logging


class AzureDatabaseManager:
    def __init__(self, database):
        self.connection_string = "https://kvc3vyswugka1463f9f0e3.northeurope.kusto.windows.net/shiba"
        self.aad_app_id = "6aed01c7-b86c-461a-857c-6ed3f234ca67"
        self.app_key = "gSC8Q~bzSfOg8FWMd1y2582fCa-b1mnzWc_QXbD9"
        self.authority_id = "f04f3e7f-6fe8-4613-b5e3-791d54cc7573"
        self.database = database
        self.kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(
            self.connection_string, aad_app_id=self.aad_app_id, app_key=self.app_key, authority_id=self.authority_id)
        self.client = None
        self.tables = ['IGH', 'TRB', 'TRG']
        self._connect()

    def _connect(self):
        self.client = KustoClient(self.kcsb)

    def _disconnect(self):
        self.client.close()

    def get_table_names(self):
        return self.tables

    def execute_query(self, query):
        try:
            response = self.client.execute(self.database, query)
            return response
        except KustoServiceError as error:
            print("Error:", error)
            print("Is semantic error:", error.is_semantic_error())
            print("Has partial results:", error.has_partial_results())
            print("Result size:", len(error.get_partial_results()))

    def get_all_participants_names(self):
        participants = []
        for table_name in self.tables:
            participants.append(dataframe_from_result_table(
                self.execute_query(f'{table_name} | distinct individual').primary_results[0]))
        return pd.concat(participants)['individual']

    def get_all_patient_names(self):
        patient = []
        for table_name in self.tables:
            patient.append(dataframe_from_result_table(self.execute_query(
                f'{table_name} | where not(individual startswith "C_") | distinct individual').primary_results[0]))
        return pd.concat(patient)['individual']

    def get_all_control_names(self):
        controls = []
        for table_name in self.tables:
            controls.append(dataframe_from_result_table(self.execute_query(
                f'{table_name} | where individual startswith "C_" | distinct individual').primary_results[0]))
        return pd.concat(controls)['individual']

    def get_participants_names_from_table(self, table_name):
        return dataframe_from_result_table(
            self.execute_query(f'{table_name} | distinct individual').primary_results[0])['individual']

    def get_patient_names_from_table(self, table_name):
        return dataframe_from_result_table(self.execute_query(
            f'{table_name} | where not(individual startswith "C_") | distinct individual').primary_results[0])[
            'individual']

    def get_control_names_from_table(self, table_name):
        return dataframe_from_result_table(self.execute_query(
            f'{table_name} | where individual startswith "C_" | distinct individual').primary_results[0])['individual']

    def participant_exists(self, individual, table_name):
        result = self.execute_query(f"{table_name} | where ['individual'] == '{individual}' | take 1")
        return result.primary_results[0].rows_count != 0

    def get_participant_data(self, individual, table_name):
        result = self.execute_query(
            f"{table_name} | where (['individual'] == '{individual}'"
            f" and ['functionality'] == 'productive') | project cdr3aa, total")
        df = dataframe_from_result_table(result.primary_results[0])
        return df

    def insert_participant(self, df, table_name):
        kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(
            "https://ingest-kvc3vyswugka1463f9f0e3.northeurope.kusto.windows.net/shiba",
            aad_app_id="6aed01c7-b86c-461a-857c-6ed3f234ca67",
            app_key="gSC8Q~bzSfOg8FWMd1y2582fCa-b1mnzWc_QXbD9",
            authority_id="f04f3e7f-6fe8-4613-b5e3-791d54cc7573"
        )
        ingestion_props = IngestionProperties(
            database=self.database,
            table=table_name,
            data_format=DataFormat.CSV,
        )
        client = QueuedIngestClient(kcsb)
        client.ingest_from_dataframe(df, ingestion_properties=ingestion_props)

    def delete_participant(self, table_name, individual):
        self.execute_query(
            f".delete table {table_name} records <| {table_name} | where ['individual'] == '{individual}'")

    def __del__(self):
        self._disconnect()
