import os
import discord
from discord.ext import commands
import datetime

from DiscordLoseitBot.bot.DiscordLoseitBot import LoseitBot
from DiscordLoseitBot.schedulers.dynamite_scheduler import check_dynamites
from DiscordLoseitBot.schedulers.log_reminder import log_reminder

from dotenv import load_dotenv
#### All the different modules are listed here
cogs = ['DiscordLoseitBot.eventhandlers.onready',
        'DiscordLoseitBot.eventhandlers.oncommanderror',
        'DiscordLoseitBot.eventhandlers.onmemberjoin',
        
        'DiscordLoseitBot.commands.bot_info',
        'DiscordLoseitBot.commands.challenge_help',
        'DiscordLoseitBot.commands.converters',
        'DiscordLoseitBot.commands.discord_help',
        'DiscordLoseitBot.commands.dynamite',
        
        'DiscordLoseitBot.commands.fun',
        'DiscordLoseitBot.commands.relay', 
        'DiscordLoseitBot.commands.superrelay',
        'DiscordLoseitBot.commands.notify',
        'DiscordLoseitBot.commands.log_reminders']

#Get info from env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('PREFIX')

intents = discord.Intents.all()

bot = LoseitBot(PREFIX, intents)
bot.remove_command('help') #Remove default help because we have our own

#Load all modules
for cog in cogs:
    bot.load_extension(cog)

#Start scheduled tasks
@bot.event
async def on_ready():
    check_dynamites.start(bot)
    # log_reminder.start(bot) #Uncomment for log reminders

bot.run(TOKEN)
