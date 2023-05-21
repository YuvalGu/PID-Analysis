import azure.kusto.data.helpers
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder, DataFormat
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table
import pandas as pd
import azure.kusto.data.helpers as helpers
from azure.kusto.ingest import QueuedIngestClient, IngestionProperties
import logging


class AzureDatabaseManager:
    def __init__(self, database):
        self.connection_string = "https://kvc3vyswugka1463f9f0e3.northeurope.kusto.windows.net/shiba"
        self.aad_app_id = "6aed01c7-b86c-461a-857c-6ed3f234ca67"
        self.app_key = "gSC8Q~bzSfOg8FWMd1y2582fCa-b1mnzWc_QXbD9"
        self.authority_id = "f04f3e7f-6fe8-4613-b5e3-791d54cc7573"
        self.database = database
        self.client = None
        self.tables = ['IGH_new', 'TRB', 'TRG']
        self._connect()

    def _connect(self):
        kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(
            self.connection_string, aad_app_id=self.aad_app_id, app_key=self.app_key, authority_id=self.authority_id)
        self.client = KustoClient(kcsb)

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
        """
qkl for dataframe: f".ingest inline into table {table_name} <|", dataframe=df
qkl for file path: .ingest inline into table TGB (h@"<file-path>")
Replace <file-path> with the actual path to your file. The h@ prefix is used to specify a file path in the
.ingest inline command.
Note that this approach is suitable for small file sizes. If you have larger files or need more advanced ingestion
options, you may want to consider using other methods, such as .ingest inline blob, .ingest inline csv, or utilizing
the Kusto Data Ingestion SDKs or connectors specific to your data source.
        """
        data_str = df.to_csv(index=False, header=False)
        self.execute_query(f".ingest inline into table {table_name} <| {data_str}")

    def delete(self, df, table_name):
        data_str = df.to_csv(index=False, header=False)
        self.execute_query(f".delete from table {table_name} where [individual] == 'C_test_IGH' ")
        # self.execute_query(f".delete {data_str} from table {table_name}")

    def __del__(self):
        self._disconnect()
