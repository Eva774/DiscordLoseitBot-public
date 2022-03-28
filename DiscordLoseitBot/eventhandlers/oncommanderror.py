from discord.ext import commands
import discord
from DiscordLoseitBot.helpers.server_ids import JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID

class OnCommandError(commands.Cog, name="on_command_error"):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.servers = [JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID]
    @commands.Cog.listener(name="on_command_error")
    async def on_command_error(self, ctx: commands.Context, error):
        command_name = ctx.message.content.split(' ')[0][1:]
        command_exists = False
        command_given = command_name
        for command in ctx.bot.commands:
            if command.name == command_name or command_name in command.aliases:
                command_exists = True
                command_given = self.bot.get_command(command_name).name


        if isinstance(error, commands.MissingRequiredArgument):
            arg_name = error.param.name
            print('Missing argument {0} for command {1}, given by {2} in {3}'.format(
                arg_name,
                command_name,
                ctx.message.author.name,
                ctx.message.guild.name))

            for command in self.bot.commands:
                if command.name == command_given:
                    msg = "My command `" + command_name + "` requires more arguments. Let me give you some help!"
                    await ctx.send(msg)
                    if command.usage == None:
                        msg = '```{0} \n\n{1}```'.format(command_name,command.help)
                    else:
                        msg = '```{0} {1} \n\n{2}```'.format(command_name,command.usage,command.help)
        elif isinstance(error, commands.CommandNotFound):
            if command_name[0] == self.bot.command_prefix or command_name[0] == ' ':
                return
            msg = "I don't know this command, use ?help to get an overview of my commands"
            print('Command {0} not found, by {1} in {2}'.format(
                command_name,
                ctx.message.author.name,
                ctx.message.guild.name))
        elif command_exists:
            msg = "This command should work, I don't know why it is not working. My owner will look into it"
            print('Command {0}, unknown error'.format(command_name))
            with open('errors.log','a') as file:
                file.write('\n'+command_name+"\t"+repr(error))

        else:
            msg = "Sorry, I don't understand what you're saying. Use ?help to get an overview of my commands"

        await ctx.send(msg)

def setup(bot):
    bot.add_cog(OnCommandError(bot))
