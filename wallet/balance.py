
import os
import glob

from discord import Embed

from wallet.log import *
from wallet.account import *
from wallet.wallet import *

users = []
balance = 0
total = 0
free = 0
txid_latest = ""

async def BalanceInit():

    global txid_latest
    global balance
    global total
    global free

    balance = 0
    total = 0
    free = 0
    
    for uid in AccountList():

        account = AccountRead(uid)
        users.append(account)

        total += account.getBalance()

    try:
        with open("db/balance", "r") as f:
            balance = float(f.read())
    except:
        pass

    free = balance - total

    try:
        with open("db/txid_latest", "r") as f:
            txid_latest = f.read().replace("\n", "").replace("\r", "")
    except:
        pass

    BalanceDisplay()

def BalanceDisplay():

    print("{0} has a total of {1} DOGE allocated and {2} DOGE free".format(glob.name, balance, free))

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

def BalanceShiftBalance(amount: float):
    
    global balance
    global free

    balance += amount
    free += amount

    try:
        with open("db/balance", "w") as f:
            f.write(str(balance))
    except:
        if not os.path.exists("db"):
            os.makedirs("db")
            BalanceShiftTotal(0)
        else:
            raise

def BalanceShiftTotal(amount: float):
    
    global total
    global free

    total += amount
    free -= amount

def BalanceTransfer(display, uid_from: int, uid_to: int, amount: int):
    
    if uid_to == glob.bot_id or uid_to == "":

        # this is a donation
        i = BalanceGetID(uid_from)
        users[i].setBalance(users[i].getBalance() - amount)
        AccountWrite(users[i])

        BalanceShiftTotal(-amount)
        BalanceShiftBalance(-amount)

        print("Recieved a donation of {0} DOGE from {1} with discord uid {2}".format(amount, display, uid_from))
        
        BalanceDisplay()

        return True

    # get both account ids
    id_from = BalanceGetID(uid_from)
    id_to = BalanceGetID(uid_to)

    # get both account balances
    b_from = users[id_from].getBalance()
    b_to = users[id_to].getBalance()

    # transfer failed because not enough balance
    if b_from < amount:
        return False

    # transfer between the 2 accounts
    users[id_from].setBalance(b_from - amount)
    users[id_to].setBalance(b_to + amount)

    # update the 2 accounts
    AccountWrite(users[id_from])
    AccountWrite(users[id_to])

    return True

def BalanceClaimDaily(duid: str):
    
    global free

    uid = BalanceGetID(duid)
    user = users[uid]

    if free <= 0:
        return (0, 0)

    left = user.claimDaily()

    if left <= 0:
        
        amount = free / glob.random.randrange(glob.dailyweightmin, glob.dailyweightmax)
        user.setBalance(user.getBalance() + amount)

        AccountWrite(user)
        BalanceShiftTotal(amount)
        BalanceDisplay()

        Log("reward", amount, uid_to=duid, fee=-amount)

        return (amount, left)
    
    return (0, left)

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

            # add the transaction amount to the right user account
            for user in users:
                
                if user.getAddress() is not None and user.getAddress() == t_address:
                    
                    print("Found block with txid {0} with value {1} DOGE and address {2}".format(t_txid, t_amount, t_address))
                    
                    # add the balance and update
                    Log("deposit", t_amount, address=t_address, uid_to=user.getUid())
                    
                    user.setBalance(user.getBalance() + t_amount)
                    AccountWrite(user)
                    
                    BalanceShiftTotal(t_amount)
                    BalanceShiftBalance(t_amount)
                    BalanceDisplay()

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

