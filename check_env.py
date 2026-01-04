"""Check .env file contents"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("365botGary アカウント:")
print(f"  TWITTER_365BOT_API_KEY: {os.getenv('TWITTER_365BOT_API_KEY', 'NOT SET')[:30]}...")
print(f"  TWITTER_365BOT_API_SECRET: {os.getenv('TWITTER_365BOT_API_SECRET', 'NOT SET')[:30]}...")
print(f"  TWITTER_365BOT_ACCESS_TOKEN: {os.getenv('TWITTER_365BOT_ACCESS_TOKEN', 'NOT SET')[:40]}...")
print(f"  TWITTER_365BOT_ACCESS_TOKEN_SECRET: {os.getenv('TWITTER_365BOT_ACCESS_TOKEN_SECRET', 'NOT SET')[:30]}...")
print()
print("pursahsgospel アカウント:")
print(f"  TWITTER_PURSAHS_API_KEY: {os.getenv('TWITTER_PURSAHS_API_KEY', 'NOT SET')[:30]}...")
print(f"  TWITTER_PURSAHS_API_SECRET: {os.getenv('TWITTER_PURSAHS_API_SECRET', 'NOT SET')[:30]}...")
print(f"  TWITTER_PURSAHS_ACCESS_TOKEN: {os.getenv('TWITTER_PURSAHS_ACCESS_TOKEN', 'NOT SET')[:40]}...")
print(f"  TWITTER_PURSAHS_ACCESS_TOKEN_SECRET: {os.getenv('TWITTER_PURSAHS_ACCESS_TOKEN_SECRET', 'NOT SET')[:30]}...")
print("=" * 60)







