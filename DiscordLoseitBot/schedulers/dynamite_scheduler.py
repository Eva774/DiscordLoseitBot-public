import os
import discord
import requests
import time
import random

from datetime import datetime, timedelta
from discord.ext import tasks

from DiscordLoseitBot.commands.GuildData import get_all_guilds_data, GuildData
#### Checks every minute if there are some expired dynamites


# TODO make interval configurable
@tasks.loop(minutes = 1.0)
async def check_dynamites(bot):
    explosion_gifs = ['http://gph.is/2gT3q91',
    'https://gph.is/g/EGKQPn3',
    'https://gph.is/g/ZrKwVXj',
    'http://gph.is/1d05zS0',
    'http://gph.is/1EnmySv',
    'https://gph.is/2JOpmfQ',
    'http://gph.is/1s201Ez',
    'http://gph.is/2vzX29Y',
    'http://gph.is/2oPwG14',
    'http://gph.is/1hCyLnQ',
    'http://gph.is/2bU0VAZ',
    'http://gph.is/2c5wbNX',
    'http://gph.is/2db0DTd',
    'https://gph.is/g/4zqOG20',
    'http://gph.is/1VEHJY8',
    'http://gph.is/2bahbul']

    guilds_data = await get_all_guilds_data()

    for guild_data in guilds_data: #For all guilds
        current_dynamites = guild_data.dynamites #Get all dynamites
        for timestamp in current_dynamites.copy(): #Go through timestamps
            detonation_time = datetime.fromtimestamp(int(timestamp)) #Convert to datetime
            time_to_spare = detonation_time - datetime.now() #Compute timeleft
            if time_to_spare.total_seconds() < 0: #If no timeleft
                users = current_dynamites[str(timestamp)] #Get users
                await guild_data.remove_dynamite(str(timestamp),0) #Remove from guild data
                msg = f'<@{users[0]}>'

                if len(users) > 2: 
                    for user_id in users[1:-1]:
                        msg += f', <@{user_id}>'
                
                if len(users) > 1:
                    msg += f', and <@{users[-1]}>' 

                msg += ' you were too late!'

                guild = bot.get_guild(guild_data.guild_id)
                channel = guild.get_channel(int(guild_data.bot_channel))

                await channel.send(f'{msg}')
                await channel.send(random.choice(explosion_gifs))



            

def check(message):
    return not message.pinned
