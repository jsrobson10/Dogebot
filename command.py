
import glob
from discord import Embed

class Command:

    name = ""
    desc = ""
    usage = ""

    def setName(self, name: str):
        self.name = name

    def setDesc(self, desc: str):
        self.desc = desc

    def setUsage(self, usage: str):
        self.usage = usage

    async def help(self, message):
        
        await message.channel.send(embed=Embed(title="Usage for {0}{1}".format(glob.prefix, self.name), description="{0}{1} {2}\n\n{3}".format(glob.prefix, self.name, self.usage, self.desc)))
    
    async def run(self, message, command):
        pass

