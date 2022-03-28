import discord
from discord.ext import commands
from DiscordLoseitBot.helpers.server_ids import JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID


class OnMemberJoin(commands.Cog, name="on_member_join"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.servers = [JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID]

    @commands.Cog.listener(name="on_member_join")
    async def on_member_join(self, member: discord.Member):
        """
        This function is executed on every member_join event, and logs a message if a certain threshold is passed.
        :param member: The member that just joined. (discord.Member)
        """
        # Fetch server
        guild = member.guild

        channel = self.bot.get_channel(793210131411632139)
        #Get user ID
        user_id = member.id

        # kick_ids = [420644819975798785,342123353261211659,342123353261211659,
                    # 627505961749315607,799586879842156554]
        kick_ids = [753340370733105232,799586879842156554]
        guild_ids = [713718109956997191,793209249073070101,661630998945071204]
        if guild.id in guild_ids and user_id in kick_ids:
            await channel.send('I have kicked {0} from {1}'.format(member.name, member.guild.name))
            await guild.kick(member)
        return

def setup(bot: commands.Bot):
    bot.add_cog(OnMemberJoin(bot))
