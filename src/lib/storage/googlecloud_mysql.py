import mysql.connector
from mysql.connector.constants import ClientFlag
from pathlib import Path
import pandas as pd
from typing import List, Union
from googleapiclient import discovery
import google.auth
from src.lib import messages as M
from src.lib import constants as C
import numpy as np


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
        #   Add a primary key
        # ----------------------------------------------------------------------
        sql_query_index = f"""
            ALTER TABLE `{table_name}` 
            CHANGE COLUMN `index` `index` INT(11) NOT NULL AUTO_INCREMENT ,
            ADD UNIQUE INDEX `index_UNIQUE` (`index` ASC),
            ADD PRIMARY KEY (`index`);
            ;
            """
        self.execute_query(database_name=database_name,
                           query=sql_query_index, type_query="ALTER")

        # ----------------------------------------------------------------------
        #   Corrects the datatypes so some text fields can be used later in
        #   Unique Keys
        # ----------------------------------------------------------------------
        fields = {
            "WKN": "VARCHAR(200)",
            "Position ID": "VARCHAR(200)",
            "Depot ID": "VARCHAR(200)",
            "Depot Aggregated ID": "VARCHAR(200)",
            "Order ID": "VARCHAR(200)",
            "Venue ID": "VARCHAR(200)",
            "Client ID": "VARCHAR(200)",
            "Account ID": "VARCHAR(200)",
            "Instrument ID": "VARCHAR(200)",
            "Account Display ID": "VARCHAR(200)",
            "Settlement account ID": "VARCHAR(200)",
            "Balance Unit": "VARCHAR(10)",
            "Balance Euro Unit": "VARCHAR(10)",
            "Available Cash Unit": "VARCHAR(10)",
            "Available Cash Euro Unit": "VARCHAR(10)",
            "Purchase Value Unit": "VARCHAR(10)",
            "Purchase Price Unit": "VARCHAR(10)",
            "Current Value Unit": "VARCHAR(10)",
            "Current Price Unit": "VARCHAR(10)",
            "Limit Unit": "VARCHAR(10)",
            "Hedgeability": "VARCHAR(30)",
            "Profit/Loss Purchase Absolute Unit": "VARCHAR(10)",
            "Profit/Loss Previous Day Absolute Unit": "VARCHAR(10)",
            "Account Currency": "VARCHAR(10)",
            "IBAN": "VARCHAR(200)",
            "Quantity": "INT(10)",
            "Available Cash Value": "DECIMAL(12, 2)",
            "Available Cash Euro Value": "DECIMAL(12, 2)",
            "Balance Value": "DECIMAL(12, 2)",
            "Balance Euro Value": "DECIMAL(12, 2)",
            "Depot Aggregated Purchase Value": "DECIMAL(12, 2)",
            "Depot Aggregated Current Value": "DECIMAL(12, 3)",
            "Depot Aggregated Profit/Loss Purchase Absolute Value": "DECIMAL(12, 3)",
            "Depot Aggregated Profit/Loss Purchase Relative": "DECIMAL(12, 3)",
            "Depot Aggregated Profit/Loss Previous Day Absolute Value": "DECIMAL(12, 3)",
            "Depot Aggregated Profit/Loss Previous Day Relative": "DECIMAL(12, 3)",
            "Purchase Value": "DECIMAL(12, 3)",
            "Purchase Price": "DECIMAL(12, 5)",
            "Current Value": "DECIMAL(12, 3)",
            "Current Price": "DECIMAL(12, 3)",
            "Profit/Loss Purchase Absolute Value": "DECIMAL(12, 3)",
            "Profit/Loss Purchase Relative": "DECIMAL(12, 3)",
            "Profit/Loss Previous Day Absolute Value": "DECIMAL(12, 3)",
            "Profit/Loss Previous Day Relative": "DECIMAL(12, 3)",
        }
        for field, type_field in fields.items():
            if f"`{field}`" in sql_query:
                sql_query_alter = f"""
                    ALTER TABLE `{table_name}`
                    MODIFY `{field}` {type_field}"""
                self.execute_query(database_name=database_name,
                                   query=sql_query_alter, type_query="ALTER")

        # ----------------------------------------------------------------------
        #   Adds an Unique Key for the table
        # ----------------------------------------------------------------------
        keys = ["Position ID",
                "Depot ID",
                "Depot Aggregated ID",
                "Account ID"
                ]

        if any(k in sql_query for k in keys):
            for key in keys:
                if key in sql_query and "`Date`" in sql_query:
                    self.logger.info(
                        f"Adding constraint to table '{table_name}' for '{key}'")
                    sql_query_alter = f"""
                        ALTER TABLE `{table_name}`
                        ADD CONSTRAINT unique_per_day
                        UNIQUE (`Date`,`{key}`);
                        """
                    self.execute_query(database_name=database_name,
                                       query=sql_query_alter, type_query="ALTER")
                    break

        return True

    def load_pandas_from_db(self, database_name: str, table_name: Union[str, List[str]]):

        if isinstance(table_name, str):
            table_name = [table_name]

        dataframes = []
        flag_final, level_final, message_final = M.get_status(
            self.logger_name, "Storage_LoadSuccess_Database")

        for table_name_item in table_name:
            dataframe, flag, level, message = self.load_pandas_from_db_item(database_name=database_name,
                                                                            table_name=table_name_item)
            dataframes.append(dataframe)
            if flag != C.SUCCESS:
                flag_final, level_final, message_final = M.get_status(
                    self.logger_name, "Storage_LoadError_Database")

        return dataframes, flag_final, level_final, message_final

    def load_pandas_from_db_item(self, database_name: str, table_name: Union[str, List[str]]):

        self.logger.info(
            f"Loading data from table '{table_name}' into Dataframe")

        # ----------------------------------------------------------------------
        #   Gets the data from database, along with the columns structure, since
        #   they are the same from the DataFrame, and convert the results in the
        #   Dataframe.
        # ----------------------------------------------------------------------
        sql_query = f"""
            DESCRIBE `{table_name}`;
        """

        result_columns = self.execute_query(database_name=database_name,
                                            query=sql_query,
                                            type_query="SELECT")

        columns = []
        for item in result_columns:
            columns.append(item[0])

        sort_list = []
        if "WKN" in columns:
            sort_list.append("`WKN` DESC")
        if "Date" in columns:
            sort_list.append("`Date` DESC")

        if sort_list:
            sort_list_string = ", ".join(sort_list)
            sort_string = f"ORDER BY {sort_list_string}"
        else:
            sort_string = ""

        sql_query = f"""
            SELECT * FROM `{table_name}`
            {sort_string};
            """

        result = self.execute_query(database_name=database_name,
                                    query=sql_query,
                                    type_query="SELECT")

        df = pd.DataFrame.from_records(result, columns=columns)

        # ----------------------------------------------------------------------
        #   Executes routine on the DataFrame to adequate the format and
        #   content.
        # ----------------------------------------------------------------------
        if "index" in df.columns:
            df.set_index('index', inplace=True)

        flag, level, message = M.get_status(
            self.logger_name, "Storage_LoadSuccess_Database")

        return df, flag, level, message

    def save_pandas_as_db(self, database_name: str, table_name: Union[str, List[str]], dataframe: Union[pd.DataFrame, List[pd.DataFrame]]):

        if isinstance(table_name, str) and isinstance(dataframe, pd.DataFrame):
            table_name = [table_name]
            dataframe = [dataframe]

        for table_name_item, dataframe_item in zip(table_name, dataframe):
            self.save_pandas_as_db_item(database_name=database_name,
                                        table_name=table_name_item,
                                        dataframe=dataframe_item)

    def save_pandas_as_db_item(self, database_name: str, table_name: str, dataframe: pd.DataFrame):

        self.logger.info(
            f"Storing data from Dataframe to table '{table_name}'")

        # ----------------------------------------------------------------------
        # Prepare the Pandas dataframe for storage.
        # ----------------------------------------------------------------------
        dataframe_storage = dataframe.copy()

        if "Date" in dataframe_storage.columns:
            # dataframe_storage["Date"] = pd.to_datetime(
            #     dataframe_storage["Date"], format="%Y-%m-%d", infer_datetime_format=True)
            # dataframe_storage["Date"] = dataframe_storage["Date"].dt.date

            dataframe_storage['Date'] = pd.to_datetime(
                dataframe_storage['Date'], infer_datetime_format=True)

        if "Unnamed: 0" in dataframe_storage.columns:
            dataframe_storage.drop(columns=["Unnamed: 0"], inplace=True)
        dataframe_storage.index = pd.RangeIndex(len(dataframe_storage.index))
        dataframe_storage.reset_index(inplace=True, drop=True)
        if "WKN" in dataframe_storage.columns and "Date" in dataframe_storage.columns:
            dataframe_storage.sort_values(
                by=["WKN", "Date"], ignore_index=True, inplace=True)
        elif "Date" in dataframe_storage.columns:
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

        dataframe_storage_clear = dataframe_storage.replace(np.NaN, pd.NA).where(
            dataframe_storage.notnull(), None)
        values = dataframe_storage_clear.to_numpy().tolist()

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
