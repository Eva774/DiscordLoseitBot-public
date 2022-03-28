import asyncio
import time
import typing

from discord.ext import commands
from DiscordLoseitBot.commands.GuildData import get_guild_data, GuildData
from DiscordLoseitBot.helpers.server_ids import JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID

class Notify(commands.Cog, name="Notification_lists"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.servers = [OWN_TEAM_SERVER_ID, TEST_SERVER_ID]

    @commands.command(name="sub", brief="Subscribe to one or more list(s).", usage="\u2000[list name]",
                      help="Subscribe to list(s)\n\nWithout a list name: you get an overview of all the lists with the corresponding emoji's. \nClick the emoji to subscribe to the corresponding list. \nClick the emoji again to unsubscribe from the corresponding list.\n\n With a list name: you will be subscribed to that list.")
    async def subscribe(self, ctx: commands.Context, list_name: typing.Optional[str] = None, user_id = None):
        """
        If used with list_name, subscribes the user to that list if possible.
        If used without parameter it prints the existing lists, and allows users to subscribe by adding reactions.
        :param ctx: The current context (discord.ext.commands.Context)
        :param list_name: The list to subscribe to. (optional - str - default = None)
        """
        if ctx.message.guild.id not in self.servers:
            return
        if not user_id: 
            user_id = ctx.author.id
        # Execute 'show_lists' if no parameter provided
        if not list_name:
            return await self.show_lists(ctx)

        # Make sure list is lowercase
        list_name = list_name.lower()

        guild_data = await get_guild_data(ctx.message.guild.id)

        # Error if list does not exist
        if not guild_data.does_list_exist(list_name):
            msg = "This list does not exist."
            return await ctx.send(msg)

        # Subscribe user and error if failed
        if not await guild_data.sub_user(list_name, user_id):
            msg = "<@{0}>, you are already subscribed to {1}.".format(str(user_id), list_name)
            return await ctx.send(msg)

        # Subscription successful, show result to user
        msg = "Subscribed <@{0}> to {1}.".format(str(user_id), list_name)
        await ctx.send(msg)

    @commands.command(name="unsub", brief="Unsubscribe from a list.", usage="\u2000<list name>",
                      help="Unsubscribe from a list.\n\n<list name> \u2003 The name of the list to unsubscribe from.")
    async def unsubscribe(self, ctx: commands.Context, list_name: str, user_id = None):
        """
        Unsubscribes the user from the provided list
        :param ctx: The current context. (discord.ext.commands.Context)
        :param list_name: The list to unsubscribe from. (str)
        """
        if ctx.message.guild.id not in self.servers:
            return
        if not user_id:
            user_id = ctx.author.id
        # make sure list is lowercase
        list_name = list_name.lower()

        guild_data = await get_guild_data(ctx.message.guild.id)

        # Error if list does not exist
        if not guild_data.does_list_exist(list_name):
            msg = "This list does not exist."
            return await ctx.send(msg)

        # Unsubscribe user and error if failed
        if not await guild_data.unsub_user(list_name, user_id):
            msg = "<@{0}>, you are not subscribed to {1}.".format(str(user_id), list_name)
            return await ctx.send(msg)

        # Unsubscribe successful, show result to user
        msg = "Unsubscribed <@{0}> from {1}.".format(str(user_id), list_name)
        await ctx.send(msg)

    @commands.command(name="notify", usage="\u2000<list name>", brief="Notify a list.", 
        help="Notify a list.\n\n<list name> \u2003 The name of the list to notify.")
    async def notify(self, ctx: commands.Context, list_name: str, *, message: typing.Optional[str] = None):
        """
        Notify all subscribers for the given list with the given message.
        :param ctx:The current context. (discord.ext.commands.Context)
        :param list_name: The name of the list to notify. (str)
        :param message: The message to send with the notification. (optional - str - default= None)
        """
        if ctx.message.guild.id not in self.servers:
            return
        guild_data = await get_guild_data(ctx.message.guild.id)

        # Error if list does not exist
        if not guild_data.does_list_exist(list_name):
            msg = "This list does not exist."
            return await ctx.send(msg)

        # Fetch users to notify
        users = guild_data.get_users_list(list_name)

        # Error if no users were found
        if len(users) < 1:
            msg = "Nobody to notify."
            return await ctx.send(msg)

        # build users mentioning string
        user_tags = []
        for user_id in users:
            user_tags.append(f'<@{str(user_id)}>')

        users_str = ', '.join(user_tags)

        # Setup the announcement with the subject and caller
        message_text = "**{0}** Notified by <@{1}>\n".format(list_name.capitalize(), ctx.message.author.id)

        # append the message if provided
        if message:
            second_line = "With message: {0}".format(message) + '\n'
            message_text += second_line

        await ctx.send(message_text + '\n' + users_str)

    async def wait_for_added_reactions(self, ctx: commands.Context, msg_id: int, guild_data: GuildData,
                                       timeout: int = 300):
        """
        Wait for new reactions on the provided message.
        :param ctx: The current context. (discord.ext.commands.Context)
        :param msg_id: The Id of the message for which we register reactions. (int)
        :param guild_data: The data of the current guild (GuildData)
        :param timeout: The amount of seconds we wish to wait. (int)
        """
        end_time = time.time() + timeout
        while True:
            try:
                reaction, user = await ctx.bot.wait_for(
                    "reaction_add",
                    check=lambda emoji, author: emoji.message.id == msg_id and not author.bot,
                    timeout=30.0,
                )

                if reaction.custom_emoji:
                    reaction_emoji = str(reaction.emoji.id)
                else:
                    reaction_emoji = reaction.emoji

                for key, v in guild_data.notification_lists.items():
                    if reaction_emoji == v["emoji"]:
                        list_name = key
                        await self.subscribe(ctx, list_name,user.id)

            except asyncio.TimeoutError:
                pass

            if time.time() > end_time:
                break

    async def wait_for_removed_reactions(self, ctx: commands.Context, msg_id: int, guild_data: GuildData,
                                         timeout: int = 300):
        """
        Wait for removed reactions on the provided message.
        :param ctx: The current context. (discord.ext.commands.Context)
        :param msg_id: The Id of the message for which we register removed reactions. (int)
        :param guild_data: The data of the current guild (GuildData)
        :param timeout: The amount of seconds we wish to wait. (int)
        """
        end_time = time.time() + timeout
        while True:
            try:
                reaction, user = await ctx.bot.wait_for(
                    "reaction_remove",
                    check=lambda emoji, author: emoji.message.id == msg_id and not author.bot,
                    timeout=30.0,
                )
                if reaction.custom_emoji:
                    reaction_emoji = str(reaction.emoji.id)
                else:
                    reaction_emoji = reaction.emoji
                for key, v in guild_data.notification_lists.items():

                    if reaction_emoji == v["emoji"]:
                        list_name = key
                        await self.unsubscribe(ctx, list_name,user.id)

            except asyncio.TimeoutError:
                pass

            if time.time() > end_time:
                break

    @commands.command(name="show_lists", brief="Show all the existing lists.", 
        help="Show all the lists with the corresponding emoji's. \nClick the emoji to subscribe to the specific list. \nClick the emoji again to unsubscribe from the specific list.")
    async def show_lists(self, ctx: commands.Context):
        """
        Show all currently existing lists for this server
        :param ctx: The current context. (discord.ext.commands.Context)
        """
        if ctx.message.guild.id not in self.servers:
            return
        guild_data = await get_guild_data(ctx.message.guild.id)

        # Error if no lists exist yet
        if not guild_data.notification_lists:
            msg = "No list exist yet."
            return await ctx.send(msg)

        # Init text with title
        text = "Lists:\n"

        # Loop and append all lists
        for list_name, list_data in sorted(guild_data.notification_lists.items()):
            if list_data["is_custom_emoji"]:
                text += get_custom_emoji(ctx, int(list_data["emoji"]))
            else:
                text += list_data["emoji"]

            text += " - " + list_name + "\n"

        # Send lists to context
        msg = await ctx.send(text)

        # Add reactions
        for list_data in guild_data.notification_lists.values():
            await msg.add_reaction(
                list_data["emoji"] if not list_data["is_custom_emoji"] else ctx.bot.get_emoji(int(list_data["emoji"])))

        # Setup listeners
        # TODO make reaction time configurable
        timeout = 60 * 5  # 5 minutes
        reaction_added_task = asyncio.create_task(
            self.wait_for_added_reactions(ctx, msg.id, guild_data, timeout))
        reaction_removed_task = asyncio.create_task(
            self.wait_for_removed_reactions(ctx, msg.id, guild_data, timeout))

        # Listen for reactions
        await reaction_added_task
        await reaction_removed_task

        # Delete message
        await msg.delete()

    @commands.command(name="my_lists", help="Get an overview of the lists you are subscribed to.")
    async def my_lists(self, ctx: commands.Context):
        """
        Show the lists the current user is subscribed to.
        :param ctx: The current context. (discord.ext.commands.Context)
        """
        if ctx.message.guild.id not in self.servers:
            return
        guild_data = await get_guild_data(ctx.message.guild.id)
        subbed_lists = []

        # Error if no lists exist yet
        if not guild_data.notification_lists:
            msg = "No lists exist yet."
            return await ctx.send(msg)

        # Fetch the lists the author is subscribed to
        for list_name, list_data in guild_data.notification_lists.items():
            if ctx.author.id in list_data["users"]:
                subbed_lists.append(list_name)

        # Error if the author is not subscribed to any lists
        if len(subbed_lists) < 1:
            msg = "You are not subscribed to any lists."
            return await ctx.send(msg)

        # Show the user his lists
        msg = "You are subscribed to:" + "\n - " + "\n - ".join(sorted(subbed_lists))
        await ctx.send(msg)

    @commands.command(name="add_list", brief="**admin-only** \n \u2003 Add a new list.", usage="\u2000<list name>",
                      help="*admin-only* \u2003 Add a new list.\nYou will be asked what emoji to use for this list. React to the question of the bot with an emoji that is not yet used for another list. \n\n <list name> \u2003 The name of the list to add.")
    async def add_list(self, ctx: commands.Context, list_name: str):
        """
        Adds a new notification list with the given name.
        :param ctx: The current context. (discord.ext.commands.Context)
        :param list_name: The name to be used for the list. (str)
        """
        if ctx.message.guild.id not in self.servers:
            return
        guild_data = await get_guild_data(ctx.message.guild.id)

        # Error if not admin
        if not ctx.message.author.guild_permissions.administrator:
            gif = "Only admins can do this"
            return await ctx.send(gif)

        # Make sure the list name is lowercase
        list_name = list_name.lower()

        # Error if list already exists
        if guild_data.does_list_exist(list_name):
            msg = "{0} already exists.".format(list_name)
            return await ctx.send(msg)

        # Request emoji from user
        msg = await ctx.send("What emoji do you want to use for " + list_name + " ?")

        # Handle user reaction
        try:
            reaction, user = await ctx.bot.wait_for(
                "reaction_add",
                check=lambda emoji, author: emoji.message.id == msg.id and author == ctx.message.author,
                timeout=30.0,
            )

            # Process emoji
            if reaction.custom_emoji:
                try:
                    reaction_emoji = reaction.emoji.id
                    emoji_to_print = get_custom_emoji(ctx, reaction_emoji)
                    custom_emoji = True
                except AttributeError:
                    msg = "Emoji not recognized. Try again with a standard emoji or a custom emoji from this server."
                    return await ctx.send(msg)
            else:
                reaction_emoji = reaction.emoji
                emoji_to_print = str(reaction_emoji)
                custom_emoji = False

            # Error if emoji is being used already on this server
            for data in guild_data.notification_lists.values():
                if reaction_emoji == data["emoji"]:
                    msg = "This emoji is already used for a list."
                    return await ctx.send(msg)

            # Add list to GuildData
            await guild_data.add_notification_list(list_name, reaction_emoji, custom_emoji)

            # Show success message to user
            await ctx.send("The list `" + list_name + "` is saved with the emoji " + emoji_to_print)

        # Handle timeout
        except asyncio.TimeoutError:
            await msg.delete()
            msg = "You snooze, you lose!"
            return await ctx.send(msg)

    @commands.command(name="remove_list", brief="**admin-only**\n\u2003 Remove a list.", usage="\u2000<list name>",
                      help="*admin-only* \u2003 Remove a list.\n\n<list name> \u2003 The name of the list to remove.")
    async def remove_list(self, ctx: commands.Context, list_name: str):
        """
        Removes the given list.
        :param ctx: The current contest. (discord.ext.commands.Context)
        :param list_name: The list to be removed. (str)
        """
        if ctx.message.guild.id not in self.servers:
            return
        thumbs_up = "👍"
        thumbs_down = "👎"
        guild_data = await get_guild_data(ctx.message.guild.id)

        # Error if not admin
        if not ctx.message.author.guild_permissions.administrator:
            gif = "Only admins can do this."
            return await ctx.send(gif)

        # Make sure the list name is lowercase
        list_name = list_name.lower()

        # Error if list does not exist
        if not guild_data.does_list_exist(list_name):
            msg = "This list does not exist."
            return await ctx.send(msg)

        # Ask user confirmation
        msg = "Are you sure?"
        confirmation_ref = await ctx.send(msg)
        await confirmation_ref.add_reaction(thumbs_up)
        await confirmation_ref.add_reaction(thumbs_down)

        # Handle user reaction
        try:
            reaction, user = await ctx.bot.wait_for(
                "reaction_add",
                check=lambda emoji, author: emoji.message.id == confirmation_ref.id and author == ctx.message.author,
                timeout=30.0,
            )

            # Process emoji
            if reaction.emoji == thumbs_up:
                await guild_data.remove_notification_list(list_name)
                msg = "The list {0} was removed.".format(list_name)
                await ctx.send(msg)

            elif reaction.emoji == thumbs_down:
                msg = "{0} won't be removed.".format(list_name)
                await ctx.send(msg)

            # Delete message
            await confirmation_ref.delete()

        # Handle Timeout
        except asyncio.TimeoutError:
            await confirmation_ref.delete()
            msg = "You snooze, you lose!"
            return await ctx.send(msg)


def setup(bot: commands.Bot):
    bot.add_cog(Notify(bot))
