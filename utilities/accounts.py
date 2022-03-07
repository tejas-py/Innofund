
from utilities.CommonFunctions import get_private_key_from_mnemonic


def account():
    account1 = "couch unveil crush drastic staff peanut tooth code matrix drip jazz team ticket ring punch local patrol smile stay hobby maze swamp cash absent erupt"
    a1 = get_private_key_from_mnemonic(account1)
    return a1
