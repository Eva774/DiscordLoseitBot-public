#### Currently not in use. It was used before and I think it worked well
from discord.ext import commands
from DiscordLoseitBot.commands.GuildData import get_guild_data

from DiscordLoseitBot.helpers.server_ids import JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID, ALLIE_TEAM_ID
from DiscordLoseitBot.helpers.server_ids import STAYCATION, ROAD_TRIP

class Log_Reminders(commands.Cog, name='Log reminders'):
    def __init__(self, bot):
    
        self.bot = bot
        self.servers = [TEST_SERVER_ID]
    
    @commands.command(name='no_reminders',help='Opt-out of personal logging reminders on Fridays')
    async def no_reminders(self,ctx):
        '''
        Opt-out of reminders
        '''
        guildData = await get_guild_data(int(ctx.guild.id))

        await guildData.add_no_reminder(int(ctx.author.id))

        await ctx.send("You have opted out of the personal logging reminders on Fridays.")

    @commands.command(name='add_reminders',help='Opt-in to personal logging reminders on Fridays')
    async def add_reminders(self,ctx):
        '''
        Opt-in to reminders
        '''
        guildData = await get_guild_data(int(ctx.guild.id))

        await guildData.remove_no_reminder(int(ctx.author.id))

        await ctx.send("You have opted in to the personal logging reminders on Fridays.")

def setup(bot):
    bot.add_cog(Log_Reminders(bot))
