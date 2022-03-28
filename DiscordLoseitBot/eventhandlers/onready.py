
import datetime
import discord
from discord.ext import commands


from DiscordLoseitBot.helpers.server_ids import JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID
class OnReady(commands.Cog, name = "on_ready"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.servers = [JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID]
    @commands.Cog.listener(name="on_ready")
    async def on_ready(self):
        print("=======================================")
        print(datetime.datetime.now())
        print("{0} has connected with the prefix {1}".format(self.bot.user.name, self.bot.command_prefix))
        print("Everything's all ready to go~")
        
def setup(bot: commands.Bot):
    bot.add_cog(OnReady(bot))
