
import os
import json

class Account:

    _balance: float = 0
    _address: str = None
    _uid: int = 0

    def __init__(self, data:str=None):
        
        if data is None:
            return

        data_s = json.loads(data)
        
        if 'balance' in data_s:
            d = data_s['balance']
            t = type(d)
            if t is int or t is float:
                self._balance = float(d)
        
        if 'address' in data_s:
            d = data_s['address']
            t = type(d)
            if t is str:
                self._address = d

        if 'uid' in data_s:
            d = data_s['uid']
            t = type(d)
            if t is int:
                self._id = d

    def setBalance(self, balance: float):
        self._balance = float(balance)

    def setAddress(self, address: str):
        self._address = str(address)

    def setUid(self, uid: int):
        self._uid = int(uid)

    def getBalance(self):
        return self._balance

    def getAddress(self):
        return self._address

    def getUid(self):
        return self._uid

    def __repr__(self):
        return "Account(balance={0}, address={1}, uid={2})".format(self._balance, self._address, self._uid, type(self._uid))

    def serialize(self):
        return json.dumps({'balance': self._balance, 'address': self._address, 'uid': self._uid})

def AccountList():

    if not os.path.exists("db/accounts"):
        os.makedirs("db/accounts")
    
    return os.listdir("db/accounts")

def AccountRead(uid: int):

    a = None

    try:
        with open("db/accounts/{0}".format(uid), "r") as f:
            a = Account(f.read())
    except:
        a = Account()

    a.setUid(uid)
    return a

def AccountWrite(account: Account):

    try:
        with open("db/accounts/{0}".format(account.getUid()), "w") as f:
            f.write(account.serialize())
    except:
        if not os.path.exists("db/accounts"):
            os.makedirs("db/accounts")
            AccountWrite(account)
        else:
            raise
