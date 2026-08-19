import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from motor.motor_asyncio import AsyncIOMotorClient
import config

app = Client(
    "movie_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

mongo_client = AsyncIOMotorClient(config.DATABASE_URI)
db = mongo_client[config.DATABASE_NAME]
collection = db["movies"]

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply_text(
        f"Namaste {message.from_user.first_name}!\n\nMain Auto-Filter Movie Bot hoon. Mujhe kisi bhi movie ka naam bhejein, main aapko file provide karunga."
    )

@app.on_message(filters.channel & (filters.document | filters.video))
async def channel_indexer(client, message):
    media = message.document or message.video
    if not media:
        return
    file_name = media.file_name or "Unknown"
    file_id = media.file_id
    file_size = media.file_size
    
    await collection.update_one(
        {"file_id": file_id},
        {"$set": {"file_name": file_name.lower(), "original_name": file_name, "file_id": file_id, "size": file_size}},
        upsert=True
    )

@app.on_message(filters.text & filters.private & ~filters.command(["start", "help"]))
async def movie_search(client, message):
    query = message.text.lower().strip()
    results = collection.find({"file_name": {"$regex": query, "$options": "i"}}).limit(10)
    buttons = []
    
    async for movie in results:
        buttons.append([InlineKeyboardButton(movie["original_name"], callback_data=f"send_{movie['file_id']}")])
    
    if buttons:
        await message.reply_text(f"🎬 Results for '{message.text}':", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text("❌ Koi movie nahi mili. Channel me file check karein ya spelling dekhein.")

@app.on_callback_query(filters.regex(r"^send_"))
async def send_file(client, query):
    file_id = query.data.split("_")[1]
    await client.send_cached_media(
        chat_id=query.from_user.id,
        file_id=file_id,
        caption="Aapki movie file ready hai! 🍿"
    )
    await query.answer()

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
