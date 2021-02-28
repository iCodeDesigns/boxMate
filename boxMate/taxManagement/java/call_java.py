import os
import subprocess

def java_func(json_str, client_name, client_id):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print("#######################################################################")
    print(BASE_DIR)
    file_dir = os.path.join(BASE_DIR,'EtaInvoiceSubmission_Model_adflib.jar')
    call_jar_file = subprocess.Popen(['java', '-jar', file_dir], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = call_jar_file.communicate(input=[json_str, client_name, client_id])
    return stdout
