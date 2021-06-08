
import glob

from discord import Embed
from command import Command

from wallet.log import *
from wallet.balance import *

class CommandGive(Command):

    def __init__(self):
        
        self.setName("give")
        self.setDesc("Give some of your dogecoin to someone on the server. To use this @mention the user you want to give to and type the amount of dogecoins you want to give. Typing 'all' will give all of your dogecoins. Typing 'roll' as the input will donate 1-6 dogecoins, 'megaroll' 6-36 dogecoins, and 'gigaroll' 36-216 dogecoins.")
        self.setUsage("@user amount")

    async def run(self, message, command):
        
        if len(command) != 3:
            await self.help(message)
            return

        mention = command[1]
        amount_str = command[2]

        if not (mention.startswith('<@') and mention.endswith('>')):
            await self.help(message)
            return

        uid = int(mention[2:-1])

        if uid == message.author.id:
            await message.channel.send(embed=Embed(title="Send coins", description="You cannot send coins to yourself"))
            return

        if uid != glob.bot_id:

            user_t = message.guild.get_member(uid)

            if user_t is None:
                await message.channel.send(embed=Embed(title="Send coins", description="You cannot send coins to a user that is not in this server"))
                return

            if user_t.bot and not glob.dry:
                await message.channel.send(embed=Embed(title="Send coins", description="You cannot send coins to a bot"))
                return

        amount = BalanceCalculateAmount(amount_str)

        # invalid
        if amount == None:
            await self.help(message)
            return

        # send all
        if amount == -1:
            amount = BalanceGet(message.author.id)

            if amount == 0:
                await message.channel.send(embed=Embed(title="Send coins", description="You cannot send coins if your wallet is empty"))
                return

        if BalanceTransfer(message.author, message.author.id, uid, amount):

            if uid == glob.bot_id:

                Log("donate", amount, uid_from=message.author.id)

                await message.channel.send(embed=Embed(title="Thanks for your donation!", description="<@{0}> just donated {1} DOGE to {2}".format(message.author.id, amount, glob.name)))

            else:

                Log("give", amount, uid_from=message.author.id, uid_to=uid)

                await message.channel.send(embed=Embed(title="Sent coins", description="<@{0}> just sent {1} DOGE to <@{2}>".format(message.author.id, amount, uid)))

        else:

            await message.channel.send(embed=Embed(title="Send coins", description="You have insufficient funds to send {0} DOGE".format(amount)))
