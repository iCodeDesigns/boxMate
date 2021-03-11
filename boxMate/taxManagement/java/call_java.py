import os
import subprocess
import json
from demjson import decode
import simplejson
from ast import literal_eval

def java_func(json_code, client_name, client_id):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    tax_app_dir = os.path.join(BASE_DIR,"taxManagement")
    file_dir = os.path.join(tax_app_dir, 'java', 'EtaInvoiceSubmission_Model_adflib.jar')
    call_jar_file = subprocess.Popen(['java', '-jar', file_dir, json_code, client_name, client_id], stdout=subprocess.PIPE)
    stdout, stderr = call_jar_file.communicate()
    return stdout
