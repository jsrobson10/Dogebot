
from wallet.balance import *

from discord import Embed
from command import Command

class CommandRichest(Command):

    def __init__(self):
        
        self.setName("richest")
        self.setDesc("Display the top 10 richest doge holders in the server.")

    async def run(self, message, command):
        
        # cannot run inside DMs
        if message.channel.id == message.author.id:

            await message.channel.send(embed=Embed(title="Leaderboard", description="This command is for servers only."))
            return

        limit = 10
        users = BalanceGetAll()
        msg = ""
        i = 0
        
        for user in sorted(users, key=lambda c: c.getBalance(), reverse=True):

            try:
                await message.guild.fetch_member(user.getUid())
            except:
                continue

            if i >= limit:
                break

            i += 1
            msg += "{0} - <@{1}> {2} DOGE\n\n".format(i, user.getUid(), user.getBalance())
        
        await message.channel.send(embed=Embed(title="Leaderboard", description=msg))
