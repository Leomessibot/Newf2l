import datetime
import motor.motor_asyncio


class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.bannedList = self.db.bannedList
        self.channels = self.db.channels  # Collection for storing approved channels
        self.user_settings = self.db.user_settings  # Collection for storing user-specific settings

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

    # --- Channel-related methods ---
    
    async def add_channel(self, channel_id, channel_title, user_id):
        # Add the channel only if it doesn't already exist for the user
        existing_channel = await self.channels.find_one({'channel_id': channel_id, 'user_id': user_id})
        if not existing_channel:
            channel_data = {
                'channel_id': channel_id,
                'title': channel_title,
                'user_id': user_id,
                'added_on': datetime.datetime.utcnow()
            }
            await self.channels.insert_one(channel_data)
            return True
        return False

    async def get_user_channels(self, user_id):
        channels = await self.channels.find({'user_id': user_id}).to_list(length=100)
        return channels

    async def get_channel(self, channel_id):
        channel = await self.channels.find_one({'channel_id': channel_id})
        return channel

    async def remove_channel(self, channel_id):
        result = await self.channels.delete_one({'channel_id': channel_id})
        return result.deleted_count > 0

    async def count_user_channels(self, user_id):
        count = await self.channels.count_documents({'user_id': user_id})
        return count

    # --- User settings methods ---

    async def get_user_settings(self, user_id):
        settings = await self.user_settings.find_one({'user_id': user_id})
        return settings if settings else {}

    async def update_user_settings(self, user_id, settings_data):
        # Update settings for the user
        existing_settings = await self.user_settings.find_one({'user_id': user_id})
        if existing_settings:
            await self.user_settings.update_one(
                {'user_id': user_id},
                {'$set': settings_data}
            )
        else:
            settings_data['user_id'] = user_id
            await self.user_settings.insert_one(settings_data)

    async def reset_user_settings(self, user_id):
        # Reset settings for the user
        await self.user_settings.delete_one({'user_id': user_id})
