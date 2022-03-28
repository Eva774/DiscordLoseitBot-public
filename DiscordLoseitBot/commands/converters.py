from discord.ext import commands
from DiscordLoseitBot.helpers.server_ids import JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID, PIRATE_KATIE

class Converters(commands.Cog, name='converters'):
    def __init__(self, bot):
        self.bot = bot
        self.servers = [JOSH_SERVER_ID, OWN_TEAM_SERVER_ID, TEST_SERVER_ID,LOSEIT_SERVER_ID, PIRATE_KATIE]
    @commands.command(name='ctof',brief='Convert degrees Celsius to Fahrenheit', usage=' <C>',help='<C>\u2003 The degrees in Celsius to convert')
    async def ctof(self,ctx,c_str):
        '''
        Converts C to F. Enter !ctof 28. Do not enter units.
        '''
        if ctx.message.guild.id not in self.servers:
            return
        try:
            c_value = float(c_str)
        except:
            return
        f_val = int((c_value * 9 /5 + 32)*100)/100
        message = str(c_value) + " deg C is " + str(f_val) + " deg F."
        await ctx.channel.send(message)

    @commands.command(name='ftoc',brief='Convert degrees Fahrenheit to Celsius', usage=' <F>',help='<F> \u2003 The degrees in Fahrenheit to convert')
    async def ftoc(self,ctx,f_str):
        '''
        Converts F to C. Enter !ftoc 98. Do not enter units.
        '''
        if ctx.message.guild.id not in self.servers:
            return
        try:
            f_value = float(f_str)
        except:
            return
        c_val = int(((f_value- 32)* 5/9)*100)/100
        message = str(f_value) + " deg F is " + str(c_val) + " deg C."
        await ctx.channel.send(message)

    @commands.command(name='lbstokg',brief='Convert weight in lbs to kg', usage=' <lbs>',help='<lbs> \u2003 The weight in lbs to convert')
    async def lbstokg(self,ctx,lbs_weight_str):
        '''
        Converts lbs to kgs. Enter !lbstokgs Value. ex !lbstokgs 98. Do not enter units.
        '''
        if ctx.message.guild.id not in self.servers:
            return
        try:
            lbs_weight = float(lbs_weight_str)
        except:
            return
        lbs_weight_rounded = int(lbs_weight*100)/100
        kgs_weight = int(lbs_weight / 2.205 * 100) / 100
        message = str(lbs_weight_rounded) + " lbs is " + str(kgs_weight) + " kgs."
        await ctx.channel.send(message)

    @commands.command(name='kgtolbs',brief='Convert weight in kg to lbs', usage=' <kg>',help='<kg> \u2003 The weight in kg to convert')
    async def kgtolbs(self,ctx,kgs_weight_str):
        '''
        Converts kgs to lbs.ex "!kgstolbs 98". Enter !kgstolbs Value. Do not enter units.
        '''
        if ctx.message.guild.id not in self.servers:
            return
        try:
            kgs_weight = float(kgs_weight_str)
        except:
            return
        kgs_weight_rounded = int(kgs_weight*100)/100
        lbs_weight = int(kgs_weight * 2.205 * 100) / 100
        message = str(kgs_weight_rounded) + " kgs is " + str(lbs_weight) + " lbs."
        await ctx.channel.send(message)

    @commands.command(name='meterstoft',brief='Convert length in feet and inches to meters', usage=' <ft>  <inches>',help='<ft> \u2003 The length in feet to convert \n<inches> \u2003 The length in inches to convert')
    async def meterstoft(self,ctx,meters_str):
        '''
        Converts meters to ft and inches. ex "!meterstoft 1.5". Enter !meterstoft Value. Do not enter units.
        '''
        if ctx.message.guild.id not in self.servers:
            return
        try:
            meters = float(meters_str)
        except:
            return
        meters_in_ft = meters // .3048
        meters_in_in = int(((meters / .3048) % 12)*100)/100
        message = str(meters) +" meters is " + str(meters_in_ft)+ " feet and "+ str(meters_in_in)+ " inches."
        await ctx.channel.send(message)

    @commands.command(name='fttometers',brief='Convert length in meters to feet and inches', usage=' <ft> [inches]',help=' <ft> [inches]\u2003 The length in feet and inchess to convert')
    async def fttometers(self,ctx,feet_str,inches_str = 0):
        '''
        Converts meters to ft & inc.ex "!meterstoft 5 4". Enter !meterstoft Feet_Value Inches_Value. This means 5ft 4inches Do not enter units.
        '''
        if ctx.message.guild.id not in self.servers:
            return
        try:
            feet = float(feet_str)
            inches = float(inches_str)
        except:
            return
        meters=  (feet + inches/12)* .3048
        rounded_meters = int(meters*100)/100
        message = str(feet)+ " feet and "+ str(inches)+ " inches is "+str(rounded_meters)+" meters."
        await ctx.channel.send(message)

    @commands.command(name='kmtomiles',brief='Convert distance in kilometers to miles', usage=' <km>',help='<km> \u2003 The distance in kilometers to convert')
    async def kmtomiles(self,ctx,km_value):
        '''
        Converts meters to km. ex "!milestokm 3.5". Enter !meterstoft miles_value. Do not enter units.
        '''

        if ctx.message.guild.id not in self.servers:
            return
        try:
            km = float(km_value)
        except:
            return
        miles=  km / 1.60934
        rounded_miles = int(miles*100)/100
        message = str(km)+ " km is "+str(rounded_miles)+"  miles."
        await ctx.channel.send(message)
    @commands.command(name='milestokm',brief='Convert distance in miles to kilometers', usage=' <miles>',help='<miles> \u2003 The distance in to convert')
    async def milestokm(self,ctx,miles_value):
        '''
        Converts km to meters. ex "!kmtomiles 3.5". Enter !kmtomiles kilometer_value. Do not enter units.
        '''
        if ctx.message.guild.id not in self.servers:
            return
        try:
            miles = float(miles_value)
        except:
            return
        kmeter=  miles * 1.60934
        rounded_kmeters = int(kmeter*100)/100
        message = str(miles)+ " miles is "+str(rounded_kmeters)+"  km."
        await ctx.channel.send(message)

def setup(bot):
    bot.add_cog(Converters(bot))
