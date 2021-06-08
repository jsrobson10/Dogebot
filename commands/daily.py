
import glob

from command import Command
from discord import Embed
from datetime import datetime

from wallet.balance import *

class CommandDaily(Command):

    def __init__(self):
        
        self.setName("daily")
        self.setDesc("Get some free dogecoins. The cooldown for this command is 24 hours.")

    async def run(self, message, command):
        
        amount, left = BalanceClaimDaily(message.author.id)

        if left <= 0:

            if amount > 0:
                
                await message.channel.send(embed=Embed(title="Daily dogecoin", description="<@{0}> has recieved their daily reward of {1} DOGE".format(message.author.id, amount)))

            else:

                await message.channel.send(embed=Embed(title="Daily dogecoin", description="Sorry, but there is currently no daily Dogecoin available."))
        
        else:

            await message.channel.send(embed=Embed(title="Daily dogecoin", description="You cannot claim your daily reward yet. You can claim another reward in {0}.".format(datetime.utcfromtimestamp(left).strftime("%H:%M:%S"))))
