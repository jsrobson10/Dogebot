
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
        total = 0.0
        i = 0
        
        e = Embed(title="{0} Richest Members".format(message.guild.name))

        for user in sorted(users, key=lambda c: c.getBalance(), reverse=True):

            user_c = message.guild.get_member(user.getUid())

            if user_c is None:
                continue

            i += 1
            total += user.getBalance()

            if i <= limit:

                name = user_c.nick

                if name is None:
                    name = user_c.name

                n = "{0} -".format(i)

                if i == 1:
                    n = ":first_place:"
                elif i == 2:
                    n = ":second_place:"
                elif i == 3:
                    n = ":third_place:"

                e.add_field(name="{0} {1}".format(n, name), value="{0} DOGE".format(user.getBalance()), inline=False)

        e.insert_field_at(0, name=":bank: Server Total", value="{0} DOGE".format(total))

        await message.channel.send(embed=e)
