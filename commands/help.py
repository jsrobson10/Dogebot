
import glob
from discord import Embed
from command import Command

class CommandHelp(Command):

    def __init__(self):
        
        self.setName("help")
        self.setDesc("Display the help menu or display information about a command.")
        self.setUsage("command?")

    async def run(self, message, command):
        
        if len(command) == 2:

            for c in glob.commands:
                
                if c.name == command[1]:
                    
                    await c.help(message)
                    
                    return

            await message.channel.send(embed=Embed(title="Usage for {0}{1}".format(glob.prefix, command[1]), description="Command {0} not found".format(command[1])))

            return

        if len(command) > 2:

            this.help(message)

            return

        e = Embed(title="Commands for {0}".format(glob.name))

        for command in glob.commands:
            e.add_field(name="{0}{1}".format(glob.prefix, command.name), value="*Usage: {0}{1} {2}_ _*\n{3}".format(glob.prefix, command.name, command.usage, command.desc), inline=False)

        await message.channel.send(embed=e)
