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
from DiscordLoseitBot.helpers.server_ids import JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID, ALLIE_SERVER_ID
from DiscordLoseitBot.helpers.server_ids import ALLIE_TEAM_ID, TORPLE_SERVER_ID
from DiscordLoseitBot.helpers.constants import COW_GIFS
class SuperRelay(commands.Cog, name= 'SuperRelay'):
    def __init__(self, bot):
        self.bot = bot
        self.servers = [TEST_SERVER_ID,LOSEIT_SERVER_ID, ALLIE_SERVER_ID,ALLIE_TEAM_ID, TORPLE_SERVER_ID]

    @commands.command(name='superbaton', usage='\u2000[name]', brief = 'Pass the superbaton or check who has it',
         help='Without an argument it prints who has the superbaton. \n\u2003With an argment it passes the superbaton.')
    async def superbaton(self,ctx, name=None):
        '''
        Same as baton in relay.py but for enthousiastic people lol
        '''
        if ctx.message.guild.id not in self.servers:
            return

        guild_data = await get_guild_data(ctx.message.guild.id)
        superbaton = guild_data.superbaton

        if name == None:
            if superbaton == None:
                msg = "I don't know who has the superbaton right now"
                await ctx.channel.send(msg)
            else:
                msg = f"<@!{int(superbaton)}> has the superbaton!"
                await ctx.channel.send(msg)
                if self.bot.user.id == int(superbaton):
                    gif_number = random.randrange(0,len(COW_GIFS))
                    await ctx.channel.send(COW_GIFS[gif_number])

        elif ctx.message.mentions:
            await guild_data.pass_superbaton(ctx.message.mentions[0].id)
            msg = "The superbaton has been given to <@{0}>".format(ctx.message.mentions[0].id)
            await ctx.channel.send(msg)

            if self.bot.user.id == ctx.message.mentions[0].id:
                gif_number = random.randrange(0,len(COW_GIFS))
                await ctx.channel.send(COW_GIFS[gif_number])
            guild_data = await get_guild_data(ctx.message.guild.id)
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

    @commands.command(name='superbaton_rank', aliases=['superbaton_ranking'], usage='\u2000[week number]', brief = 'Prints the superbaton ranking.',
         help='Without an argument it prints ranking for the last completed week. \n\u2003With a week number it gives the rank for that week.')
    async def superbaton_rank(self,ctx, weeknumber=None):
        if ctx.message.guild.id not in self.servers:
            return
        if weeknumber == None:
            this_week = datetime.now(timezone('US/Eastern'))
            weeknumber = str(int(this_week.strftime('%W')))

        guild_data = await get_guild_data(ctx.message.guild.id)
        if len(guild_data.past_superbatons.keys()) == 0:
            message = "I have not saved any data yet."
            return await ctx.channel.send(message)
        if str(weeknumber) not in guild_data.past_superbatons.keys():
            new_weeknumber = str(int(datetime.now(timezone('US/Eastern')).strftime('%W')))

            if str(new_weeknumber) not in guild_data.past_superbatons.keys():
                message = f"I don't have any data for week {weeknumber}. The weeks I have are:\n"
                for weeks in guild_data.past_superbatons.keys():
                    weekstring = f"2021-W{weeks.rjust(2,'0')}"
                    week_start = datetime.strptime(weekstring + '-1', "%Y-W%W-%w").strftime("%B %d")
                    message += f'- week {weeks} (week of Monday {week_start})\n'
                return await ctx.channel.send(message)
            else:
                weeknumber = new_weeknumber

        past_superbatons = guild_data.past_superbatons[weeknumber]

        past_superbatons_df = pd.DataFrame.from_dict(list(past_superbatons.items())).rename(columns={0:'user_id',1:'score'})
        past_superbatons_df = past_superbatons_df.sort_values(by='score',ascending=False)
        past_superbatons_df = past_superbatons_df[past_superbatons_df['user_id'] != str(self.bot.user.id)]


        weekstring = f"2021-W{weeknumber.rjust(2,'0')}"
        week_start = datetime.strptime(weekstring + '-1', "%Y-W%W-%w").strftime("%B %d")
        message = f'superbaton scores for week {weeknumber} (week of Monday {week_start}):\n'
        for idx, row in past_superbatons_df.iterrows():
            if row['user_id'] == 'None':
                continue
            user = self.bot.get_guild(ctx.guild.id).get_member(int(row['user_id']))
            times = 'times'
            if int(row['score']) == 1:
                times = 'time'
            message += f"- {user.display_name} - {row['score']} {times} \n"


        await ctx.channel.send(message)


def setup(bot):
    bot.add_cog(SuperRelay(bot))
