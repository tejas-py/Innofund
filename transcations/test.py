
import re

txnID = ""

if re.search("[0-9]+[A-Z]", txnID):
    print("Transaction was successful. Transaction ID: {}".format(txnID))
else:
    print("Transaction was not successful.")
