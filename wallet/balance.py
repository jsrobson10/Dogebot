
import os
import glob

from discord import Embed

from wallet.log import *
from wallet.account import *
from wallet.wallet import *
from wallet.user import *

users = []
total = 0
free = 0
txid_latest = ""

async def BalanceInit():

    global txid_latest
    global total
    global free

    total = 0
    free = 0
    
    for uid in AccountList():

        account = AccountRead(uid)
        users.append(account)

        total += account.getBalance()

    free = await WalletGetBalance() - total

    try:
        with open("db/txid_latest", "r") as f:
            txid_latest = f.read().replace("\n", "").replace("\r", "")
    except:
        pass

    print("{0} has a total of {1} DOGE allocated and {2} DOGE free".format(glob.name, total, free))

def BalanceGetID(uid: int):

    for i in range(len(users)):
        
        user = users[i]

        if user.getUid() == uid:
            return i
    
    user = Account()
    user.setUid(uid)
    users.append(user)

    return len(users) - 1

def BalanceGet(uid: int):
   
    i = BalanceGetID(uid)

    return users[i].getBalance()

def BalanceGetAll():

    return users

def BalanceRemove(uid: int, amount: int):

    i = BalanceGetID(uid)
    users[i].setBalance(users[i].getBalance() - amount)
    AccountWrite(users[i])

def BalanceTransfer(uid_from: int, uid_to: int, amount: int):
    
    # get both account ids
    id_from = BalanceGetID(uid_from)
    id_to = BalanceGetID(uid_to)

    # get both account balances
    b_from = users[id_from].getBalance()
    b_to = users[id_to].getBalance()

    # transfer failed because not enough balance
    if b_from < amount:
        return False

    if uid_to == glob.bot_id or uid_to == "":

        # this is a donation
        users[id_from].setBalance(b_from - amount)
        AccountWrite(users[id_from])

        print("Recieved a donation of {0} DOGE from user with uid {1}".format(amount, uid_from))

        return True

    # transfer between the 2 accounts
    users[id_from].setBalance(b_from - amount)
    users[id_to].setBalance(b_to + amount)

    # update the 2 accounts
    AccountWrite(users[id_from])
    AccountWrite(users[id_to])

    return True

def BalanceCalculateAmount(amount,dorng=True):

    if(dorng):
        
        if amount == "roll":
            return glob.random.randrange(1, 6)
        if amount == "megaroll":
            return glob.random.randrange(6, 36)
        if amount == "gigaroll":
            return glob.random.randrange(36, 216)
    
    if amount == "all":
        return -1
    
    try:
        a = float(amount)
        if a > 0:
            return a
        else:
            return None
    except:
        return None

async def BalanceGetAddress(uid: int):

    changed = False

    id = BalanceGetID(uid)
    user = users[id]

    if user.getAddress() is None:
        changed = True
        user.setAddress(await WalletGenerateAddress())

        if user.getAddress() is None:
            return None

    address = user.getAddress()
    AccountWrite(user)

    return address

async def BalanceUpdate(client):

    global txid_latest
    global total

    page = 0
    pagesize = 64
    running = True

    transactions = await WalletGetTransactions(pagesize, page * pagesize)
    txid_new = ""

    # traverse in order most recent to least recent
    while True:

        running = len(transactions) > 0

        for transaction in reversed(transactions):

            t_address = transaction['address']
            t_amount = transaction['amount']
            t_txid = transaction['txid']

            # stop when the traversal gets to the last transaction
            if t_txid == txid_latest:
                running = False;
                break;

            # skip the newest transactions if they dont have enough confirmations
            if transaction['confirmations'] < glob.mintransactions:
                continue
            
            # set the newest trustworthy transaction
            if txid_new == "":
                txid_new = t_txid

            # skip all transactions that aren't recieving money, we don't care about this
            if transaction['category'] != "receive":
                continue

            total += t_amount

            print("Found block with txid {0} with value {1} DOGE and address {2}".format(t_txid, t_amount, t_address))
            
            # add the transaction amount to the right user account
            for user in users:
                
                if user.getAddress() is not None and user.getAddress() == t_address:
                    
                    # add the balance and update
                    Log("deposit", t_amount, address=t_address, uid_to=user.getUid())
                    user.setBalance(user.getBalance() + t_amount)
                    AccountWrite(user)

                    # message the user about the new balance, if possible
                    try:
                    
                        d_user = await client.fetch_user(user.getUid())
                        
                        await d_user.send(embed=Embed(title="New deposit", description="A deposit of {0} DOGE has been added to your account. You can view this transaction [here](https://dogechain.info/tx/{1}).".format(t_amount, t_txid)))

                    except:
                        print("Failed to message user transaction")

                    break

        
        if not running:
            break

        page += 1
        transactions = await WalletGetTransactions(pagesize, page * pagesize)
   
    # only update the latest transaction if its been changed
    if txid_new != "":
        txid_latest = txid_new
    
        with open("db/txid_latest", "w") as f:
            f.write(txid_latest)

