import discord
import json
import random
from discord.ext import commands

from DiscordLoseitBot.helpers.server_ids import JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID, COVID_CHANNEL_ID
# class OnMessage(commands.Cog,name="on_message"):
#     def __init__(self, bot: commands.Bot):
#         self.bot = bot
#         self.servers = [JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID]

    # @OnMessage.before_invoke
    # async def cog_before_invoke(self,ctx: commands.Context):
    #     print('cog local before: {0.command.qualified_name}'.format(ctx))

    # async def cog_after_invoke(self, ctx):
    #     print('cog local after: {0.command.qualified_name}'.format(ctx))

    # @commands.Cog.listener(name="on_message")

async def on_message(bot,message):
    # if message.guild.id == 713718109956997191:
    #     # if "uyuni" in message.content.lower() or "flats" in message.content.lower():
    #     #     images = 'https://imgur.com/mCZjKqm'

    #     #     await message.channel.send(images)
    #     if "rbg" in message.content.lower():
    #         await message.channel.send('https://imgur.com/1t43HZB')
    if (message.author.bot):
        return

    prefix = bot.command_prefix
    if message.content.startswith(prefix+" "):
        message.content = message.content[0]+message.content[2:]
        # return await bot.process_commands(message)

    if message.content.startswith(prefix+"echo"):
        return await bot.process_commands(message)

    channelIds = [COVID_CHANNEL_ID,732249840896966707] #Id of covid channel
    covid_channel = COVID_CHANNEL_ID
    detection_guilds = [OWN_TEAM_SERVER_ID, TEST_SERVER_ID] #IDs of test server and Petra server
    if isinstance(message.channel, discord.channel.DMChannel):
        await message.author.send("I am not meant to be used in DM's, the basic commands might work here, but the commands to log weight and/or activity will not work, so please use your challenge discord server for that.")
        print('{0} has sent a DM: "{1}"'.format(message.author.name,message.content))
    elif message.channel.id not in channelIds and message.guild.id in detection_guilds:# or "Eva" in message.guild.name:
        if "coronavirus" in message.content.lower() or \
                "corona" in message.content.lower() or \
                "covid" in message.content.lower() or \
                "pandemic" in message.content.lower() or \
                "quarantine" in message.content.lower():
                msg = "<@" + str(message.author.id) + "> All COVID talk must be confined to the channel <#" + str(covid_channel) + ">"
                await message.channel.send(msg)

    # if "petra" in message.content.lower() and message.author.id != 427539689663234060:
    #     if message.author.id == 375845639273054222 or message.author.id == 214967406768947200 or message.author.id == 756155266507997186:
    #         await message.channel.send("http://gph.is/2hrTIs7")
    #         await message.channel.send('Petra says hi!')
    #         return
    #     elif message.guild.id == 661630998945071204:
    #         await message.channel.send('https://imgur.com/a/O25fGOl')


    if '[' in message.content:
        message.content = message.content.replace('[','').replace(']','')
        # await bot.process_commands(message)
        # return
    await bot.process_commands(message)
# def setup(bot):
#     bot.add_cog(OnMessage(bot))
