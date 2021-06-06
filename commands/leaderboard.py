
from command import Command

class CommandLeaderboard(Command):

    def __init__(self):
        
        self.setName("leaderboard")
        self.setDesc("Display the top 10 dogecoin holders in the server.")

    async def run(self, message, command):
        pass

