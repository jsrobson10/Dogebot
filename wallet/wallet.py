
import glob
import requests
import json

async def WalletSendCommand(command: str, *params, silent=False):

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
    if res.status_code != 200 and not silent:

        print("Error: rpc command failed with status code {0}".format(res.status_code))

    return res.json()

async def WalletGetBalance():
    
    res = await WalletSendCommand("getbalance")

    if 'result' in res:
        
        t = type(res['result'])

        if t is float or t is int:

            return res['result']

    return 0

async def WalletGenerateAddress():

    res = await WalletSendCommand("getnewaddress")

    if 'result' in res and type(res['result']) is str:
        return res['result']

    return None

async def WalletGetTransactions(count: int, skip: int):

    res = await WalletSendCommand("listtransactions", "", count, skip)

    if 'result' in res and res['result'] is not None:

       return res['result']

    return []

async def WalletSend(address: str, amount: int):
    
    # not an empty password
    if glob.walletpassword != "":
        await WalletSendCommand("walletpassphrase", glob.walletpassword, 60)
   
    # send the dogecoin
    return await WalletSendCommand("sendtoaddress", address, amount, "", "", True, silent=True)

