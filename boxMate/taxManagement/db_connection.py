import json

import cx_Oracle


class OracleConnection:

    def __init__(self, address, port, service_nm, username, password):
        self.address = address
        self.port = port
        self.service_nm = service_nm
        self.username = username
        self.password = password

    def init_db_connection(self):
        dsn_tns = cx_Oracle.makedsn(self.address, self.port, service_name=self.service_nm)
        try:
            conn = cx_Oracle.connect(user=self.username, password=self.password, dsn=dsn_tns)
            return conn
        except Exception as e:
            return e

    def get_data_from_db(self, query):
        conn = self.init_db_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                cursor.rowfactory = lambda *args: dict(zip(columns, args))
                data = cursor.fetchall()
                return data
            except Exception as e:
                return e
        else:
            return conn

# x = OracleConnection(
#     '127.0.0.1', '1521', 'orcl0', 'hr', 'hr')
# print(x.get_data_from_db())
