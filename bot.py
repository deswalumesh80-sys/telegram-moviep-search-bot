import asyncio
from aiohttp import web
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

# Render Health Check (Port binding fix)
routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.Response(text="Bot is running!")

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply_text(
        f"Namaste {message.from_user.first_name}!\n\nMain Auto-Filter Movie Bot hoon. Mujhe kisi bhi movie ka naam bhejein, main aapko file provide karunga."
    )

# Auto Indexing from Channel
@app.on_message(filters.channel & (filters.document | filters.video))
async def channel_indexer(client, message):
    media = message.document or message.video
    if not media:
        return
    file_name = getattr(media, "file_name", "Unknown File")
    file_id = media.file_id
    file_size = getattr(media, "file_size", 0)
    
    await collection.update_one(
        {"file_id": file_id},
        {"$set": {
            "file_name": file_name.lower(),
            "original_name": file_name,
            "file_id": file_id,
            "size": file_size
        }},
        upsert=True
    )

# Movie Search Handler
@app.on_message(filters.text & filters.private & ~filters.command(["start", "help"]))
async def movie_search(client, message):
    query = message.text.lower().strip()
    cursor = collection.find({"file_name": {"$regex": query, "$options": "i"}}).limit(10)
    movies = await cursor.to_list(length=10)
    
    if not movies:
        await message.reply_text("❌ Koi movie nahi mili. Channel me file check karein ya spelling dekhein.")
        return

    buttons = []
    for movie in movies:
        btn_text = f"🎬 {movie.get('original_name', 'Download')}"
        buttons.append([InlineKeyboardButton(btn_text, callback_data=f"send_{movie['file_id']}")])
    
    await message.reply_text(f"🎬 Results for '{message.text}':", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex(r"^send_"))
async def send_file(client, query):
    file_id = query.data.split("_")[1]
    await client.send_cached_media(
        chat_id=query.from_user.id,
        file_id=file_id,
        caption="Aapki movie file ready hai! 🍿"
    )
    await query.answer()

async def main():
    await app.start()
    print("Bot is started!")
    
    # Start web server for Render port check
    app_runner = web.AppRunner(await web_server())
    await app_runner.setup()
    port = int(config.os.environ.get("PORT", 8080))
    site = web.TCPSite(app_runner, "0.0.0.0", port)
    await site.start()
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
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
