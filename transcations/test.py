# ignore test.py file, this for the test


while True:
    is_valid = False
    if len(username) < 6 or len(username) > 12:
        print("Not valid ! Username total characters should be between 6 and 12")
        break
    elif not re.search("[A-Z]", username):
        print("Not valid ! Username should contain one letter between [A-Z]")
        break
    elif not re.search("[a-z]", username):
        print("Not valid ! Username should contain one letter between [a-z]")
        break
    elif not re.search("[1-9]", username):
        print("Not valid ! Username should contain one letter between [1-9]")
        break
    elif re.search("[\s]", username):
        print("Not valid ! Username should not contain any space")
        break
    else:
        is_valid = True
        break
if is_valid:
    print("Username is valid !")