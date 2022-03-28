#### Currently not in use. It was used before and I think it worked well

from asyncio.tasks import wait
import datetime
import json
import asyncio
from discord.ext import tasks
from numpy.core.defchararray import find
import pandas as pd
import numpy as np
import random

from DiscordLoseitBot.helpers.server_ids import ALLIE_TEAM_ID, LOG_REMINDER_CHANNEL, TEST_SERVER_ID
from DiscordLoseitBot.helpers.constants import LOG_GIFS
from DiscordLoseitBot.commands.GuildData import GuildData, get_guild_data

@tasks.loop(hours = 4) #Run every 4 hours
async def log_reminder(bot):
    with open('DiscordLoseitBot/Information/loseit_information.txt') as f:
        loseit_information = json.load(f)
    today = datetime.datetime.now()
    format = '%Y-%m-%d %H:%M:%S'
    until = datetime.datetime.strptime(loseit_information['until'],format)
    reminder_time = until - datetime.timedelta(hours = 5) #Reminder time is 5 hours before the deadline

    if today.day == reminder_time.day and today < reminder_time: #If the reminder time is today but has not passed yet: wait
        wait_seconds = (reminder_time-today).total_seconds()
        await asyncio.sleep(wait_seconds)
        GuildData = await get_guild_data(int(ALLIE_TEAM_ID)) #Was only used in Allie's team

        with open('DiscordLoseitBot/Information/activity_questions.txt') as f:
            activity_questions_dict = json.load(f)
        dates_list = activity_questions_dict['dates'] #Get all dates of the week
        not_logged_columns = dates_list + ['weight']   #Add weight to the columns

        reminders_sent = []
        while True:
            #### Get weight tracker
            tracker_url = loseit_information["challenge_tracker"]
            googleSheetId = tracker_url.split('/edit')[0]
            worksheetName = 'Tracker'#loseit_information["week"]
            URL = '{0}/gviz/tq?tqx=out:csv&sheet={1}'.format(
                googleSheetId,
                worksheetName
            )

            data_weight = pd.read_csv(URL)  #Load weight as dataframe
            data_weight = data_weight.set_index(data_weight.columns[1],drop=True) #Set index to usernames
            data_weight = data_weight[data_weight['Team'] == GuildData.team_name] #Filter to current team
            not_logged = pd.DataFrame(columns = not_logged_columns, index = data_weight.index)  #Empty dataframe to save unlogged entries

            strWeekNum = 'Week ' + loseit_information["week"][-1]
            if loseit_information["week"][-1] == '1':
                strWeekNum = 'Goal Weight'

            for user,data in data_weight.iterrows(): #Check if weight is logged
                if np.isnan(data[strWeekNum]):
                    not_logged.loc[user,'weight'] = 'no'
                else:
                    not_logged.loc[user,'weight'] = 'yes'
            #### Get activity tracker
            worksheetName = loseit_information["week"]+'%20Inter'
            URL = '{0}/gviz/tq?tqx=out:csv&sheet={1}'.format(
                googleSheetId,
                worksheetName
            )
            data_activity = pd.read_csv(URL) #load ativity tracker as dataframe
            data_activity = data_activity.set_index(data_activity.columns[1],drop=True) #usernames as index
            data_activity = data_activity[data_activity['What is your team?'] == GuildData.team_name] #filter for team
            data_activity = data_activity.groupby(data_activity.index).last()
            
            for username, activity in data_activity.iterrows():
                find_user = data_weight.filter(regex=rf'(?i){username.strip()}', axis=0).index.values #Find username in index
                if len(find_user) == 0: #If no results: no activity logged
                    continue
                else:
                    user = find_user[0]
                if user not in not_logged.index: #if user not in index: no activity logged
                    continue

                columns = activity.keys()
                for i in range(2,len(columns),2): #Loop through all columns, but 2 by 2 since a user could log either steps or minutes but possibly not both
                    day = [s for s in str.split(columns[i]) if s.isdigit()] #Find the day in the column name
                    if np.isnan(activity[columns[i]]) and np.isnan(activity[columns[i+1]]): #If steps AND minutes are NaN, that day is not logged 
                        if not_logged.loc[user,day].values[0] != 'yes':
                            not_logged.loc[user,day] = 'no'
                    else:
                        not_logged.loc[user,day] = 'yes'  
              

            not_logged = not_logged.replace(np.nan,'no') #If an entry in the not_logged dataframe is still empty, it isn't logged



            for user, data in not_logged.iterrows(): #Loop through all users
                if data[dates_list+['weight']].eq('yes').all() or user not in GuildData.usernames.values():
                    not_logged = not_logged.drop([user]) #If all are yes, everything is logged
                elif user in GuildData.usernames.values():
                    user_id = list(GuildData.usernames.keys())[list(GuildData.usernames.values()).index(user)] #Find discord ID
                    if user_id not in reminders_sent and str(user_id) not in GuildData.no_reminders:
                        #If reminder not sent yet and they did not opt out: send reminder 
                        if bot.get_guild(int(ALLIE_TEAM_ID)).get_member(int(user_id)) is None: #if member not found, drop them from the df
                            not_logged = not_logged.drop([user])
                        else:
                            not_logged.loc[user,'discord'] = user_id
                    else: 
                        not_logged = not_logged.drop([user])
                    
            timeleft = until - datetime.datetime.now()
            msg = ""
            #### Assemble message
            for user, data in not_logged.iloc[:6,:].iterrows(): # Send 5 reminders
                msg += f"Hey <@{data['discord']}>, you have not logged "
                reminders_sent.append(data['discord']) #Add them to list of sent reminders
                if data['weight'] == 'no':
                    msg += "your weight"
                    if data[dates_list].eq('no').any():
                        msg += " and your steps or minutes for "
                        msg += ", ".join(list(data[dates_list][data[dates_list].eq('no')].keys()))
                else:
                    msg += "your steps or minutes for "
                    msg += ", ".join(list(data[dates_list][data[dates_list].eq('no')].keys()))
                msg += " yet. \n"
            msg += f"\nLog your weight or activity with the commands in the bot or using the following forms: \nWeight form: <{loseit_information['weighin_form']}> \nActivity form: <{loseit_information['activity_form']}>"
            msg += "\n\nI am a bot and this is just a friendly reminder, logging is entirely optional. Use `?no_reminders` to stop receiving these reminders from me. You can always use `?add_reminders` if you wish to receive them again."
            msg += f"\n\nYou have {timeleft.seconds//3600} hours and {(timeleft.seconds//60)%60} minutes left to log."
            
            if len(not_logged) == 0:
                break
            guild = bot.get_guild(int(ALLIE_TEAM_ID))
            channel = guild.get_channel(int(LOG_REMINDER_CHANNEL))


            await channel.send(msg)
            await asyncio.sleep(10*60) #Wait 10 minutes before sending the next 5

        await asyncio.sleep(5*60*60)
