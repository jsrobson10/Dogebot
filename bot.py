
import asyncio
import glob
import base64
import secrets
import discord
import json

from wallet.log import LogInit
from wallet.balance import BalanceInit, BalanceUpdate
from wallet.wallet import WalletSendCommand

from command import Command
from commands.help import CommandHelp
from commands.deposit import CommandDeposit
from commands.withdraw import CommandWithdraw
from commands.give import CommandGive
from commands.richest import CommandRichest
from commands.balance import CommandBalance
from commands.donate import CommandDonate

glob.random = secrets.SystemRandom()

glob.config_default = {
    "discord": {
        "token": "",
        "prefix": "+",
        "name": "Dogebot",
    },
    "crypto": {
        "rpcuser": "",
        "rpcpassword": "",
        "rpcconnect": "http://127.0.0.1:22555",
        "mintransactions": 6,
        "walletpassword": "",
        "fee": 1,
    },
}


def writeConfigTemplate():

    with open("config.json", 'w') as f:
        f.write(json.dumps(glob.config_default, indent=4))

    print("Created new config. Please make changes to config.json")
    exit(1)

try:
    with open("config.json", "r") as f:
        glob.config = json.load(f)
except:
    writeConfigTemplate()

if not 'discord' in glob.config:
    writeConfigTemplate()

if not 'crypto' in glob.config:
    writeConfigTemplate()

if not 'rpcuser' in glob.config['crypto']:
    print("Cannot run without username")
    exit(1)

if not 'rpcpassword' in glob.config['crypto']:
    print("Cannot run without password")
    exit(1)

if not 'token' in glob.config['discord'] or glob.config['discord']['token'] == "":
    print("Cannot run without discord token")
    exit(1)

if not 'fee' in glob.config['crypto']:
    print("Cannot run without fee")
    exit(1)

if 'prefix' in glob.config['discord']:
    glob.prefix = glob.config['discord']['prefix']

if 'name' in glob.config['discord']:
    glob.name = glob.config['discord']['name']

if 'rpcconnect' in glob.config['crypto']:
    glob.rpcconnect = glob.config['crypto']['rpcconnect']

if 'mintransactions' in glob.config['crypto']:
    glob.mintransactions = glob.config['crypto']['mintransactions']

if 'walletpassword' in glob.config['crypto']:
    glob.walletpassword = glob.config['crypto']['walletpassword']

glob.fee = glob.config['crypto']['fee']
glob.rpcauth = base64.b64encode("{0}:{1}".format(glob.config['crypto']['rpcuser'], glob.config['crypto']['rpcpassword']).encode('utf-8')).decode('utf-8')

glob.commands = [
    CommandHelp(),
    CommandDeposit(),
    CommandWithdraw(),
    CommandGive(),
    CommandRichest(),
    CommandBalance(),
    CommandDonate(),
]

class DiscordDogecoin(discord.Client):

    async def on_ready(self):
    
        glob.bot_id = self.user.id
        glob.ready = True

        print("{0} is ready as {1}".format(glob.name, self.user))

    async def on_message(self, message):
        
        # dont listen to bots
        if message.author.bot:
            return

        # listen to commands starting with the prefix
        if message.content.startswith(glob.prefix):

            command = message.content.split(" ")
            command[0] = command[0][len(glob.prefix):]

            for c in glob.commands:

                if c.name == command[0]:
                    
                    await c.run(message, command)

    async def update_loop(self):

        # wait until ready
        while not glob.ready:
            await asyncio.sleep(1)

        # loop forever
        while True:

            # check if any doge has been recieved
            await BalanceUpdate(self)

            # only update every minute
            await asyncio.sleep(60)

client = DiscordDogecoin()

LogInit()

loop = asyncio.get_event_loop()
asyncio.ensure_future(BalanceInit())
asyncio.ensure_future(client.update_loop())

client.run(glob.config['discord']['token'])

loop.run_forever()
loop.close()

