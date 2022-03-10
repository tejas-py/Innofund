# ignore test.py file, this for the test




try:
    txnID = transcations.txn_escrow.transfer(passphrase, amount)
    if re.search("[0-9]+[A-Z]", txnID):
        return "Transaction of {} was successful. Transaction ID: {}".format(amount, txnID)
    else:
        return "Transaction was not successful."
except Exception:
    return "Transaction was not successful, please check your passphrase."
