import os
from dotenv import load_dotenv
from pathlib import Path


load_dotenv(Path(__file__).parent / ".env")


TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")