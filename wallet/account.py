
import os
import json

def AccountList():

    if not os.path.exists("db/accounts"):
        os.makedirs("db/accounts")
    
    return os.listdir("db/accounts")

def AccountRead(uid: int):

    try:
        with open("db/accounts/{0}".format(uid), "r") as f:
            return json.load(f)
    except:
        return {
            "balance": 0,
        }

def AccountWrite(uid: int, account):

    try:
        with open("db/accounts/{0}".format(uid), "w") as f:
            f.write(json.dumps(account))
    except:
        if not os.path.exists("db/accounts"):
            os.makedirs("db/accounts")
            AccountWrite(uid, account)
