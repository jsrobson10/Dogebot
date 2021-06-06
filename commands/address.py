
import os
import qrcode

from wallet.balance import *

from command import Command
from discord import File, Embed

class CommandAddress(Command):

    def __init__(self):
        
        self.setName("address")
        self.setDesc("Get your wallet dogecoin address for you to transfer some dogecoin into.")

    async def run(self, message, command):
        
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

