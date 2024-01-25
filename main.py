import asyncio
import os

from dotenv import load_dotenv

from roll_call_bot import RollCallBot

load_dotenv()
client = RollCallBot()


async def main():
    await client.start(os.environ['DISCORD_TOKEN'])

asyncio.run(main())