from discord.ext.commands import Bot
from discord import Intents
from DiscordLoseitBot.eventhandlers.onmessage import on_message

class LoseitBot(Bot):
    def __init__(self, prefix:str, intents: Intents):
        self.prefix = prefix
        super().__init__(command_prefix=self.prefix,intents = intents, case_insensitive = True,help_command = None)
    

    async def on_message(self, message):
        await on_message(self,message)
