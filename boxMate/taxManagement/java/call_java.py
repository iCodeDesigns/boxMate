import os
import subprocess
import json
from demjson import decode
import simplejson
from ast import literal_eval

def java_func(json_code, client_name, client_id):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_dir = os.path.join(BASE_DIR,'EtaInvoiceSubmission_Model_adflib.jar')
    call_jar_file = subprocess.Popen(['java', '-jar', file_dir, json_code, client_name, client_id], stdout=subprocess.PIPE)
    stdout, stderr = call_jar_file.communicate()
    #print(stdout)
    #data = stdout.decode('utf8')
    #print(data)
    #json_data = simplejson.loads(stdout)
    #print(json_data)
    #st1 = simplejson.dumps(json_data)
    #signature = json_data["documents"][0]["signatures"]

    #print(json_data)
    #print(signature)
    return stdout
