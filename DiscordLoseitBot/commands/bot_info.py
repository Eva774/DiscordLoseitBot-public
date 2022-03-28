import discord
from discord.ext import commands
import datetime

from DiscordLoseitBot.commands.GuildData import get_guild_data, GuildData
from DiscordLoseitBot.helpers.server_ids import JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID, TORPLE_SERVER_ID
from DiscordLoseitBot.helpers.server_ids import ALLIE_SERVER_ID,ALLIE_TEAM_ID, STAYCATION, ROAD_TRIP, PIRATE_KATIE, BASILISK_SERVER_ID, FUTURAMA_SERVER

def get_channel(ctx, channel_input:str):
    """
    Returns a channel object based on an id or a name.
    :param channel_input: The input string to parse to a channel name. (str)
    :return: The channel object. (str)
    """
    if channel_input[:2] == '<#':
        channel = ctx.bot.get_channel(int(channel_input[2:-1]))
    elif channel_input.isnumeric():
        channel = ctx.bot.get_channel(int(channel_input))
    else:
        channel = discord.utils.get(ctx.channel.guild.channels, name=channel_input)

    return channel


class Bot_Info(commands.Cog, name='bot_info'):
    def __init__(self, bot):
        self.bot = bot
        self.servers = [JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID, ALLIE_SERVER_ID
        ,ALLIE_TEAM_ID, STAYCATION, ROAD_TRIP, PIRATE_KATIE,BASILISK_SERVER_ID, TORPLE_SERVER_ID, FUTURAMA_SERVER]

    @commands.command(name='ping', help = 'Print the latency of the bot')
    async def ping(self,ctx):
        '''
        Gets the latency of the bot
        '''
        if ctx.message.guild.id not in self.servers:
            return
        def check(reaction,user):
            return str(reaction.emoji)=="\U0001F4A9" and user == ctx.author
        latency = self.bot.latency


        await ctx.send(latency)

    @commands.command(name='echo', hidden=True, brief = 'Print whatever comes after echo',usage='[message]', help='Print whatever comes after echo. The original command message will be deleted. \n\n[message]\u2003 The message that the bot will echo.')
    async def echo(self,ctx,*, content:str):
        '''
        Echos the sentence after
        '''
        if ctx.message.guild.id not in self.servers:
            return
        await ctx.message.delete()
        await ctx.send(content)

    @commands.command(name= 'botoverlord', help = 'Print the name of the owner of the bot')
    async def botoverlord(self,ctx):
        '''
        Owner info
        '''
        if ctx.message.guild.id not in self.servers:
            return
        msg = "My bot overload and owner is Eva. Feel free to message her with questions and suggestions."
        await ctx.channel.send(msg)

    @commands.command(name= 'bot_channel', help = 'Print the name of the owner of the bot')
    async def cmd_bot_channel(self,ctx,channel):
        '''
        set the bot channel (where to post a detonation gif for the dynamite)
        '''
        if ctx.message.guild.id not in self.servers:
            return

        guild_data = await get_guild_data(ctx.message.guild.id)

        if not ctx.message.author.guild_permissions.administrator:
            gif = "Only admins can do this."
            return await ctx.send(gif)
        channels = get_channel(ctx,channel)
        channel_id = channels.id
        channel_name = channels.name
        await guild_data.add_bot_channel(int(channel_id))
        await ctx.send(f'Set {channel_name} as the bot channel.')



def setup(bot):
    bot.add_cog(Bot_Info(bot))
