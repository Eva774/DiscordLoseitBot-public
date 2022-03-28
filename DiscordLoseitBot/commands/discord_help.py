from discord.ext import commands
import discord
from dotenv import load_dotenv
import os
import json
from DiscordLoseitBot.helpers.server_ids import JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID, STAYCATION, ROAD_TRIP
from DiscordLoseitBot.helpers.server_ids import BASILISK_SERVER_ID, TORPLE_SERVER_ID, FUTURAMA_SERVER

class Discord_help(commands.Cog, name='discord'):
    def __init__(self, bot):
        self.bot = bot
        self.servers = [JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID, STAYCATION, ROAD_TRIP,BASILISK_SERVER_ID, TORPLE_SERVER_ID, FUTURAMA_SERVER]

    @commands.command(name='pin', help='Instructions to view the pinned posts of a channel')
    async def pin(self,ctx):
        '''
        how to view channel pinned messages
        '''
        if ctx.message.guild.id not in self.servers:
            return
        msg= "On mobile, look for the three dots on the upper right corner to access menu, click on pinned messages.\nOn desktop, click the pin icon in the same line as channel name and description."

        await ctx.channel.send(msg)

    @commands.command(name='descriptions', help='Instructions to view the description of a channel')
    async def descriptions(self,ctx):
        '''
        How to view channel descriptions
        '''
        if ctx.message.guild.id not in self.servers:
            return
        msg= "On mobile, look on upper right corner to press the person icon(between search and three dots) to see the description above the member list.\nOn desktop, it should appear in the same line as channel name."
        await ctx.channel.send(msg)

    @commands.command(name='help', usage='\u2000[command or category]',brief='Print the help list', help = 'Print the help list\n\n\u2003[command or category] \u2003 The command or category you need help on')
    async def help(self,ctx,subject=None):
        '''
        Our own custom help because I think it's prettier this way
        '''
        to_embed = discord.Embed()
        
        if subject == None:
            for cog_name in ctx.bot.cogs:
                msg=[] 
                message = {}   
                cog = ctx.bot.get_cog(cog_name)
                if ctx.guild.id not in cog.servers:
                    continue
                for command in cog.get_commands():
                    if not command.hidden:  
                        if command.brief == None:
                            message[command.name] = command.help
                            msg.append("*{0}*\n \u2003 {1}\n".format(command.name,command.help))
                        else:
                            message[command.name] = command.brief
                            msg.append("*{0}*\n \u2003 {1}\n".format(command.name,command.brief))
                string = []
                if cog_name == 'converters':
                    for name in message.keys():
                        string.append("*{0}*\n \u2003 {1}\n".format(name,message[name]))
                else:
                    for name in sorted(message):
                        string.append("*{0}*\n \u2003 {1}\n".format(name,message[name]))
                if msg:
                    to_embed.add_field(name='~~-'+' '*30+'-~~' + '\n**' + cog_name + '**\n', value=" ".join(string), inline=False)
            to_embed.add_field(name='\u200b', value="Type `{0}help [command]` for more info on a command. \nType `{0}help [category]` for more info on a category.".format(ctx.prefix), inline=False)
        else:
            for cog_name in ctx.bot.cogs:
                if str(cog_name).lower() == str(subject).lower():
                    cog = ctx.bot.get_cog(cog_name)
                    to_embed = discord.Embed()
                    msg=[]
                    message={}
                    if ctx.guild.id not in cog.servers:
                        continue
                    for command in cog.get_commands():
                        if not command.hidden:  
                            if command.brief == None:
                                message[command.name] = command.help
                            else:
                                message[command.name] = command.brief
                    string = []
                    if cog_name == 'converters':
                        for name in message.keys():
                            string.append("*{0}*\n \u2003 {1}\n".format(name,message[name]))
                    else:
                        for name in sorted(message):
                            string.append("*{0}*\n \u2003 {1}\n".format(name,message[name]))

                    to_embed.add_field(name= '**'+cog_name + '**\n', value=" ".join(string), inline=False)
                    to_embed.add_field(name='\u200b', value="Type `{0}help [command]` for more info on a command.".format(ctx.prefix), inline=False)

            for command_name in ctx.bot.commands:
                if str(command_name).lower() == str(subject).lower():
                    command = ctx.bot.get_command(str(command_name))
                    to_embed = discord.Embed()
                    msg=[]
                    if command.usage == None:
                        to_embed.add_field(name=ctx.prefix+command.name+'\n', value=command.help, inline=False)
                    else:
                        to_embed.add_field(name=ctx.prefix+command.name+command.usage+'\n', value=command.help, inline=False)
                        to_embed.add_field(name='\u200b', value="Arguments with <> are required.\nArguments with [] are optional.", inline=False)
            
        if len(to_embed) == 0: 
            to_embed.add_field(name='\u200b', value="The argument you gave is not a category or command. Use `{0}help` without an argument to get all the categories and commands.".format(ctx.prefix), inline=False)
        return await ctx.channel.send(embed = to_embed)

def setup(bot):
    bot.add_cog(Discord_help(bot))
