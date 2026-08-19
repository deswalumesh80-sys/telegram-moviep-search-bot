import os

API_ID = int(os.environ.get("API_ID", "38398715"))
API_HASH = os.environ.get("API_HASH", "6cf70e41fbc67908ae547a31c2cfe9c3a")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8957794036:AAHJctqtHq5zMKke_t9kJqC-Kx8aNqyGW8c")
DATABASE_URI = os.environ.get("DATABASE_URI", "mongodb+srv://deswalumesh80_db_user:UmeshMovieBot123@cluster0.nrzckbo.mongodb.net/?retryWrites=true&w=majority")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "Cluster0")
ADMINS = [int(admin) for admin in os.environ.get("ADMINS", "8471574210").split()]
CHANNELS = [int(ch) for ch in os.environ.get("CHANNELS", "-1004328943081").split()]
