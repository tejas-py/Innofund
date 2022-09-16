from algosdk import encoding
from pyteal import *


# convert pyteal to teal
def to_teal(client, smart_contract):

    # First convert the PyTeal to TEAL
    approval_teal_campaign = compileTeal(smart_contract, Mode.Application, version=6)

    # Next compile our TEAL to bytecode. (it's returned in base64)
    approval_b64_campaign = client.compile(approval_teal_campaign)['result']

    # Lastly decode the base64.
    approval_prog_campaign = encoding.base64.b64decode(approval_b64_campaign)

    return approval_prog_campaign
