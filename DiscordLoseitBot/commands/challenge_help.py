# from __future__ import absolute_import
import discord
import json
import time
import datetime
from pytz import timezone
import pandas as pd
from discord.ext import commands

import math
import random

from DiscordLoseitBot.helpers.form_submission import activity_answers, weighin_answers, submit_response
from DiscordLoseitBot.Information.json_write import update_questions
# from DiscordLoseitBot.helpers.json_write import update
from .GuildData import get_guild_data, GuildData
from DiscordLoseitBot.helpers.server_ids import JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID
from DiscordLoseitBot.helpers.server_ids import ALLIE_TEAM_ID, STAYCATION, ROAD_TRIP, PIRATE_KATIE
from DiscordLoseitBot.helpers.server_ids import MILESTONES_CHANNEL,BASILISK_SERVER_ID, TORPLE_SERVER_ID, FUTURAMA_SERVER
from DiscordLoseitBot.helpers.constants import CHEERING_GIFS
class Challenge_Help(commands.Cog, name= 'challenge'):
    def __init__(self, bot):
        self.bot = bot
        self.servers = [JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,ALLIE_TEAM_ID, STAYCATION, ROAD_TRIP, PIRATE_KATIE,BASILISK_SERVER_ID, 
        TORPLE_SERVER_ID, FUTURAMA_SERVER]
    def day_formatting(self,date):
        # Format dates to add the suffix (there was something wrong with this, but I don't remember what exactly tbh)
        if date[0] == '1':
            formated_date = date + 'th'
        elif date[-1] == '1':
            formated_date = date + 'st'
        elif date[-1] == '2':
            formated_date = date + 'nd'
        elif date[-1] =='3':
            formated_date = date + 'rd'
        else:
            formated_date = date + 'th'
        return formated_date

    def date_sorter(self,dates):
        #Sort the dates according to the order in the activity questions file
        with open('DiscordLoseitBot/Information/activity_questions.txt') as f:
            activity_questions_dict = json.load(f)
        dates_list = activity_questions_dict['dates']
        sort_order = [dates_list.index(x) for x in dates]
        sorted_dates = [x for _,x in sorted(zip(sort_order,dates))]
        return sorted_dates

    @commands.command(name='links', brief = 'Print some useful challenge links', help='Print the challenge links:\n -\u2000 the LoseitChallenges subreddit \n -\u2000 the tracker sheet \n -\u2000 the weigh in form \n -\u2000 the activity form')
    async def links(self,ctx):
        '''
        Replies with helpful links: subreddit, tracker sheet, weighin form and activity form (the latter two only if the deadline is in the future)
        '''
        if ctx.message.guild.id not in self.servers:
            return
        with open('DiscordLoseitBot/Information/loseit_information.txt') as f:
            loseit_information = json.load(f)

        today = datetime.datetime.now()
        format = '%Y-%m-%d %H:%M:%S'
        until = datetime.datetime.strptime(loseit_information['until'],format)
        if today>until:
            msg = str('**Here are some useful links for you!**\n Challenge subreddit: <{0}>\n Tracker: <{1}>\n The links to the forms still need to be updated'
            .format(loseit_information['LoseitChallenges_subreddit'],
                loseit_information['challenge_tracker']))
        else:
            msg= str('**Here are some useful links for you!**\n Challenge subreddit: <{0}>\n Tracker: <{1}>\n Weigh-in form: <{2}>\n Activity form: <{3}>'
            .format(loseit_information['LoseitChallenges_subreddit'],
                loseit_information['challenge_tracker'],
                loseit_information['weighin_form'],
                loseit_information['activity_form']))
        await ctx.channel.send(msg)


    @commands.command(name='timeline', help='Print the timeline of the challenge')
    async def timeline(self,ctx):
        '''
        Shows a timeline for the challenge
        '''
        if ctx.message.guild.id not in self.servers:
            return
        dates = ['January 7', 'January 14','January 21','January 28','February 4','February 11','February 18', 'February 25']
        weeks = ['Week 1','Week 2','Week 3','Week 4','Week 5','Week 6','Week 7', 'Results']
        infos = ['Sign-ups, battle royale.','Head to Head battles begin, signups are closed.',' ',' ',' ',' ','Final week. Battle royale!',' ']
        # padding is used so that the table is more or less aligned 
        padding1 = max(map(len,dates))+5
        padding2 = max(map(len,weeks))+3

        msg = " "
        for num in range(len(dates)):
            msg += f"__*{dates[num]}*__{' '*(padding1-len(dates[num]))}  {weeks[num].ljust(padding2)} {infos[num]}\n"

        await ctx.channel.send(msg)


    @commands.command(name='timeleft', aliases = ['deadline'], help = 'Print the remaining time before the next deadline')
    async def timeleft(self,ctx):
        '''
        Hours till logging deadline to help give reference for timezones
        '''
        if ctx.message.guild.id not in self.servers:
            return
        def days_hours_minutes(td):
            return td.days, td.seconds // 3600, (td.seconds // 60) % 60

        def next_weekday_fridays(d, weekday):
            days_ahead = weekday - d.weekday() #Days between today and the target day
            if days_ahead == 0 and d.hour >= 12:  # Today is the target day after noon est, therefore new target is next week
                days_ahead += 7
            elif days_ahead < 0: #Today is after the target day, therefore new target day is next week
                days_ahead += 7
            return d + datetime.timedelta(days_ahead)

        eastern = timezone('US/Eastern')
        today = datetime.datetime.now(eastern) #Compute time in eastern timezone
        friday = next_weekday_fridays(today,4) #Find the next friday
        friday = friday.replace(hour=12, minute=0, second=0, microsecond=0) #Set the hour on the next friday to 12
        timediff = friday - today #Compute the difference between now and next Friday
        timediffsplit = days_hours_minutes(timediff) #Split the time difference in days, hours and minutes
        msg = "The deadline to log weight and activity is Friday noon EST. This is in " + str(timediffsplit[0]) + " days, " + str(timediffsplit[1]) +" hours and " + str(timediffsplit[2]) + " minutes."
        await ctx.channel.send(msg)

    @commands.command(name='username', usage='\u2000[name]', brief = 'Prints argument or stored reddit username',
         help='Without an argument it prints the stored reddit username. This is the name that will be used for logging of activity and weights.\n\u2003With an argment it stores the argument as your reddit username.')
    async def username(self,ctx, name=None):
        '''
        Set the reddit username and link it to the discord ID
        '''
        if ctx.message.guild.id not in self.servers:
            return
        
        guild_data = await get_guild_data(ctx.message.guild.id) #Retrieve the guild data
        known_names = guild_data.usernames #Find all the known usernames


        if name == None: #If command is given without argument: return username if it is known
            if str(ctx.message.author.id) in known_names.keys():
                msg = 'The reddit username I have for you is: {0}'.format(known_names[str(ctx.message.author.id)])
            else:
                msg = "I don't know your reddit username yet"
        else: #If command is given with argument: ste the username to argument
            await guild_data.add_username(ctx.message.author.id,name)
            msg = "I have set your reddit username to: {0}".format(name)

        await ctx.channel.send(msg)

    @commands.command(name='teamname', usage='\u2000[team name]', brief = '**admin-only**\n\u2003 Prints argument or stored team name',
         help='*admin-only* \u2003 Without an argument it prints the stored team name. This is the team name that will be used for logging of activity and weights.\n\u2003With an argment it stores the argument as the team name for this server.')
    async def teamname(self,ctx,*, name=None):
        '''
        Set the teamname and link it to the discord guild id
        '''
        if ctx.message.guild.id not in self.servers:
            return
        guild_data = await get_guild_data(ctx.message.guild.id) #Get guild data
        team_name = guild_data.team_name #Get known teamnames


        if name == None: #If command is given without argument: return team name if it is known
            if team_name != "":
                msg = 'The team name I have for this server is: {0}'.format(team_name)
            else:
                msg = "I don't know your team name yet"
        else: #If command is given with argument: ste the team name to argument
            if ctx.message.author.guild_permissions.administrator  or await self.bot.is_owner(ctx.message.author):
                #Should only been down when the user is a server administrator or the owner of the bot.
                await guild_data.add_teamname(name)
                msg = "I have set your team name to: {0}".format(name)
            else: 
                await ctx.channel.send('Only team captains are supposed to set the team name.')
                return
        await ctx.channel.send(msg)


    @commands.command(name='activity',usage='\u2000<date>\u2000<steps>\u2000<minutes>', brief= 'Log your activity to the form',
         help = 'Log your activity with the stored reddit username.\n\u2003Change your reddit username with ?username [name] \n\n\u2003<date> \u2003\u2003 The day, so to submit your info for the 10th of July, you enter 10 \n\u2003<steps> \u2003 The amount of steps for that day, without commas or decimals\n\u2003<minutes> \u2003 The amount of activity minutes for that day, without commas or decmals')
    async def activity(self,ctx, date, steps, minutes):
        '''
        Log activity (steps and minutes) for a certain day
        '''
        if ctx.message.guild.id not in self.servers:
            return
        with open('DiscordLoseitBot/Information/loseit_information.txt') as f: #Load the challenge information
            loseit_information = json.load(f)

        #### Find out whether today is still before the deadline, otherwise the links should be updated
        input_steps = steps
        today = datetime.datetime.now()
        format = '%Y-%m-%d %H:%M:%S'
        until = datetime.datetime.strptime(loseit_information['until'],format)
        if today>until:
            msg = 'My owner still needs to update the form links, we thank you for your patience :)'
            await ctx.channel.send(msg)
            return

        #### Check if the username of the person is known
        guild_data = await get_guild_data(ctx.message.guild.id) #Get the guild data
        known_names = guild_data.usernames # Get the known usernames
        if str(ctx.message.author.id) in known_names.keys():
            username = known_names[str(ctx.message.author.id)]
        else:
            await ctx.channel.send("I don't know your reddit username yet, please set a username first with the `?username [name]` command")
            return
        #### Check if the team name is known
        team_name = guild_data.team_name
        if team_name == "":
            await ctx.channel.send("I don't know your team's name yet, captains should set a teamname first with the `?teamname` command")
            return

        #### If deadline is in the future and username and teamname are known
        with open('DiscordLoseitBot/Information/activity_questions.txt') as f:  #Load the questions from the form
            activity_questions_dict = json.load(f)
        activity_url = loseit_information['activity_form'] #Get form URL
        if date not in activity_questions_dict['dates']: #Check if the chosen date is actually in this week
            msg = 'This date is not in the current week, please enter a date between {0} and {1}'.format(activity_questions_dict['dates'][0],activity_questions_dict['dates'][-1])
            await ctx.channel.send(msg)
            return

        user = '{0}'.format(username) #username to string (idk why tbh)
        msg, activity_dict = activity_answers(activity_questions_dict, team_name, user, date, steps, minutes) #Make the dictionary with the answers for the form
        request = submit_response(activity_url, activity_dict)
        if msg == 'none': #The activity_answers function returns this if it was succesfull, otherwise it returns a message with the problem
            msg = "I submitted your activity with the reddit username `{0}`!\n{1} steps and {2} activity minutes for the {3}".format(user,steps, minutes, self.day_formatting(date))

        await ctx.channel.send(msg)

        #### check if the submitted steps bring the total above one million, only in 2 servers.
        if ctx.message.guild.id not in [ALLIE_TEAM_ID,TEST_SERVER_ID]:
            return
 
        tracker_url = loseit_information["challenge_tracker"] #Get tracker URL
        googleSheetId = tracker_url.split('/edit')[0] #Split the tracker URL before the edit to get the ID

        weekNumber = loseit_information["week"] #Get the week number
        worksheetName = weekNumber+'%20Inter' #Convert the week number to the worksheet

        URL = '{0}/gviz/tq?tqx=out:csv&sheet={1}'.format(
            googleSheetId,
            worksheetName
        )   #Combine the parts to ghet the URL

        guild_data = await get_guild_data(ctx.message.guild.id) #Get the guild data
        team_name = guild_data.team_name   #Get the teamname
        df = pd.read_csv(URL)   #Read the URL of the current tracker sheet into a dataframe

        for column in df.columns:   #Find the column with the usernames and the column with the teamnames
            if 'username' in column:
                column_name = column
            if 'team' in column:
                team_column = column

        df['filtered_usernames'] = df[column_name].str.lower().str.strip() #Change all usernames to lowercase and remove padded spaces
        df_last = df.groupby(['filtered_usernames']).last() #Use only the last entry per column for each user (to remove duplicates)
        df_team = df_last.copy().loc[df_last[team_column] == team_name] #Filter for team

        for user, data in df_team.iterrows():   #Loop through rows 
            steps = [0 if math.isnan(value) else value for value in data.filter(regex='.Steps.').values] #Find all the numbers in the columns with "steps"
            total_steps = sum(steps)   #Sum all the steps
            df_team.loc[user,'total_steps'] = int(total_steps)


        total_steps = sum(df_team['total_steps'])

        if total_steps - int(input_steps) < 1000000 and total_steps >= 1000000: #If previous was below one million and current is above it
            milestones_channel = ctx.bot.get_channel(int(MILESTONES_CHANNEL))
            msg = f"<@{ctx.author.id}> has just logged steps that brought our total over 1 million for this week!"
            await milestones_channel.send(msg)
            await milestones_channel.send('http://gph.is/28UIbfw')


    @commands.command(name='weighin',aliases=['weight'], usage='\u2000<weight>\u2000[goal]',brief='Log your weight to the form',
         help='Log your weight with the stored reddit username.\n\u2003Change your reddit username with ?username [name] \n\n\u2003<weight> \u2003 Your current weight, without commas or decimals. In week 0 this is your goal weight. ') # \n\u2003[goal] \u2003 Your goal weight, without commas or decimals. The goal is only necessary for week 0')
    async def weighin(self,ctx, weight, goal = None):
        '''
        Add a weighin for a user
        '''
        if ctx.message.guild.id not in self.servers:
            return
        #### Check if today is before the deadline
        with open('DiscordLoseitBot/Information/loseit_information.txt') as f:
            loseit_information = json.load(f)
        today = datetime.datetime.now()
        format = '%Y-%m-%d %H:%M:%S'
        until = datetime.datetime.strptime(loseit_information['until'],format)

        if today>until:
            msg = 'My owner still needs to update the form links, we thank you for your patience :)'
            await ctx.channel.send(msg)
            return
        #### Check if username is known
        guild_data = await get_guild_data(ctx.message.guild.id)
        known_names = guild_data.usernames
        if str(ctx.message.author.id) in known_names.keys():
            username = known_names[str(ctx.message.author.id)]
        else:
            await ctx.channel.send("I don't know your reddit username yet, please set a username first with the `?username [name]` command")
            return
        #### Check if team name is known
        team_name = guild_data.team_name
        if team_name == "":
            await ctx.channel.send("I don't know your team's name yet, captains should set a teamname first with the `?teamname` command")
            return
        with open('DiscordLoseitBot/Information/weighin_questions.txt') as f:
            weighin_questions_dict = json.load(f)


        weighin_url = loseit_information['weighin_form'] #Get url weighin form
        user = '{0}'.format(username)
        msg, weighin_dict = weighin_answers(weighin_questions_dict, user, weight, goal) #Get dict with weighin answers
        request = submit_response(weighin_url, weighin_dict)
        if msg == 'none': #The weighin_answers function returns this if it was succesfull, otherwise it returns a message with the problem
            msg = "I submitted your weighin with the reddit username `{0}`!\nWeight of {1} lbs ".format(user,weight)
        await ctx.channel.send(msg)


    @commands.command(name='weighinkg',aliases=['weightkg'], usage='\u2000<weight>\u2000[goal]',brief='Log your weight in kg to the form',
        help='Log your weight in kg with the stored reddit username.\n\u2003Change your reddit username with ?username [name] \n\n\u2003<weight> \u2003 Your current weight, without commas or decimals. \n\u2003[goal] \u2003 Your goal weight, without commas or decimals. The goal is only necessary for week 0')
    async def weighinkg(self,ctx, weightkg, goalkg = None):
        '''
        Add a weighin for a user. 
        The function is the exact same as the weighin function, but it converts the weight and the goal to kg (rounded to 2 digits)
        '''
        if ctx.message.guild.id not in self.servers:
            return
        if "," in weightkg:
            weightkg = weightkg.replace(",",".")

        weight = str(int(float(weightkg) * 2.205 * 100) / 100)
        if goalkg != None:
            if "," in goalkg:
                goalkg = goalkg.replace(",",".")
            goal = str(int(float(goalkg) * 2.205 * 100) / 100)
        else:
            goal = None
        with open('DiscordLoseitBot/Information/loseit_information.txt') as f:
            loseit_information = json.load(f)

        today = datetime.datetime.now()
        format = '%Y-%m-%d %H:%M:%S'
        until = datetime.datetime.strptime(loseit_information['until'],format)
        if today - datetime.timedelta(days = 7) > until:
            msg = 'Logging for this challenge will start on July 9.'
            await ctx.channel.send(msg)
            return
        if today>until:
            msg = 'My owner still needs to update the form links, we thank you for your patience :)'
            await ctx.channel.send(msg)
            return
        guild_data = await get_guild_data(ctx.message.guild.id)
        known_names = guild_data.usernames
        if str(ctx.message.author.id) in known_names.keys():
            username = known_names[str(ctx.message.author.id)]
        else:
            await ctx.channel.send("I don't know your reddit username yet, please set a username first with the `?username [name]` command")
            return
        team_name = guild_data.team_name
        if team_name == "":
            await ctx.channel.send("I don't know your team's name yet, captains should set a teamname first with the `?teamname` command")
            return
        with open('DiscordLoseitBot/Information/weighin_questions.txt') as f:
            weighin_questions_dict = json.load(f)


        weighin_url = loseit_information['weighin_form']
        user = '{0}'.format(username)

        msg, weighin_dict = weighin_answers(weighin_questions_dict, user, weight, goal)
        request = submit_response(weighin_url, weighin_dict)
        if msg == 'none':
            msg = "I submitted your weighin with the reddit username `{0}`!\nWeight of {1} kg, which is {2} lbs ".format(user,weightkg,weight)
        await ctx.channel.send(msg)

    @commands.command(name='set_links',usage='\u2000<new weigh in>\u2000<new activity>',brief='**admin-only**\n\u2003 Set the new links', help='*admin-only* \u2003  To set new links. Note: this takes a few seconds :)\n\n\u2003<new weigh in> \u2003 Link to the new weigh in form\n\u2003<new activity> \u2003 Link to the new activity form ')
    async def set_links(self, ctx, new_weighin, new_activity):
        '''
        Set the links for the weighin and activity forms
        '''
        if ctx.message.guild.id not in self.servers:
            return
        if ctx.message.author.guild_permissions.administrator or await self.bot.is_owner(ctx.message.author):
            #Only if the user is admin or bot owner
            with open('DiscordLoseitBot/Information/loseit_information.txt') as f: #Get current info
                loseit_information = json.load(f)
            loseit_information['weighin_form'] = new_weighin #replace links with new ones
            loseit_information['activity_form'] = new_activity

            #### Compute the new expiration date of the links
            def next_weekday_friday(d, weekday):
                days_ahead = weekday - d.weekday()
                if days_ahead <= 0 and d.hour > 18:  # Target day already happened this week
                    days_ahead += 7
                return d + datetime.timedelta(days_ahead)
            today = datetime.datetime.now()
            if today.weekday() != 4:
                friday = next_weekday_friday(today,4).replace(hour=18, minute=0, second=0, microsecond=0)
            else:
                friday = (today.replace(hour=18, minute=0, second=0, microsecond=0) + datetime.timedelta(days=7)).replace(hour=18, minute=0, second=0, microsecond=0)
            format = '%Y-%m-%d %H:%M:%S'
            loseit_information['until'] = datetime.datetime.strftime(friday, format)

            location = 'DiscordLoseitBot/Information/'  #Folder with the files
            msg = 'Updating the info, give me a sec.'  #Post this because loading the info takes a while
            await ctx.channel.send(msg)
            week = update_questions(new_weighin, new_activity,location) #update the questions
            loseit_information['week'] = week   #Set the new weak number

            with open('DiscordLoseitBot/Information/loseit_information.txt','w') as f: #dump the data
                json.dump(loseit_information,f,indent=4)
            msg = 'The infomation is updated.'
            await ctx.channel.send(msg)
        else:
            msg = "Only my owner is allowed to do that."
            await ctx.channel.send(msg)

    @commands.command(name='days', help='Get the dates of this week')
    async def days(self,ctx):
        ''' 
        Returns the days in this week for the acitivity form
        '''
        if ctx.message.guild.id not in self.servers:
            return

        #### Check if form deadline is in the future
        with open('DiscordLoseitBot/Information/loseit_information.txt') as f:
            loseit_information = json.load(f)
        today = datetime.datetime.now()
        format = '%Y-%m-%d %H:%M:%S'
        until = datetime.datetime.strptime(loseit_information['until'],format)
        if today>until:
            msg = 'My owner still needs to update the form links, we thank you for your patience :)'
            await ctx.channel.send(msg)
            return

        with open('DiscordLoseitBot/Information/activity_questions.txt') as f:  #load questions
            activity_questions_dict = json.load(f)
        dates_list = activity_questions_dict['dates'] #load dates
        #Find this month and next and previous month
        this_month = today.strftime('%B')
        if today.month == 12:
            next_month = today.replace(month = 1).strftime('%B')
        else:
            next_month = today.replace(day = 1,month = today.month + 1).strftime('%B')

        if today.month == 1:
            previous_month = today.replace(month = 12).strftime('%B')
        else:
            previous_month = today.replace(day=1,month = today.month - 1).strftime('%B')

        #Check in which months the first and last day of the list are
        if int(dates_list[0])<int(dates_list[-1]):
            day_1 = this_month +' '+ self.day_formatting(dates_list[0])
            day_2 = this_month +' '+ self.day_formatting(dates_list[-1])
        elif today.day > 10:
            day_1 = this_month +' '+ self.day_formatting(dates_list[0])
            day_2 = next_month +' '+ self.day_formatting(dates_list[-1])
        else:
            day_1 = previous_month +' '+ self.day_formatting(dates_list[0])
            day_2 = this_month +' '+ self.day_formatting(dates_list[-1])
        msg = 'This week starts on ' + day_1 + ' and ends on '+ day_2 + '.'
        await ctx.channel.send(msg)

    @commands.command(name = 'logged',help='What did you log for this week?')
    async def cmd_logged(self,ctx):
        '''
        Returns the dates for which the user has logged
        '''
        if ctx.message.guild.id not in self.servers:
            return
        #### Check if usrename is known
        with open('DiscordLoseitBot/Information/loseit_information.txt') as f:
            loseit_information = json.load(f)
        tracker_url = loseit_information["challenge_tracker"]

        guild_data = await get_guild_data(ctx.message.guild.id)
        known_names = guild_data.usernames

        if str(ctx.message.author.id) not in known_names.keys():
            await ctx.send("I don't know your reddit username yet, please set a username first with the `?username [name]` command")
            return

        user = '{0}'.format(known_names[str(ctx.message.author.id)]) #Get reddit username for discord id

        googleSheetId = tracker_url.split('/edit')[0] #Get ID of google sheet
        worksheetName = loseit_information["week"] #Name of worksheet weighins
        if worksheetName == 'W1':
            worksheetName = 'GOALS'
        URL = '{0}/gviz/tq?tqx=out:csv&sheet={1}'.format(
            googleSheetId,
            worksheetName
        )   #Combine info to get URL of the submitted weights

        df1 = pd.read_csv(URL) #Load weight URL to dataframe
        df1 = df1.set_index(df1.columns[1],drop=True) #Set second column (usernames) as index
        df1.index = df1.index.str.lower().str.strip()  #Usernames to lowercase and remove padded spaces
        weight_logged = False
        if user.lower() in df1.index: #Check if weight is logged
            message = str(ctx.message.author.display_name) + "\nWeight is logged \n"
            weight_logged = True
        else:
            message = str(ctx.message.author.display_name) + "\nWeight is **NOT** logged \n"

        worksheetName = loseit_information["week"]+'%20Inter' #Name of worksheet activity
        URL = '{0}/gviz/tq?tqx=out:csv&sheet={1}'.format(
            googleSheetId,
            worksheetName
        ) #Combine info to get URL of subitted activity

        df = pd.read_csv(URL) #Load activity sheet to dataframe
        df = df.drop(columns = [df.columns[0],df.columns[2]]) #Drop first and third column
        df = df.set_index(df.columns[0],drop=True)#Set second column (usernames) as index
        filled_dates = []
        df.index = df.index.str.strip().str.lower()#Usernames to lowercase and remove padded spaces
        if user.lower() in df.index: #If username is in the dataframe
            df_user = df.loc[user.lower(),:] #Filter data for the user
            if isinstance(df_user,pd.Series): #If there is only one entry, the previous filter returns a series
                names = df_user.loc[df_user.notnull()].keys()   #Find columns nonzero values
                # Find the dates in the columns and append to filled_dates
                for name in names:
                    for word in name.split():
                        if word.isnumeric() and word not in filled_dates:
                            filled_dates.append(word)

            else:
                for key,values in df_user.iterrows(): #Loop through rows
                    names = values.loc[values.notnull()].keys() #Find nonzero columns in row
                    #Find dates in columns and append to filled_dates
                    for name in names:
                        for word in name.split():
                            if word.isnumeric() and word not in filled_dates:
                                filled_dates.append(word)
            if filled_dates == []:
                message += "Activity is **NOT** logged"
            else:
                message += "Activity is logged for: "+", ".join(self.date_sorter(filled_dates)) #Put dates in right order with sorter function
        else:
            message +="Activity is **NOT** logged"

        #### In some servers: special gif when everything is logged
        all_logged = False
        if weight_logged and len(filled_dates) == 7 and ctx.guild.id in [OWN_TEAM_SERVER_ID,ALLIE_TEAM_ID]:
            message = "Congrats, " + str(ctx.message.author.display_name) + ", you logged everything!"
            all_logged = True

        await ctx.send(message)

        if all_logged:
            gif_number = random.randrange(0,len(CHEERING_GIFS))
            await ctx.send(CHEERING_GIFS[gif_number])

    @commands.command(name = 'battle', help='How are we doing in the head to head challenge?')
    async def battle(self,ctx):
        '''
        Compare current score in head-to-head battle.
        This does not work for the battle royale
        '''
        if ctx.message.guild.id not in self.servers:
            return
        #### Check if team name is known
        with open('DiscordLoseitBot/Information/loseit_information.txt') as f:
            loseit_information = json.load(f)
        tracker_url = loseit_information["challenge_tracker"]

        guild_data = await get_guild_data(ctx.message.guild.id)
        team_name = guild_data.team_name
        if team_name == "":
            await ctx.channel.send("I don't know your team's name yet, captains should set a teamname first with the `?teamname` command")
            return

        googleSheetId = tracker_url.split('/edit')[0] #Get tracker sheet ID
        worksheetName = loseit_information["week"] #Get week name
        URL = '{0}/export?format=xlsx'.format(
            googleSheetId,
            worksheetName
        )
        df = pd.read_excel(URL,sheet_name = '{0} Activity'.format(worksheetName)) #Read activity summary as dataframe
        df = df.set_index(df.iloc[:,0]) 
        team_found = False
        for row, data in df.iterrows():
            if 'head' in str(row).lower(): #Find the row with 'head' as a name.
                subject = row.split(' ')[-1]
                row_number = df.index.get_loc(row) + 1
                break

        df_battle = df.iloc[row_number:,:] #Filter for rows after row with 'head'
        df_battle.index = df_battle.index.str.lower() #Set index to lowercase
        if team_name.lower() in df_battle.index: #If current team is in index, then the enemy is in the third column
            counter_team = df_battle.loc[team_name.lower(),:][2]
            team_found = True


        if team_found == False:
            column = df_battle.iloc[:,2]
            for row, names in column.items(): #If team is not in index, find it in the third column and the enemy in the first
                if team_name.lower() == str(names).lower():
                    team_found = True
                    counter_team = df_battle.loc[row][0]
                    break

        #### Find scores for our and enemy team
        df_scores = df.iloc[:row_number,:]
        df_scores.columns = df_scores.iloc[0,:]
        for column, data in df_scores.items():
            if subject.lower() in column.lower():
                our_activity = data.loc[team_name]
                other_activity = data.loc[counter_team]
                break

        if (math.isnan(float(our_activity)) or math.isnan(float(other_activity))):
            #If this is the case, the sheet is doing its weird shit, if it happens to often, bug Jameson about it
            await ctx.channel.send("The sheet is busy with calculations, please wait a bit and try again.")
            return
        elif float(our_activity) > float(other_activity):
            msg = 'Go team!!'
        else:
            msg = "Let's kick it up a notch!!"


        await ctx.channel.send("We have {0:,} {1}, {2} has {3:,} {1}. That's a difference of {5:,} {1}! {4}".format(int(our_activity),subject.lower(),counter_team,int(other_activity),msg,int(abs(int(float(our_activity))-int(float(other_activity))))))

    @commands.command(name = 'top',usage='\u2000[week]', brief='Get the top 10 exercisers of last week', help='Get the top 10 exercisers. \nWithout a week, you get the top 10 of last week.\nGet a specific week by entering the week as W0 for example.')
    async def top(self,ctx,week = None):
        '''
        Find top 10 for the last completed week
        I think it gives an error in week 0 without an argument because there is no week -1
        '''

        if ctx.message.guild.id not in self.servers:
            return
        #In own team, not everyone can request this
        if ctx.guild.id == OWN_TEAM_SERVER_ID and not ctx.message.author.guild_permissions.administrator:
            await ctx.channel.send("Only captains can do this.")
            return
        with open('DiscordLoseitBot/Information/loseit_information.txt') as f:
            loseit_information = json.load(f)
        
        tracker_url = loseit_information["challenge_tracker"]
        googleSheetId = tracker_url.split('/edit')[0]
        if week == None: #If no argument: find last week
            weekNumber = loseit_information["week"]
            lastWeek = 'W'+str(int(weekNumber[-1])-1)
            worksheetName = lastWeek+'%20Inter'
            if weekNumber[-1] == '0':
                worksheetName = 'W0%20Inter'
        else: #If argument, check that it is a week in the past
            weekNumber = int(loseit_information["week"][-1])
            if int(week[-1]) <= weekNumber:
                worksheetName = week +'%20Inter'
            else:
                await ctx.send('Please enter a week in the past, I cannot predict the future.')
                return
        URL = '{0}/gviz/tq?tqx=out:csv&sheet={1}'.format(
            googleSheetId,
            worksheetName
        )   #URL for activity sheet

        guild_data = await get_guild_data(ctx.message.guild.id)
        team_name = guild_data.team_name
        df = pd.read_csv(URL) #Load activity sheet into dataframe

        for column in df.columns:
            if 'username' in column:
                column_name = column
            if 'team' in column:
                team_column = column
        df['filtered_usernames'] = df[column_name].str.lower().str.strip() #Usernames to lowercase and remove padded spaces
        df_last = df.groupby(['filtered_usernames']).last() #This makes sure that only the last entry for each column is selected to overwrite if someone enters a date multiple times
        df_team = df_last.copy().loc[df_last[team_column] == team_name] #Filter for the own team

        for user, data in df_team.iterrows(): #Sum all the steps and minutes separately
            steps = [0 if math.isnan(value) else value for value in data.filter(regex='.Steps.').values]
            total_steps = sum(steps)
            df_team.loc[user,'total_steps'] = int(total_steps)


            minutes = [0 if math.isnan(value) else value for value in data.filter(regex='.Minutes.').values]
            total_minutes = sum(minutes)
            df_team.loc[user,'total_minutes'] = int(total_minutes)

        #Sort and find top 10 for steps and minutes separately
        df_steps = df_team.copy().sort_values(by=['total_steps'],ascending=False).iloc[:,[-2]].copy().head(10)
        df_minutes = df_team.copy().sort_values(by=['total_minutes'],ascending=False).iloc[:,[-1]].copy().head(10)

        users = []
        steps = []
        names = []
        for user, total in df_steps.iterrows():
            user_found = False
            if ctx.guild.id == OWN_TEAM_SERVER_ID and ctx.message.author.guild_permissions.administrator:
                # In own team server, the users that have linked their username are tagged in discord
                for user_id, name in guild_data.usernames.items():
                    member = ctx.message.guild.get_member(int(user_id))
                    if user == name and member != None: #Only tagged if they have linked their username
                        user_found = True
                        users.append('<@{0}> - '.format(str(user_id)))
                        steps.append('{0}'.format(str(int(total.values[0]))))
                        names.append(member.display_name)
                        break
                if user_found == False: #Otherwise reddit name is used
                    users.append('u/{0} - '.format(str(user)))
                    steps.append('{0}'.format(str(int(total.values[0]))))
                    names.append(str(user))

                msg = "**Top 10 steps week {0}**\n".format(worksheetName[1])
                for num in range(len(users)):
                    msg += f"{users[num]}{steps[num]}\n"

            else: #In other servers: reddit usernames are used
                users.append('{0}'.format(str(user)))
                steps.append('{0}'.format(str(int(total.values[0]))))
                padding1 = max(map(len,users))+7

                msg = "+== Top 10 steps week {0} ==+\n".format(worksheetName[1])
                for num in range(len(users)):
                    msg += f"{users[num]}{' '*(padding1-len(users[num]))} {steps[num]}\n"

        #in own team: regular string message for tags, in other teams: code block
        if ctx.guild.id == OWN_TEAM_SERVER_ID and ctx.message.author.guild_permissions.administrator:
            await ctx.channel.send(msg+'\u200b\n\u2003\n')
        else:
            await ctx.channel.send("```diff\n"+msg+"```")

        #### Same as before but for minutes
        users = []
        minutes = []
        names = []
        for user, total in df_minutes.iterrows():
            user_found = False
            if ctx.guild.id == TEST_SERVER_ID and ctx.message.author.guild_permissions.administrator:
                for user_id, name in guild_data.usernames.items():
                    member = ctx.message.guild.get_member(int(user_id))
                    if user == name and member != None:
                        user_found = True
                        users.append('<@{0}> - '.format(str(user_id)))
                        minutes.append('{0}'.format(str(int(total.values[0]))))
                        names.append(member.display_name)
                        break
                if user_found == False:
                    users.append('u/{0} - '.format(str(user)))
                    minutes.append('{0}'.format(str(int(total.values[0]))))
                    names.append(str(user))

                msg = "**Top 10 minutes week {0}**\n".format(worksheetName[1])
                for num in range(len(users)):
                    msg += f"{users[num]}{minutes[num]}\n"

            else:
                users.append('{0}'.format(str(user)))
                minutes.append('{0}'.format(str(int(total.values[0]))))
                padding1 = max(map(len,users))+7

                msg = "+== Top 10 minutes week {0} ==+\n".format(worksheetName[1])
                for num in range(len(users)):
                    msg += f"{users[num]}{' '*(padding1-len(users[num]))} {minutes[num]}\n"
        if ctx.guild.id == TEST_SERVER_ID and ctx.message.author.guild_permissions.administrator:
            await ctx.channel.send(msg)
        else:
            await ctx.channel.send("```diff\n"+msg+"```")



    @commands.command(name = 'ranking',usage='\u2000[week]', brief='Find out how you ranked last week', help='Get your ranking in steps and activity minutes in our team. \nWithout a week, you get the ranking of last week.\nGet a specific week by entering the week as W0 for example.')
    async def ranking(self,ctx,week = None):
        '''
        Find place in ranking for the own team
        '''
        if ctx.message.guild.id not in self.servers:
            return
        #### Check if username is known
        guild_data = await get_guild_data(ctx.message.guild.id)
        team_name = guild_data.team_name
        known_names = guild_data.usernames
        if str(ctx.message.author.id) in known_names.keys():
            username = known_names[str(ctx.message.author.id)]
        else:
            await ctx.channel.send("I don't know your reddit username yet, please set a username first with the `?username [name]` command")
            return
        #### Find weeknumber of last week if no argument is given
        with open('DiscordLoseitBot/Information/loseit_information.txt') as f:
            loseit_information = json.load(f)
        tracker_url = loseit_information["challenge_tracker"]
        googleSheetId = tracker_url.split('/edit')[0]
        if week == None:
            weekNumber = int(loseit_information["week"][-1])-1
            lastWeek = 'W'+str(weekNumber)
            worksheetName = lastWeek+'%20Inter'
        else:
            weekNumber = int(loseit_information["week"][-1])
            if int(week[-1]) <= weekNumber:
                worksheetName = week +'%20Inter'
                weekNumber = week[-1]
            else:
                await ctx.send('Please enter a week in the past, I cannot predict the future.')
                return
            
        #### Load sheet for the given week
        URL = '{0}/gviz/tq?tqx=out:csv&sheet={1}'.format(
            googleSheetId,
            worksheetName
        )
        df = pd.read_csv(URL)

        for column in df.columns:
            if 'username' in column:
                column_name = column
            if 'team' in column:
                team_column = column

        df['filtered_usernames'] = df[column_name].str.lower().str.strip()
        df_last = df.groupby(['filtered_usernames']).last() #Only count last entry per day
        df_team = df_last.copy().loc[df_last[team_column] == team_name] #Filter for teamname

        if len(df_team) == 0:
            return await ctx.send("I can't find any past activity data for this challenge.")
        for user, data in df_team.iterrows(): #Count all steps and minutes
            steps = [0 if math.isnan(value) else value for value in data.filter(regex='.Steps.').values]
            total_steps = sum(steps)
            df_team.loc[user.lower(),'total_steps'] = int(total_steps)


            minutes = [0 if math.isnan(value) else value for value in data.filter(regex='.Minutes.').values]
            total_minutes = sum(minutes)
            df_team.loc[user.lower(),'total_minutes'] = int(total_minutes)

        df_steps = df_team.copy().sort_values(by=['total_steps'],ascending=False)
        df_minutes = df_team.copy().sort_values(by=['total_minutes'],ascending=False)

        #### Find location in ranking for steps and minutes for user
        msg = str(ctx.message.author.display_name) + ", your ranking for week " + str(weekNumber) + ": \n"
        if username.lower() not in df_steps.index:
            msg += "- I cannot find any steps for you\n"
        else:
            your_steps = df_steps.loc[username.lower(),'total_steps']
            your_place = df_steps.index.tolist().index(username.lower())
            total_steppers = len(df_steps.index)
            msg += f'- {int(your_steps)} steps, {self.day_formatting(str(your_place+1))} out of {total_steppers} team members.\n'

        if username.lower() not in df_minutes.index:
            msg += "- I cannot find any activity minutes for you"
        else:
            your_minutes = df_minutes.loc[username.lower(),'total_minutes']
            your_place = df_minutes.index.tolist().index(username.lower())
            total_minutes = len(df_minutes.index)
            
            msg += f'- {int(your_minutes)} activity minutes, {self.day_formatting(str(your_place+1))} out of {total_minutes} team members.'
        await ctx.channel.send(msg)
        
def setup(bot):
    bot.add_cog(Challenge_Help(bot))
