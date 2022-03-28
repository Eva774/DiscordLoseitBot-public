# DiscordLoseitBot-public

## .env file
Make an .env file in the parent directory with credentials and the prefix in the format of

```
TOKEN =  xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PREFIX = "#"
```

## Server ID's
In the `DiscordLoseitBot/helpers` directory, make a file called `servers_id.py` with a variable for each server where the bot needs to run.

In each of the files in the `DiscordLoseitBot/commands` directory, import the necessary ID variables and add them to the self.servers list at the top.

## Running the bot
Install python3 with the following modules:
- discord.py
- python-dotenv
- requests
- beautifulsoup4 
- pandas
- numpy
- os
- datetime


Then run `python -m DiscordLoseitBot` to start the bot.
