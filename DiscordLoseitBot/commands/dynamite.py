# from __future__ import absolute_import
import discord
import json
import time
from datetime import datetime, timedelta
from discord.ext import commands
from pytz import timezone
import pandas as pd

from DiscordLoseitBot.commands.GuildData import get_guild_data, GuildData
from DiscordLoseitBot.helpers.server_ids import JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID, ALLIE_SERVER_ID
from DiscordLoseitBot.helpers.server_ids import ALLIE_TEAM_ID, STAYCATION, ROAD_TRIP
class Dynamite(commands.Cog, name= 'Dynamite'):
    def __init__(self, bot):
        self.bot = bot
        self.default_time = 60
        self.max_time = 240
        self.servers = [TEST_SERVER_ID,LOSEIT_SERVER_ID,OWN_TEAM_SERVER_ID, ALLIE_SERVER_ID,ALLIE_TEAM_ID, STAYCATION, ROAD_TRIP]


    @commands.command(name='dynamite', usage='\u2000<names> [minutes]', brief = 'Toss a stick of dynamite to someone',
         help='Without an time limit it sets the detonation time to an hour. \n\u2003With an argment it passes the dynamite. You can pass it to multiple people, they can all save the others from an explosion.')
    async def dynamite(self,ctx, *, string=None):
        ''' 
        Pass a dynamite to someone to give the an incentive to be active.
        Can be disarmed by tossing a stick to someone else (or the bot) or by getting a baton or superbaton'''
        if ctx.message.guild.id not in self.servers:
            return
        guild_data = await get_guild_data(ctx.message.guild.id)
        current_dynamites = guild_data.dynamites

        mentioned_users = ctx.message.mentions
        mentioned_user_ids = [int(user.id) for user in mentioned_users]

        msg = ""
        holding_dynamite = False
        #### If there are no arguments, calculate the remaining time

        if string == None or mentioned_user_ids == [self.bot.user.id]:
            for timestamp in current_dynamites.copy():
                users = current_dynamites[str(timestamp)]
                if ctx.message.author.id in users:
                    detonation_time = datetime.fromtimestamp(int(timestamp))
                    time_to_spare = detonation_time - datetime.now()
                    hours = int(time_to_spare.seconds/3600)
                    minutes = int(time_to_spare.seconds/60) - hours*60

                    if hours == 0:
                        timestring = f'{minutes} minutes'
                    else:
                        timestring = f'{hours} hours and {minutes} minutes'

                    msg = f'You have {timestring} left to disarm the dynamite.'


                    if mentioned_user_ids == [self.bot.user.id]: #If bot is mentioned, disarm dynamite
                        await guild_data.remove_dynamite(str(timestamp),ctx.author.id)
                        msg = f'Congrats, you have disarmed the dynamite in time, with {timestring} to spare!'
                    holding_dynamite = True
                    return await ctx.send(f'{msg}')

        if (string == None or mentioned_user_ids == [self.bot.user.id]) and holding_dynamite == False:
            #If no message, or bot mentioned but no dynamite to disarm
            msg = "You don't have any dynamite to disarm."
            return await ctx.send(msg)


        if ctx.author.id in mentioned_user_ids:
            msg = "You cannot pass the dynamite to yourself. If you have any dynamite, it is not disarmed yet!"
            return await ctx.send(msg)

        if len(mentioned_user_ids) != 1 and self.bot.user.id in mentioned_user_ids:
            msg = "You can only tag me to disarm the dynamite, you can't pass the dynamite to me together with other people. If you have any dynamite, it is not disarmed yet!"
            return await ctx.send(msg)

        msg = ""
        #If users are mentioned: disarm own dynamite
        if len(mentioned_user_ids) > 0:
            for timestamp in current_dynamites.copy():
                users = current_dynamites[str(timestamp)]
                if ctx.message.author.id in users:
                    await guild_data.remove_dynamite(str(timestamp),ctx.author.id)
                    detonation_time = datetime.fromtimestamp(int(timestamp))
                    time_to_spare = detonation_time - datetime.now()
                    hours = int(time_to_spare.seconds/3600)
                    minutes = int(time_to_spare.seconds/60) - hours

                    if hours == 0:
                        timestring = f'{minutes} minutes'
                    else:
                        timestring = f'{hours} hours and {minutes} minutes'

                    msg += f'Congrats, you have disarmed the dynamite in time, with {timestring} to spare!\n '

        if mentioned_user_ids == [self.bot.user.id]:
            return await ctx.send(f'{msg}')


        time = self.default_time
        #If there are spaces in the input, a time has been given and should overwrite the default time.
        if " " in string:
            inputs = string.split(" ")
            if inputs[-1].isnumeric():
                time = int(inputs[-1])
                if time > self.max_time:
                    time = self.max_time
                    await ctx.send(f'The maximum time is {int(self.max_time/60)} hours, I have set the detonation time to {int(self.max_time/60)} hours')

        #### Check if tagged users are not already holding dynamite
        for timestamp in current_dynamites.copy():
            users = current_dynamites[str(timestamp)]
            double_users = []
            for user in users:
                if user in mentioned_user_ids:
                    double_users.append(f'<@{user}>')

            if len(double_users) ==1:
                return await ctx.send(f'{double_users[0]} is already holding some dynamite. Please select a new set of users.')
            elif len(double_users) > 1:
                return await ctx.send(f"{', '.join(double_users)} are already holding some dynamite. Please select a new set of users.")

        detonation_time = datetime.now() + timedelta(minutes = time)
        detonation_timestap = int(detonation_time.timestamp())

        await guild_data.toss_dynamite(detonation_timestap,mentioned_user_ids) #Add dynamite to guild data

        msg += f'You have tossed some dynamite to <@{mentioned_user_ids[0]}>'
        if len(mentioned_user_ids) > 2:
            for user_id in mentioned_user_ids[1:-1]:
                msg += f', <@{user_id}>'

        elif len(mentioned_user_ids) > 1:
            msg += f', and <@{mentioned_user_ids[-1]}>'

        if time < 60:
            msg += f' that will detonate in {round(time,1)} minutes. TIC TOC'
        else:
            msg += f' that will detonate in {round(time/60,1)} hours. TIC TOC'

        return await ctx.send(msg)

    @commands.command(name='dynamite_rank', aliases=['dynamite_ranking'], usage='\u2000[week number]', brief = 'Prints the dynamite ranking.',
         help='Without an argument it prints ranking for the last completed week. \n\u2003With a week number it gives the rank for that week.')
    async def dynamite_rank(self,ctx, weeknumber=None):
        ''' 
        Ranking for detonated dynamites.
        Basically the same as for the baton in relay.py
        '''
        if ctx.message.guild.id not in self.servers:
            return
        if weeknumber == None:
            this_week = datetime.now(timezone('US/Eastern'))
            weeknumber = str(int(this_week.strftime('%W')))

        guild_data = await get_guild_data(ctx.message.guild.id)
        if len(guild_data.past_dynamites.keys()) == 0:
            message = "I have not saved any data yet."
            return await ctx.channel.send(message)
        if str(weeknumber) not in guild_data.past_dynamites.keys():
            new_weeknumber = str(int(datetime.now(timezone('US/Eastern')).strftime('%W')))

            if str(new_weeknumber) not in guild_data.past_dynamites.keys():
                message = f"I don't have any data for week {weeknumber}. The weeks I have are:\n"
                for weeks in guild_data.past_dynamites.keys():
                    weekstring = f"2021-W{weeks.rjust(2,'0')}"
                    week_start = datetime.strptime(weekstring + '-1', "%Y-W%W-%w").strftime("%B %d")
                    message += f'- week {weeks} (week of Monday {week_start})\n'
                return await ctx.channel.send(message)
            else:
                weeknumber = new_weeknumber

        past_dynamites = guild_data.past_dynamites[weeknumber]

        past_dynamites_df = pd.DataFrame.from_dict(list(past_dynamites.items())).rename(columns={0:'user_id',1:'score'})
        past_dynamites_df = past_dynamites_df.sort_values(by='score',ascending=False)
        past_dynamites_df = past_dynamites_df[past_dynamites_df['user_id'] != str(self.bot.user.id)]


        weekstring = f"2021-W{weeknumber.rjust(2,'0')}"
        week_start = datetime.strptime(weekstring + '-1', "%Y-W%W-%w").strftime("%B %d")
        message = f'dynamite scores for week {weeknumber} (week of Monday {week_start}):\n'
        for idx, row in past_dynamites_df.iterrows():
            user = self.bot.get_guild(ctx.guild.id).get_member(int(row['user_id']))
            times = 'times'
            if int(row['score']) == 1:
                times = 'time'
            message += f"- {user.display_name} - {row['score']} {times} \n"


        await ctx.channel.send(message)

def setup(bot):
    bot.add_cog(Dynamite(bot))
