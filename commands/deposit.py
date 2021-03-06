
import os
import qrcode
import glob

from wallet.balance import *

from command import Command
from discord import File, Embed

class CommandDeposit(Command):

    def __init__(self):
        
        self.setName("deposit")
        
        if not glob.dry:
            self.setDesc("Get your dogecoin address for you to transfer some dogecoin into. Transfer speeds may take a while.")

        else:
            self.setDesc("[Dry mode] Add new dogecoins into your account.")
            self.setUsage("amount")

    async def run(self, message, command):

        # do this if running in dry mode
        if glob.dry:

            amount = int(command[1])

            BalanceRemove(message.author.id, -amount)
            BalanceShiftTotal(amount)
            BalanceShiftBalance(amount)
            BalanceDisplay()

            Log("deposit", amount, address="0", uid_to=message.author.id)
            
            await message.author.send(embed=Embed(title="New deposit", description="A deposit of {0} DOGE has been added to your account. You can view this transaction [here](https://dogechain.info/tx/{1}).".format(amount, "0")))
            
            return

        address = await BalanceGetAddress(message.author.id)

        if address is None:
            await message.author.send(embed=Embed(title="Wallet address", description="Sorry, but due to technical difficulties we are unable to contact the payment server. Please try again later."))
            return

        if not os.path.exists("db/address"):
            os.makedirs("db/address")

        path = "db/address/{0}.png".format(address)

        if not os.path.exists(path):
            img = qrcode.make(address)
            img.save(path)

        await message.author.send(embed=Embed(title="Dogecoin address", description="Your dogecoin address is {0}. Please send your coins to the address for the funds to show up in your wallet.".format(address)), file=File(open(path, "rb"), filename="{0}.png".format(address)))

