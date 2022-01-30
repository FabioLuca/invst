import mysql.connector
from mysql.connector.constants import ClientFlag
from pathlib import Path
import pandas as pd
from typing import List, Union


class GoogleCloudMySQL:

    def create_connection_string(self):
        self.config_db = {
            'user': self.config.get_key(
                "user", ["storage",
                         "GoogleCloudMySQL",
                         "user_data",
                         "User"], ""),
            'password': self.config.get_key(
                "user", ["storage",
                         "GoogleCloudMySQL",
                         "user_data",
                         "Password"], ""),
            'host': self.config.get_key(
                "user", ["storage",
                         "GoogleCloudMySQL",
                         "user_data",
                         "Host"], ""),
            'client_flags': [ClientFlag.SSL],
            'ssl_ca': self.config.get_key(
                "user", ["storage",
                         "GoogleCloudMySQL",
                         "user_data",
                         "SSL_CA"], ""),
            'ssl_cert': self.config.get_key(
                "user", ["storage",
                         "GoogleCloudMySQL",
                         "user_data",
                         "SSL_Cert"], ""),
            'ssl_key': self.config.get_key(
                "user", ["storage",
                         "GoogleCloudMySQL",
                         "user_data",
                         "SSL_Key"], ""),
        }

    def create_connection(self, database_name: str = None):

        self.create_connection_string()

        if database_name is not None:
            self.config_db['database'] = database_name

        self.cnxn = mysql.connector.connect(**self.config_db)
        cursor = self.cnxn.cursor()

        return cursor

    def close_connection(self):

        self.cnxn.close()
        self.cnxn = None

    def check_db_exists(self, database_name: str):

        cursor = self.create_connection()

        cursor.execute("SHOW DATABASES")

        result = False
        for db in cursor:
            if db[0] == database_name:
                result = True
                break

        self.close_connection()

        return result

    def check_table_exists(self, database_name: str, table_name: str):

        sql_query = """
            SHOW TABLES;
            """
        cursor = self.execute_query(database_name=database_name,
                                    query=sql_query,
                                    type_query="SELECT")

        result = False
        for table in cursor:
            if table[0] == table_name:
                result = True

        return result

    def execute_query(self, database_name: str, query: List[str], type_query: List[str]):

        self.logger.info("Multiple querries call")

        results = []

        for query_item, type_query_item in zip(query, type_query):
            result = self.execute_query(database_name=database_name,
                                        query=query_item,
                                        type_query=type_query_item)
            results.append(result)

        return results

    def execute_query(self, database_name: str, query: str, type_query: str, parameter=None):

        result = None

        if self.cnxn is not None:
            self.logger.info("Connection already open!")
            return None
        cursor = self.create_connection(database_name=database_name)

        if parameter is None:
            cursor.execute(query)
        else:
            if isinstance(parameter, list):
                cursor.executemany(query, parameter)
            else:
                cursor.execute(query, parameter)

        if type_query == "NONE" or type_query == "" or type_query is None:
            result = cursor
        elif type_query in ["SELECT"]:
            result = cursor.fetchall()
        elif type_query in ["INSERT", "UPDATE", "ALTER"]:
            self.cnxn.commit()
            result = cursor

        self.close_connection()

        return result

    def create_db(self, database_name: str):

        self.logger.info(f"Creating the database '{database_name}'")

        # ----------------------------------------------------------------------
        #   Verifies if the database to be created already exists, and if so,
        #   skips the creation process.
        # ----------------------------------------------------------------------
        db_exists = self.check_db_exists(database_name=database_name)

        if db_exists:
            self.logger.info(f"Database '{database_name}' already present")
            return False

        cursor = self.create_connection()
        cursor.execute(f"CREATE DATABASE {database_name}")
        self.close_connection()

        return True

    def create_table_from_pandas(self, database_name: str, table_name: str, dataframe: pd.DataFrame):

        self.logger.info(f"Creating the table '{table_name}' from Dataframe")

        # ----------------------------------------------------------------------
        #   Verifies if the database to be created already exists, and if so,
        #   skips the creation process.
        # ----------------------------------------------------------------------
        table_exists = self.check_table_exists(
            database_name=database_name, table_name=table_name)

        if table_exists:
            self.logger.info(f"Table '{table_name}' already present")
            return False

        sql_query = pd.io.sql.get_schema(
            dataframe.reset_index(), table_name)

        sql_query = sql_query.replace('"', '`')

        self.execute_query(database_name=database_name,
                           query=sql_query, type_query="INSERT")

        # ----------------------------------------------------------------------
        #   Corrects the datatypes so some text fields can be used later in
        #   Unique Keys
        # ----------------------------------------------------------------------
        if "`Position ID`" in sql_query:
            sql_query_alter = f"""
                ALTER TABLE `{table_name}`
                MODIFY `Position ID` VARCHAR(200)"""
            self.execute_query(database_name=database_name,
                               query=sql_query_alter, type_query="ALTER")

        if "`Depot ID`" in sql_query:
            sql_query_alter = f"""
                ALTER TABLE `{table_name}`
                MODIFY `Depot ID` VARCHAR(200)"""
            self.execute_query(database_name=database_name,
                               query=sql_query_alter, type_query="ALTER")

        # ----------------------------------------------------------------------
        #   Adds an Unique Key for the table
        # ----------------------------------------------------------------------
        if "`Position ID`" in sql_query or "`Depot ID`" in sql_query:
            if "`Position ID`" in sql_query and "`Date`" in sql_query:
                self.logger.info(
                    f"Adding constraint to table '{table_name}' for `Position ID`")
                sql_query_alter = f"""
                    ALTER TABLE `{table_name}`
                    ADD CONSTRAINT unique_per_day
                    UNIQUE (`Date`, `Position ID`);
                    """
            elif "`Depot ID`" in sql_query_alter and "`Date`" in sql_query:
                self.logger.info(
                    f"Adding constraint to table '{table_name}' for `Depot ID`")
                sql_query_alter = f"""
                    ALTER TABLE `{table_name}`
                    ADD CONSTRAINT unique_per_day 
                    UNIQUE (`Date`, `Depot ID`);
                    """

            self.execute_query(database_name=database_name,
                               query=sql_query_alter, type_query="ALTER")

        return True

    def save_pandas_as_db(self, database_name: str, table_name: Union[str, List[str]], dataframe: Union[pd.DataFrame, List[pd.DataFrame]]):

        if isinstance(table_name, str) and isinstance(dataframe, pd.DataFrame):
            table_name = [table_name]
            dataframe = [dataframe]

        for table_name_item, dataframe_item in zip(table_name, dataframe):
            self.save_pandas_as_db_item(database_name=database_name,
                                        table_name=table_name_item,
                                        dataframe=dataframe_item)

    def save_pandas_as_db_item(self, database_name: str, table_name: str, dataframe: pd.DataFrame):

        # ----------------------------------------------------------------------
        # Prepare the Pandas dataframe for storage.
        # ----------------------------------------------------------------------
        dataframe_storage = dataframe.copy()

        dataframe_storage["Date"] = pd.to_datetime(
            dataframe_storage["Date"], format="%Y-%m-%d", infer_datetime_format=True)
        dataframe_storage["Date"] = dataframe_storage["Date"].dt.date

        dataframe_storage['Date'] = pd.to_datetime(
            dataframe_storage['Date'], infer_datetime_format=True)

        if "Unnamed: 0" in dataframe_storage.columns:
            dataframe_storage.drop(columns=["Unnamed: 0"], inplace=True)
        dataframe_storage.index = pd.RangeIndex(len(dataframe_storage.index))
        dataframe_storage.reset_index(inplace=True, drop=True)
        if "WKN" in dataframe_storage.columns:
            dataframe_storage.sort_values(
                by=["WKN", "Date"], ignore_index=True, inplace=True)
        else:
            dataframe_storage.sort_values(
                by=["Date"], ignore_index=True, inplace=True)

        # ----------------------------------------------------------------------
        #   Tries to create the database and the table for the dataframe. In
        #   case they are already existing, this is checked inside the creation
        #   methods and nothing is done, so the insertion of new data proceeds.
        # ----------------------------------------------------------------------
        self.create_db(database_name=database_name)

        self.create_table_from_pandas(dataframe=dataframe_storage,
                                      database_name=database_name,
                                      table_name=table_name)

        self.logger.info(f"Adding data to {table_name}")

        pandas_columns_list = [
            '`' + x + '`' for x in dataframe_storage.columns]
        pandas_columns_list = ", ".join(pandas_columns_list)

        pandas_values_list = ['%s'] * len(dataframe_storage.columns)
        pandas_values_list = ', '.join(pandas_values_list)

        updates = []
        for item in dataframe_storage.columns:
            #updates.append(f"`{item}` = newval.`{item}`")
            updates.append(f"`{item}` = VALUES(`{item}`)")

        update_string = ", ".join(updates)

        values = dataframe_storage.to_numpy().tolist()

        sql_query = f"""
            INSERT INTO `{table_name}` ({pandas_columns_list})
            VALUES ({pandas_values_list}) 
            ON DUPLICATE KEY UPDATE
                {update_string}
            """

        self.execute_query(database_name=database_name,
                           query=sql_query,
                           type_query="INSERT",
                           parameter=values)
