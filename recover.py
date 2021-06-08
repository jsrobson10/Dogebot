#!/usr/bin/env /usr/bin/python

from wallet.account import *

import sys
import csv

if len(sys.argv) != 2:
    print("Usage: {} <log>.csv".format(sys.argv[0]))
    exit(1)

f = open(sys.argv[1], 'r')

reader = csv.reader(f)
next(reader)

users = []

def GetUser(uid):

    uid = int(uid)

    for user in users:

        if user.getUid() == uid:

            return user

    user = Account()
    user.setUid(uid)
    users.append(user)

    return user

balance = 0

for utime, method, uid_from, uid_to, address, amount, fee in reader:

    amount = float(amount)

    if method == 'deposit':
        
        user = GetUser(uid_to)
        user.setBalance(user.getBalance() + amount)

        balance += amount

    elif method == 'withdraw':

        fee = float(fee)

        user = GetUser(uid_from)
        user.setBalance(user.getBalance() - amount - fee)

        balance -= amount + fee

    elif method == 'donate':

        user = GetUser(uid_from)
        user.setBalance(user.getBalance() - amount)

        balance -= amount

    elif method == 'give':

        user_from = GetUser(uid_from)
        user_to = GetUser(uid_to)

        user_from.setBalance(user_from.getBalance() - amount)
        user_to.setBalance(user_to.getBalance() + amount)

    elif method == 'reward':

        user = GetUser(uid_to)
        user.setBalance(user.getBalance() + amount)

        balance += amount

    else:

        print("Method not found:", method)

f.close()

if not os.path.exists("db"):
    os.makedirs("db")

try:
    os.rmdir("db/accounts")
except:
    pass

try:
    os.rmdir("db/address")
except:
    pass

try:
    os.unlink("db/txid_latest")
except:
    pass

try:
    os.unlink("db/balance")
except:
    pass

if os.path.normpath(sys.argv[1]) != os.path.normpath("db/log.csv"):
    try:
        os.unlink("db/log.csv")
    except:
        pass
    try:
        os.link(sys.argv[1], "db/log.csv")
    except:
        pass

with open("db/balance", "w") as f:
    f.write(str(balance))

for user in users:
    AccountWrite(user)

print("Recovered user data")
