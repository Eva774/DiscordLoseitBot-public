# from __future__ import absolute_import
import discord
import json
import time
from datetime import datetime,timedelta
from pytz import timezone
import pandas as pd
from discord.ext import commands


import math
import random

from DiscordLoseitBot.commands.GuildData import get_guild_data, GuildData
from DiscordLoseitBot.helpers.server_ids import JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID, TORPLE_SERVER_ID
from DiscordLoseitBot.helpers.server_ids import ALLIE_SERVER_ID,ALLIE_TEAM_ID, STAYCATION, ROAD_TRIP, FUTURAMA_SERVER
from DiscordLoseitBot.helpers.constants import SPONGEBOB_GIFS, RECESS_BATON_GIFS

class Relay(commands.Cog, name= 'Relay'):
    def __init__(self, bot):
        self.bot = bot
        self.servers = [JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID, ALLIE_SERVER_ID
        ,ALLIE_TEAM_ID, STAYCATION, ROAD_TRIP, TORPLE_SERVER_ID, FUTURAMA_SERVER]

    @commands.command(name='baton', usage='\u2000[name]', brief = 'Pass the baton or check who has it',
         help='Without an argument it prints who has the baton. \n\u2003With an argment it passes the baton.')
    async def baton(self,ctx, name=None):
        '''
        To pass the baton to someone for exercising'''
        if ctx.message.guild.id not in self.servers:
            return
        
        guild_data = await get_guild_data(ctx.message.guild.id)
        baton = guild_data.baton #Get the current baton holder

        if name == None: #If there is no argument, we want to know who currently has the baton
            if baton == None:
                msg = "I don't know who has the baton right now"
                await ctx.channel.send(msg)
            else:
                msg = f"<@!{int(baton)}> has the baton!"
                await ctx.channel.send(msg)
                if self.bot.user.id == int(baton): #If the bot has the bot post a gif (at least in those two servers)
                    if ctx.guild.id == JOSH_SERVER_ID:
                        gif_number = random.randrange(0,len(SPONGEBOB_GIFS))
                        await ctx.channel.send(SPONGEBOB_GIFS[gif_number])
                    elif ctx.guild.id == OWN_TEAM_SERVER_ID:
                        gif_number = random.randrange(0,len(RECESS_BATON_GIFS))
                        await ctx.channel.send(RECESS_BATON_GIFS[gif_number])
        elif ctx.message.mentions: #If there is a mention, we pass the baton to them
            await guild_data.pass_baton(ctx.message.mentions[0].id)
            msg = "The baton has been given to <@{0}>".format(ctx.message.mentions[0].id)
            await ctx.channel.send(msg)

            if self.bot.user.id == ctx.message.mentions[0].id: #If baton is passed to the bot, post a gif
                if ctx.guild.id == JOSH_SERVER_ID:
                    gif_number = random.randrange(0,len(SPONGEBOB_GIFS))
                    await ctx.channel.send(SPONGEBOB_GIFS[gif_number])
                elif ctx.guild.id == OWN_TEAM_SERVER_ID:
                    gif_number = random.randrange(0,len(RECESS_BATON_GIFS))
                    await ctx.channel.send(RECESS_BATON_GIFS[gif_number])

            else:
                guild_data = await get_guild_data(ctx.message.guild.id)
                #### If the baton is not passed to the bot, we want to disarm possible dynamites
                current_dynamites = guild_data.dynamites

                msg = ""
                for timestamp in current_dynamites.copy():
                    users = current_dynamites[str(timestamp)]
                    if ctx.message.mentions[0].id in users:
                        await guild_data.remove_dynamite(str(timestamp),ctx.author.id)
                        detonation_time = datetime.fromtimestamp(int(timestamp))
                        time_to_spare = detonation_time - datetime.now()
                        hours = int(time_to_spare.seconds/3600)
                        minutes = int(time_to_spare.seconds/60) - hours*60

                        if hours == 0:
                            timestring = f'{minutes} minutes'
                        else:
                            timestring = f'{hours} hours and {minutes} minutes'

                        msg += f'Congrats, you have disarmed the dynamite in time, with {timestring} to spare!'
                        await ctx.send(f'{msg}')

    @commands.command(name='baton_rank', aliases=['baton_ranking'], usage='\u2000[week number]', brief = 'Prints the baton ranking.',
         help='Without an argument it prints ranking for the last completed week. \n\u2003With a week number it gives the rank for that week.')
    async def baton_rank(self,ctx, weeknumber=None):
        '''
        Ranking for the baton for the week.
        Weeknumbers are calendar numbers in this case, not challenge weeks
        '''
        if ctx.message.guild.id not in self.servers:
            return
        if weeknumber == None: #Without argument: use current week
            this_week = datetime.now(timezone('US/Eastern'))
            weeknumber = str(int(this_week.strftime('%W')))

        #Find past baton data in guild_data
        guild_data = await get_guild_data(ctx.message.guild.id)
        if len(guild_data.past_batons.keys()) == 0:
            message = "I have not saved any data yet."
            return await ctx.channel.send(message)
        if str(weeknumber) not in guild_data.past_batons.keys(): #If the week number is not in the data.
            new_weeknumber = str(int(datetime.now(timezone('US/Eastern')).strftime('%W')))

            if str(new_weeknumber) not in guild_data.past_batons.keys():
                message = f"I don't have any data for week {weeknumber}. The weeks I have are:\n"
                for weeks in guild_data.past_batons.keys():
                    weekstring = f"2021-W{weeks.rjust(2,'0')}"
                    week_start = datetime.strptime(weekstring + '-1', "%Y-W%W-%w").strftime("%B %d")
                    message += f'- week {weeks} (week of Monday {week_start})\n'
                return await ctx.channel.send(message)
            else: #If the current week is in the data, just use that
                weeknumber = new_weeknumber

        #Get dictionary of past batons and put it into a dataframe
        past_batons = guild_data.past_batons[weeknumber]
        past_batons_df = pd.DataFrame.from_dict(list(past_batons.items())).rename(columns={0:'user_id',1:'score'})
        past_batons_df = past_batons_df.sort_values(by='score',ascending=False)
        past_batons_df = past_batons_df[past_batons_df['user_id'] != str(self.bot.user.id)]


        weekstring = f"2021-W{weeknumber.rjust(2,'0')}"
        week_start = datetime.strptime(weekstring + '-1', "%Y-W%W-%w").strftime("%B %d")
        message = f'Baton scores for week {weeknumber} (week of Monday {week_start}):\n'
        for idx, row in past_batons_df.iterrows(): #Pars the rows into the message. If the user is not in the server anymore, don't include them
            user = self.bot.get_guild(ctx.guild.id).get_member(int(row['user_id']))
            times = 'times'
            if int(row['score']) == 1:
                times = 'time'
            if user:
                message += f"- {user.display_name} - {row['score']} {times} \n"


        await ctx.channel.send(message)

    @commands.command(name='week', help='Prints the number of the current week.')
    async def week(self,ctx):
        '''
        Return the weeknumber
        '''
        if ctx.message.guild.id not in self.servers:
            return
        weeknumber = datetime.now(timezone('US/Eastern')).strftime('%W')
        await ctx.channel.send(f'This week is week {int(weeknumber)}')





def setup(bot):
    bot.add_cog(Relay(bot))
