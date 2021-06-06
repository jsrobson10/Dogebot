
from wallet.balance import *

from discord import Embed
from command import Command

class CommandLeaderboard(Command):

    def __init__(self):
        
        self.setName("leaderboard")
        self.setDesc("Display the top 10 dogecoin holders in the server.")

    async def run(self, message, command):
        
        # cannot run inside DMs
        if message.channel.id == message.author.id:

            await message.channel.send(embed=Embed(title="Leaderboard", description="This command is for servers only."))
            return

        limit = 10
        users = BalanceGetAll()
        msg = ""
        i = 0
        
        for uid in sorted(users, key=lambda c: users[c]['balance']):

            user = users[uid]
            
            try:
                await message.guild.fetch_member(uid)
            except:
                continue

            if i >= limit:
                break

            i += 1
            msg += "**{0} - <@{1}>** {2} DOGE\n\n".format(i, uid, user['balance'])
        
        await message.channel.send(embed=Embed(title="Leaderboard", description=msg))
