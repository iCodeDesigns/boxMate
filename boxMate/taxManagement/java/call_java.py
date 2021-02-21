# from py4j.java_gateway import JavaGateway
import os
import subprocess

# gateway = JavaGateway()
#
# stack = gateway.entry_point.getStack()

def func_call_jar():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    jar = os.path.join(BASE_DIR, "taxManagement",'final_adflib.jar' )
    xxx = subprocess.call(['java', '-jar', jar])
    print(xxx)
    return xxx
