
from wallet.balance import *

from discord import Embed
from command import Command

class CommandWithdraw(Command):

    def __init__(self):
        
        self.setName("withdraw")
        self.setDesc("Send some or 'all' of your dogecoin to an address. The fee for the dogecoin transfer will be at least {0} DOGE. The fee will be subtracted from the final amount.".format(1 + glob.fee))
        self.setUsage("address amount")

    async def run(self, message, command):
        
        if len(command) != 3:
            await self.help(message)
            return

        address = command[1]
        amount = BalanceCalculateAmount(command[2])
        user_amount = BalanceGet(message.author.id)
        final_amount = 0

        if amount == None:
            await self.help(message)
            return

        if amount > user_amount:
            await message.channel.send(embed=Embed(title="Dogecoin withdraw", description="Failed with error: Insufficient funds"))
            return

        if amount == -1:
            amount = user_amount
        
        final_amount = amount - glob.fee
        
        if final_amount <= 0:
            await message.channel.send(embed=Embed(title="Dogecoin withdraw", description="Failed with error: Transaction amount too small"))
            return
        
        res = await WalletSend(address, final_amount)

        if 'result' in res and type(res['result']) is str:

            user = BalanceRemove(message.author.id, amount)
            
            Log("withdraw", uid_from=message.author.id, address=address, amount=final_amount, fee=glob.fee)
            BalanceShiftBalance(glob.fee * glob.feedist - amount) # do this to collet DOGE and feed DOGE back into the system
            BalanceShiftTotal(-amount)

            await message.channel.send(embed=Embed(title="Dogecoin withdraw", description="Successfully deposited {0} DOGE to {1}. You can view the transaction [here](https://dogechain.info/tx/{2}).".format(amount, address, res['result'])))

            BalanceDisplay()

        else:
            if 'error' in res and type(res['error']) is dict and 'message' in res['error'] and type(res['error']['message']) is str:
                await message.channel.send(embed=Embed(title="Dogecoin withdraw", description="Failed with error: {0}".format(res['error']['message'])))

            else:
                
                await message.channel.send(embed=Embed(title="Dogecoin withdraw", description="Failed with error: Unknown. Please try again later."))
                print("Dogecoin withdraw failed for unknown reason.")

