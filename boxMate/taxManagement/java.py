import os
import subprocess

def java_func():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_dir = os.path.join(BASE_DIR, "taxManagement")
    call_jar_file = subprocess.call(['java', '-jar', file_dir+'\\adflib.jar', 'SignatureInvoice','getFullSignedDocument', "Dreem", "08268939" ])
    return call_jar_file
