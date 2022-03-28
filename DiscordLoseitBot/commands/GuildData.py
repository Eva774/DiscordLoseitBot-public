import json
from os import path, listdir, makedirs
from datetime import datetime, tzinfo
from pytz import timezone

from discord import Member
from typing import List

_configFolder = "GuildConfigs"
_guildConfigCache = dict()

if not path.exists(_configFolder):
    makedirs(_configFolder)

class GuildData:
    guild_id: int
    team_name: str
    notification_lists: dict
    usernames: dict
    baton: int
    past_batons: dict
    superbaton: int
    past_superbatons: dict
    dynamites: dict
    past_dynamites: dict
    bot_channel: int
    no_reminders: list

    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.notification_lists = dict()
        self.team_name = ""
        self.usernames = dict()
        self.baton = 756269222459473970
        self.past_batons = dict()
        self.superbaton = 756269222459473970
        self.past_superbatons = dict()
        self.dynamites = dict()
        self.past_dynamites = dict()
        self.bot_channel = 761262465404108852
        self.no_reminders = []

    async def sub_user(self, list_name: str, user_id: int) -> bool:
        """
        Adds a user to the list if not already there.
        :param list_name: The list to add the user to. (str)
        :param user_id: The user to add to the list. (int)
        :return: True if added successfully, False if already in list. (bool)
        """
        user_list = self.notification_lists[list_name]["users"]

        if user_id not in user_list:
            # user not in list, add to list and return True
            user_list.append(user_id)
            await self.save()
            return True

        else:
            # user already in list, return false
            return False

    async def unsub_user(self, list_name: str, user_id: int) -> bool:
        """
        Removes a user from the list
        :param list_name: The list to remove the user from. (str)
        :param user_id: The user to remove from the list. (str)
        :returns: True if the user is successfully removed, False if the user is not on the list. (bool)
        """
        user_list = self.notification_lists[list_name]["users"]

        if user_id in user_list:
            # user exists in list, remove and return True
            user_list.remove(user_id)
            await self.save()
            return True
        else:
            # user does not exist in list, return False
            return False

    def get_users_list(self, list_name: str) -> List[str]:
        """
        Return all users who subscribed to the given list
        :param list_name: The list to fetch. (str)
        :return: A list with the id of all users who subscribed to the given list. (list[str])
        """
        return self.notification_lists[list_name]["users"]

    def does_list_exist(self, list_name: str) -> bool:
        """
        Checks whether or not a list exists.
        :param list_name: The name of the list to check. (str)
        :return: True if the list exists, False if it doesn't. (bool)
        """
        return list_name in self.notification_lists.keys()

    async def add_notification_list(self, list_name: str, emoji, custom_emoji: bool):
        """
        Adds a new notification list.
        :param list_name: The name of the list to add. (str)
        :param emoji: The emoji to be used for the list. (any)
        :param custom_emoji: Whether or not we're using a custom emoji. (bool)
        """
        self.notification_lists[list_name] = {
            "emoji": emoji,
            "is_custom_emoji": custom_emoji,
            "users": [],
        }
        await self.save()

    async def remove_notification_list(self, list_name: str):
        """
        Removes a notification list.
        :param list_name: The list to be removed. (str)
        """
        if list_name in self.notification_lists.keys():
            del self.notification_lists[list_name]
            await self.save()


    async def get_username(self, user_id: int):
        """
        Removes a notification list.
        :param user_id: The id of the user to add (int)
        """
        return self.usernames.get(str(user_id),None)

    async def add_username(self, user_id: int, user_name: str):
        """
        Removes a notification list.
        :param user_id: The id of the user to add (int)
        :param user_name: Name of the user to add (str)
        """
        self.usernames[str(user_id)] = user_name
        await self.save()

    async def add_teamname(self, team_name: str):
        """
        Removes a notification list.
        ;param team_name: Name of the user to add (str)
        """
        self.team_name = team_name
        await self.save()

    async def pass_baton(self, baton: int):
        """
        Removes a notification list.
        ;param team_name: Name of the user to add (str)
        """
        weeknumber = int(datetime.now(timezone('US/Eastern')).strftime('%W'))
        if str(weeknumber) not in self.past_batons.keys():
            self.past_batons[str(weeknumber)] = dict()
        if str(self.baton) not in self.past_batons[str(weeknumber)].keys():
            self.past_batons[str(weeknumber)][str(self.baton)] = 0

        self.past_batons[str(weeknumber)][str(self.baton)] += 1
        self.baton = baton

        await self.save()

    async def pass_superbaton(self, superbaton: int):
        """
        Removes a notification list.
        ;param team_name: Name of the user to add (str)
        """
        if superbaton != None:
            weeknumber = int(datetime.now(timezone('US/Eastern')).strftime('%W'))
            if str(weeknumber) not in self.past_superbatons.keys():
                self.past_superbatons[str(weeknumber)] = dict()
            if str(self.superbaton) not in self.past_superbatons[str(weeknumber)].keys():
                self.past_superbatons[str(weeknumber)][str(self.superbaton)] = 0

            self.past_superbatons[str(weeknumber)][str(self.superbaton)] += 1
        self.superbaton = superbaton
        await self.save()

    async def toss_dynamite(self, time:int, recipients:list):

        self.dynamites[str(time)] = recipients
        await self.save()

    async def remove_dynamite(self,timestamp:str,user_id:int):
        if user_id != 0:
            weeknumber = int(datetime.now(timezone('US/Eastern')).strftime('%W'))
            if str(weeknumber) not in self.past_dynamites.keys():
                self.past_dynamites[str(weeknumber)] = dict()
            if str(user_id) not in self.past_dynamites[str(weeknumber)].keys():
                self.past_dynamites[str(weeknumber)][str(user_id)] = 0

            self.past_dynamites[str(weeknumber)][str(user_id)] += 1
        del self.dynamites[str(timestamp)]
        await self.save()

    async def add_bot_channel(self, channel:int):
        self.bot_channel = channel
        await self.save()

    async def add_no_reminder(self, user_id:int):
        if str(user_id) not in self.no_reminders:
            self.no_reminders.append(str(user_id))
        await self.save()

    async def remove_no_reminder (self,user_id: int):
        if str(user_id) in self.no_reminders:
            self.no_reminders.remove(str(user_id))
        await self.save()
        
    async def save(self):
        """
        Saves the current data to storage
        """
        await self.__write_file()

    async def __write_file(self):
        """
        Write data to file
        """
        # TODO: Actually make this async
        with open(get_config_file_path(self.guild_id), "w+") as config:
            json.dump(self.__dict__, config, indent=4, sort_keys=True)

async def get_all_guilds_data() -> [GuildData]:
    """
    Retrieves the guild data for all guilds.
    :returns: List of GuildData objects ([GuildData])
    """
    guilds_data = []
    for file in listdir(_configFolder):
        split_file = path.splitext(file)
        if split_file[1] == ".json":
            guild_data = await get_guild_data(int(split_file[0]))
            guilds_data.append(guild_data)
    return guilds_data


async def get_guild_data(guild_id: int) -> GuildData:
    """
    Retrieves the guild data for the given guild id.
    If possible it will be fetched from the cache, otherwise it will be loaded from the json file
    :param guild_id: Guild id (int)
    :returns:GuildData object (GuildData)
    """

    # check if memory cache contains server config
    if guild_id in _guildConfigCache.keys():
        return _guildConfigCache[guild_id]

    # check if server config file exists
    fileName = get_config_file_path(guild_id)

    if path.exists(fileName):
        # Load data
        config = await __read_file(guild_id, fileName)
    else:
        # Init new instance of ServerData
        config = GuildData(guild_id)

    _guildConfigCache[guild_id] = config
    return config


async def __read_file(guild_id: int, filename: str) -> GuildData:
    """
    Read the given json file and parse it to a GuildData object
    :param guild_id: Guild Id (int)
    :param filename: The name of the file to open (str)
    :returns: GuildData object (GuildData)
    """
    # TODO: Actually make this async
    with open(filename) as config:
        data = json.load(config)

        guildData = GuildData(guild_id)

        guildData.notification_lists = data.get("notification_lists", [])
        guildData.team_name = data.get("team_name", "")
        guildData.usernames = data.get("usernames", dict())
        guildData.baton = data.get("baton",756269222459473970)
        guildData.past_batons = data.get("past_batons",dict())
        guildData.superbaton = data.get("superbaton",756269222459473970)
        guildData.past_superbatons = data.get("past_superbatons",dict())
        guildData.dynamites = data.get("dynamites",dict())
        guildData.past_dynamites = data.get("past_dynamites",dict())
        guildData.bot_channel = data.get("bot_channel",761262465404108852)
        guildData.no_reminders = data.get("no_reminders",[])
        return guildData


def get_config_file_path(guild_id: int) -> str:
    """
    Get the path for the save file for the given guild id
    :param guild_id: Guild Id (int)
    :return: filepath (str)
    """
    return path.join(_configFolder, str(guild_id) + ".json")
