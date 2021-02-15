import json

import cx_Oracle

import cx_Oracle


# Connect as user "hr" with password "welcome" to the "orclpdb1" service running on this computer.
def get_data_from_db():
    dsn_tns = cx_Oracle.makedsn('156.4.58.40', '1521', service_name='prod')
    conn = cx_Oracle.connect(user=r'apps', password='applmgr_42', dsn=dsn_tns)

    cursor = conn.cursor()
    cursor.execute(" select * from apps.xxeta_invoices")
    columns = [col[0] for col in cursor.description]
    cursor.rowfactory = lambda *args: dict(zip(columns, args))
    data = cursor.fetchall()
    return data
