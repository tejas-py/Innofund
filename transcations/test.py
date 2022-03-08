myprogram = "escrow_account/sample.teal"

data = load_resource(myprogram)
source = data.decode('utf-8')

response = algod_client.compile(source)
# Print(response)
print("Response Result = ", response['result'])
print("Response Hash = ", response['hash'])
# Create logic sig
programstr = response['result']
t = programstr.encode("ascii")