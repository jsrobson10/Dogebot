
import glob
from command import Command
from discord import Embed

from wallet.balance import *

class CommandBalance(Command):

    def __init__(self):
        
        self.setName("balance")
        self.setDesc("Get the current amount of dogecoin in your wallet, or @mention someone in the server to see their balance.")
        self.setUsage("@user?")

    async def run(self, message, command):
        
        uid = message.author.id

        if len(command) == 2:

            if command[1].startswith("<@") and command[1].endswith(">"):
                uid = int(command[1][2:-1])

            else:
                await self.help(message)
                return

        elif len(command) > 2:
            await self.help(message)
            return

        if uid != message.author.id and message.guild.get_member(uid) is None:
            await message.channel.send(embed=Embed(title="Account balance", description="Please mention a valid member of this server"))
            return

        balance = BalanceGet(uid)

        await message.channel.send(embed=Embed(title="Account balance", description="<@{0}> has {1} DOGE in their wallet".format(uid, balance)))

