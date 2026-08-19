import asyncio
import urllib.parse
from bs4 import BeautifulSoup
import aiohttp
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

# Render Port Binding Check
routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.Response(text="Bot is running smoothly!")

async def web_server():
    web_app = web.Application()
    web_app.add_routes(routes)
    return web_app

# Start Command Handler
@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply_text(
        f"Namaste {message.from_user.first_name}!\n\n"
        "Main Live Movie Finder Bot hoon. Mujhe kisi bhi Movie ya Web Series ka naam bhejein, main direct web server se download links nikal kar dunga."
    )

# Live Scraper Engine
async def search_movies(query):
    encoded_query = urllib.parse.quote_plus(query)
    search_url = f"https://moviesmod.day/?s={encoded_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    results = []
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(search_url, timeout=10) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    articles = soup.find_all("article", limit=8)
                    for article in articles:
                        title_tag = article.find("h2") or article.find("h3") or article.find("a")
                        link_tag = article.find("a", href=True)
                        
                        if title_tag and link_tag:
                            title = title_tag.get_text(strip=True)[:45]
                            link = link_tag["href"]
                            results.append({"title": title, "url": link})
    except Exception as e:
        print(f"Error scraping: {e}")
        
    return results

# User Search Query Handler
@app.on_message(filters.text & filters.private & ~filters.command(["start", "help"]))
async def movie_search_handler(client, message):
    query = message.text.strip()
    status_msg = await message.reply_text(f"🔍 Searching for **'{query}'** across web servers...")
    
    results = await search_movies(query)
    
    if not results:
        await status_msg.edit_text("❌ Movie nahi mili. Spelling check karein ya dusra naam likhein.")
        return
        
    buttons = []
    for item in results:
        buttons.append([InlineKeyboardButton(f"🎬 {item['title']}", url=item['url'])])
        
    await status_msg.edit_text(
        f"🍿 **Results for:** `{query}`\n\nNeeche button par click karke movie download karein:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def main():
    await app.start()
    print("Bot is started!")
    
    # Run Background Web Server for Render
    app_runner = web.AppRunner(await web_server())
    await app_runner.setup()
    port = int(config.os.environ.get("PORT", 8080))
    site = web.TCPSite(app_runner, "0.0.0.0", port)
    await site.start()
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
