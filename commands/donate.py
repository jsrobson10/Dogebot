
import glob

from command import Command
from discord import Embed

from wallet.log import *
from wallet.balance import *

class CommandDonate(Command):

    def __init__(self):
        
        self.setName("donate")
        self.setDesc("Donate some of your dogecoin to {}. To use this you need to type the amount of dogecoins you want to donate. Typing 'all' will give all of your dogecoins. Typing 'roll' as the input will donate 1-6 dogecoins, 'megaroll' 6-36 dogecoins, and 'gigaroll' 36-216 dogecoins.".format(glob.name))
        self.setUsage("amount")

    async def run(self, message, command):
        
        if len(command) != 2:
            await self.help(message)
            return

        amount_str = command[1]

        amount = BalanceCalculateAmount(amount_str)

        # invalid amount
        if amount == None:
            await self.help(message)
            return

        # send all
        if amount == -1:
            amount = BalanceGet(message.author.id)

            if amount == 0:
                await message.channel.send(embed=Embed(title="Coin donation", description="Cannot donate coins if your wallet is empty"))
                return

        if BalanceTransfer(message.author, message.author.id, "", amount):

            Log("donate", amount, uid_from=message.author.id)

            await message.channel.send(embed=Embed(title="Thanks for your donation!", description="<@{0}> just donated {1} DOGE to {2}".format(message.author.id, amount, glob.name)))

        else:

            await message.channel.send(embed=Embed(title="Coin donation", description="You have insufficient funds to donate {0} DOGE".format(amount)))

