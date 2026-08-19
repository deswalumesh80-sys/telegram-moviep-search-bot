import os
import asyncio
import urllib.parse
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import config

app = Client(
    "movie_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

# Render Port Web Server
routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.Response(text="Bot is running smoothly!")

async def web_server():
    web_app = web.Application()
    web_app.add_routes(routes)
    return web_app

# Start Command
@app.on_message(filters.command("start"))
async def start_handler(client, message):
    user_name = message.from_user.first_name if message.from_user else "Dost"
    await message.reply_text(
        f"Namaste {user_name}!\n\n"
        "Main Live Movie Search Bot hoon. 🎬\n\n"
        "Mujhe kisi bhi Movie ya Web Series ka naam bhejein, main aapko direct online watch & download servers ke link dunga."
    )

# Search Query Handler
@app.on_message(filters.text & filters.private & ~filters.command(["start", "help"]))
async def movie_search_handler(client, message):
    query = message.text.strip()
    encoded = urllib.parse.quote_plus(query)
    
    buttons = [
        [InlineKeyboardButton("🌐 Server 1 (VegaMovies Direct)", url=f"https://www.google.com/search?q=site:vegamovies.im+{encoded}+download")],
        [InlineKeyboardButton("⚡ Server 2 (MoviesMod HD)", url=f"https://www.google.com/search?q=site:moviesmod.day+{encoded}+download")],
        [InlineKeyboardButton("🍿 Server 3 (Direct Watch & DL)", url=f"https://www.google.com/search?q=watch+{encoded}+online+free")]
    ]
    
    await message.reply_text(
        f"🎬 **Results for:** `{query}`\n\n"
        "Neeche diye gaye kisi bhi server link par click karke movie download ya stream karein:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def main():
    await app.start()
    print("Bot is started!")
    
    app_runner = web.AppRunner(await web_server())
    await app_runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(app_runner, "0.0.0.0", port)
    await site.start()
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
