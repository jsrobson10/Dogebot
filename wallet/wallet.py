
import glob
import requests
import json

async def WalletSendCommand(command: str, *params):

    data = json.dumps({
        "method": command,
        "params": params,
    })

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic {0}".format(glob.rpcauth),
    }

    res = requests.post(glob.rpcconnect, data=data, headers=headers)
    
    # handle any errors
    if res.status_code != 200:

        print("Error: rpc command failed with status code {0}".format(res.status_code))

    return res.json()

async def WalletGetBalance():
    
    res = await WalletSendCommand("getbalance", glob.account)

    if 'result' in res:
        
        t = type(res['result'])

        if t is float or t is int:

            return res['result']

    return 0

async def WalletGenerateAddress():

    res = await WalletSendCommand("getnewaddress", glob.account)

    if 'result' in res:

        t = type(res['result'])

        if t is str:

            return res['result']

    return None

async def WalletGetTransactions(count: int, skip: int):

    res = await WalletSendCommand("listtransactions", "1", count, skip)

    if 'result' in res:

       return res['result']

    else:
        
        return []

