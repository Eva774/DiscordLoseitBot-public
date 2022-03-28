from discord.ext import commands


from DiscordLoseitBot.helpers.server_ids import JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID, ALLIE_TEAM_ID
from DiscordLoseitBot.helpers.server_ids import STAYCATION, ROAD_TRIP

class Fun(commands.Cog, name='fun'):
    def __init__(self, bot):
    
        self.bot = bot
        self.servers = [JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID,ALLIE_TEAM_ID, STAYCATION, ROAD_TRIP]
    
    @commands.command(name='rainbows',help='You know which gif ;)')
    async def rainbows(self,ctx):
        '''
        rainbows
        '''
        msg = "https://tenor.com/view/rainbow-gif-8764636"
        await ctx.channel.send(msg)


    @commands.command(name='rooting',help='You know which gif ;)')
    async def rooting(self,ctx):
        '''
        I'm rooting for you patrick
        '''
        msg = "https://tenor.com/view/spongebob-squarepants-patrick-star-im-rooting-for-you-cheer-cheering-gif-5104276"
        await ctx.channel.send(msg)



    @commands.command(name='spaceelmo',help='You know which gif ;)')
    async def spaceelmo(self,ctx):
        '''
        space elmo
        '''
        msg = "https://tenor.com/view/elmo-dancing-space-gif-13040423"
        await ctx.channel.send(msg)

    @commands.command(name='elmorage',help='You know which gif ;)')
    async def elmorage(self,ctx):
        '''
        space elmo
        '''
        msg = "https://giphy.com/gifs/i-did-a-thing-e5kbmb3wX3J1S"
        await ctx.channel.send(msg)

    @commands.command(name='welcometotheclub',help='You know which gif ;)')
    async def welcometotheclub(self,ctx):
        '''
        welcome to the club
        '''
        msg = "https://media.tenor.com/images/1c43814df5a461b7dbaf95682992e25d/tenor.gif"
        await ctx.channel.send(msg)

    @commands.command(name='stabbystab',help='You know which gif ;)')
    async def stabbystab(self,ctx):
        '''
        BEST GIF  from imgur
        '''
        msg = "https://imgur.com/0HW9DAD"
        await ctx.channel.send(msg)

    @commands.command(name='whalehello',help='You know which gif ;)')
    async def whalehello(self,ctx):
        '''
        Whale hello there gif
        '''
        msg = "https://tenor.com/view/whale-hellothere-hello-hi-hey-gif-4505186"
        await ctx.channel.send(msg)


    @commands.command(name='title',help='You know which gif ;)')
    async def title(self,ctx):
        '''
        Title of your sex tape
        '''
        msg = "https://tenor.com/view/title-of-your-sex-tape-jake-peralta-brooklyn-nine-nine-andy-samberg-nbc-gif-13615436"
        await ctx.channel.send(msg)

    @commands.command(name='zerodays',help='Reddit link to the non-zero days post')
    async def zerodays(self,ctx):
        '''
        No zero days reddit post
        '''
        msg = "https://www.reddit.com/r/getdisciplined/comments/1q96b5/i_just_dont_care_about_myself/cdah4af/"
        await ctx.channel.send(msg)

    @commands.command(name='hydrate',help='Image to remind people to hydrate')
    async def hydrate(self,ctx):
        '''
        Benefits of staying hydrated
        '''
        msg = "https://pics.awwmemes.com/nutrition-fact-if-you-drink-a-gallon-of-water-per-45080823.png"
        await ctx.channel.send(msg)

def setup(bot):
    bot.add_cog(Fun(bot))
