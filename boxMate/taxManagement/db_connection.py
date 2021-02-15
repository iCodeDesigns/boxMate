import json

import cx_Oracle


class OracleConnection:

    def __init__(self, address, port, service_nm, username, password):
        self.address = address
        self.port = port
        self.service_nm = service_nm
        self.username = username
        self.password = password


    def get_data_from_db(self):
        dsn_tns = cx_Oracle.makedsn(self.address, self.port, service_name=self.service_nm)
        conn = cx_Oracle.connect(user=self.username, password=self.password, dsn=dsn_tns)

        cursor = conn.cursor()
        cursor.execute(" select * from apps.xxeta_invoices")
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        data = cursor.fetchall()
        return data
