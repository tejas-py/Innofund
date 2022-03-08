from billiard.five import string
from algosdk.future import transaction
import utilities.CommonFunctions as com_func
from algosdk import account
from API.connection import algo_conn

client = algo_conn()

account_info = client.application_info(76552592)
params_info = account_info['params']
print(params_info['creator'])
