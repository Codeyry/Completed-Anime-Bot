from config import DB_URL, DB_NAME
from pymongo import AsyncMongoClient


# clients setup 
_client = AsyncMongoClient(DB_URL) 
_db = _client[DB_NAME] 
_users = _db.users # collection name "users"
_entries = _db.entries # entry collection 

# save id 
async def add_user(user_id: int):
  await _users.update_one(
    {"_id": user_id}, {"$setOnInsert": {"_id": user_id}}, upsert=True
  )
  
# get all users 
async def get_all_users() -> list[int]:
  cursor = _users.find({}, {"_id": 1}) 
  return [doc["_id"] async for doc in cursor] 
  
# delete users [bot blocked or deactivated account cleanup] 
async def del_user(user_id: int):
  await _users.delete_one({"_id": user_id}) 




# check if any entry is already processed or not 
async def is_entry_already_processed(entry_id: int):
  cursor = _entries.find({}, {"_id": entry_id}).limit(1)
  return bool(await cursor.to_list(length=1))




# mark item to be already processed
async def mark_entry(entry_id):
  await _entries.update_one(
    {"_id": entry_id},
    {"$setOnInsert": {"_Id": entry_id}},
    upsert=True
  )



