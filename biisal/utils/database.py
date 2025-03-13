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

    # Add a new channel for link generation
    async def add_channel(self, channel_id):
        channel = await self.channels.find_one({"channel_id": int(channel_id)})
        if channel:
            return False  # Channel already added
        await self.channels.insert_one({"channel_id": int(channel_id)})
        return True  # Channel successfully added

    # Check if a channel is already approved
    async def get_channel(self, channel_id):
        return await self.channels.find_one({"channel_id": int(channel_id)})

    # Remove a channel (if needed)
    async def remove_channel(self, channel_id):
        await self.channels.delete_one({"channel_id": int(channel_id)})
