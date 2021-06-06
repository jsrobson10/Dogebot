
from command import Command

class CommandWithdraw(Command):

    def __init__(self):
        
        self.setName("withdraw")
        self.setDesc("Send some or all of your dogecoin to an address.")
        self.setUsage("address amount")

    async def run(self, message, command):
        pass

