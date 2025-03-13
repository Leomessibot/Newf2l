import datetime
import motor.motor_asyncio


class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.bannedList = self.db.bannedList
        self.channels = self.db.channels  # Collection for storing approved channels

    def new_user(self, id):
        return dict(
            id=id,
            join_date=datetime.date.today().isoformat()
        )

    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)

    async def add_user_pass(self, id, ag_pass):
        await self.add_user(int(id))
        await self.col.update_one({'id': int(id)}, {'$set': {'ag_p': ag_pass}})

    async def get_user_pass(self, id):
        user_pass = await self.col.find_one({'id': int(id)})
        return user_pass.get("ag_p", None) if user_pass else None

    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return True if user else False

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def ban_user(self, user_id):
        user = await self.bannedList.find_one({'banId': int(user_id)})
        if user:
            return False
        else:
            await self.bannedList.insert_one({'banId': int(user_id)})
            return True

    async def is_banned(self, user_id):
        user = await self.bannedList.find_one({'banId': int(user_id)})
        return True if user else False

    async def is_unbanned(self, user_id):
        try:
            if await self.bannedList.find_one({'banId': int(user_id)}):
                await self.bannedList.delete_one({'banId': int(user_id)})
                return True
            else:
                return False
        except Exception as e:
            print(f"Failed to unban. Reason: {e}")
            return e

    # --- Add a channel to the database ---
    async def add_channel(self, channel_id, channel_title, user_id):
        channel_data = {
            'channel_id': channel_id,
            'title': channel_title,
            'user_id': user_id,
            'added_on': datetime.datetime.utcnow()
        }
        # Add the channel only if it doesn't already exist for the user
        existing_channel = await self.channels_col.find_one({'channel_id': channel_id, 'user_id': user_id})
        if not existing_channel:
            await self.channels_col.insert_one(channel_data)
            return True
        return False

    # --- Get all channels for a user ---
    async def get_user_channels(self, user_id):
        channels = await self.channels_col.find({'user_id': user_id}).to_list(length=100)
        return channels

    # --- Get a single channel by its channel_id ---
    async def get_channel(self, channel_id):
        channel = await self.channels_col.find_one({'channel_id': channel_id})
        return channel

    # --- Remove a channel ---
    async def remove_channel(self, channel_id):
        result = await self.channels_col.delete_one({'channel_id': channel_id})
        return result.deleted_count > 0

    # --- Count the number of channels a user has ---
    async def count_user_channels(self, user_id):
        count = await self.channels_col.count_documents({'user_id': user_id})
        return count
