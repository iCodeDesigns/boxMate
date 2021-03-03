import os
import subprocess
import json
from demjson import decode

def java_func(json_code, client_name, client_id):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_dir = os.path.join(BASE_DIR,'EtaInvoiceSubmission_Model_adflib.jar')
    call_jar_file = subprocess.Popen(['java', '-jar', file_dir, json_code, client_name, client_id], stdout=subprocess.PIPE)
    stdout, stderr = call_jar_file.communicate()
    json_data = json.loads(stdout)
    st1 = json.dumps(json_data)
    return st1
