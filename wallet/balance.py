
import os
import glob

from wallet.log import *
from wallet.account import *
from wallet.wallet import *
from wallet.user import *

users = {}
total = 0
free = 0
blockhash_latest = ""

async def BalanceInit():

    global blockhash_latest
    global total
    global free

    total = 0
    free = 0
    
    for uid in AccountList():

        account = AccountRead(uid)
        users[int(uid)] = account
        total += account['balance']

    free = await WalletGetBalance() - total

    try:
        with open("db/blockhash_latest", "r") as f:
            blockhash_latest = f.read().replace("\n", "").replace("\r", "")
    except:
        pass

    print("{0} has a total of {1} DOGE allocated and {2} DOGE free".format(glob.name, total, free))

def BalanceGet(uid: int):
    
    if not uid in users:
        users[uid] = {
            "balance": 0,
        }

    return users[uid]['balance']

def BalanceTransfer(uid_from: int, uid_to: int, amount: int):
    
    # get both account balances
    b_from = BalanceGet(uid_from)
    b_to = BalanceGet(uid_to)

    # transfer failed because not enough balance
    if b_from < amount:
        return False

    if uid_to == glob.bot_id or uid_to == "":

        # this is a donation
        users[uid_from]['balance'] -= amount
        AccountWrite(uid_from, users[uid_from])

        print("Recieved a donation of {0} DOGE from user with uid {1}".format(amount, uid_from))

        return True

    # transfer between the 2 accounts
    users[uid_from]['balance'] -= amount
    users[uid_to]['balance'] += amount

    # update the 2 accounts
    AccountWrite(uid_from, users[uid_from])
    AccountWrite(uid_to, users[uid_to])

    return True

def BalanceCalculateAmount(amount):

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

    if not uid in users:
        changed = True
        users[uid] = {
            "balance": 0,
        }

    user = users[uid]

    if not "address" in user:
        changed = True
        user["address"] = await WalletGenerateAddress()
        user["recieved"] = 0

        if user["address"] is None:
            return None

    address = user["address"]

    AccountWrite(uid, user)

    return address

async def BalanceUpdate(client):

    global blockhash_latest
    global total

    page = 0
    pagesize = 64
    running = True

    transactions = await WalletGetTransactions(pagesize, page * pagesize)
    blockhash_new = ""

    # traverse in order most recent to least recent
    while True:

        print("Searching for blockhashes... Page", page)

        running = len(transactions) > 0

        for transaction in reversed(transactions):
           
            # stop when the traversal gets to the last blockhash
            if transaction['blockhash'] == blockhash_latest:
                running = False;
                break;

            # skip the newest transactions if they dont have enough confirmations
            if transaction['confirmations'] < glob.mintransactions:
                continue
            
            # set the newest trustworthy blockhash
            if blockhash_new == "":
                blockhash_new = transaction['blockhash']

            # skip all transactions that aren't recieving money, we don't care about this
            if transaction['category'] != "receive":
                continue

            t_amount = transaction['amount']
            total += t_amount

            print("Found blockhash {0} with value {1} DOGE, transaction ID {2}, and address {3}".format(transaction['blockhash'], transaction['amount'], transaction['txid'], transaction['address']))
            
            # add the transaction amount to the right user account
            t_address = transaction['address']

            for uid in users:
                
                user = users[uid]

                if 'address' in user and user['address'] == t_address:
                    
                    # add the balance and update
                    Log("deposit", t_amount, address=t_address, uid_to=uid)
                    user.balance += t_amount
                    AccountWrite(uid, user)

                    # message the user about the new balance, if possible
                    try:
                    
                        d_user = await client.fetch_user(uid)

                        # do this so we can still message the user even if we don't have any mutual servers
                        if not d_user.is_friend():
                            await d_user.send_friend_request()
                        
                        await d_user.send(embed=Embed(title="New deposit", description="A deposit of {0} DOGE has been added to your account. The transaction ID of this deposit is {1}.".format(t_amount, transaction['txid'])))

                    except:
                        print("Failed to message user transaction")

                    break

        
        if not running:
            break

        page += 1
        transactions = await WalletGetTransactions(pagesize, page * pagesize)
   
    # only update the latest blockhash if its been changed
    if blockhash_new != "":
        blockhash_latest = blockhash_new
    
        with open("db/blockhash_latest", "w") as f:
            f.write(blockhash_latest)

