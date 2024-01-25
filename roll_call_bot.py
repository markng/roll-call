import asyncio
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from models import Base, CheckIn

engine = create_async_engine('sqlite+aiosqlite:///roll_call_bot.db', echo=True, future=True)

intents = discord.Intents.default()
intents.message_content = True



class RollCallBot(commands.Bot):
    conn = None
    session = None
    def __init__(self):
        super().__init__(
            command_prefix={"!"},
            intents=discord.Intents.all(),
            case_insensitive=True,
        )

    async def on_ready(self):
        self.conn = await engine.connect()
        self.session_maker = async_sessionmaker(engine, expire_on_commit=False)
        await self.conn.run_sync(Base.metadata.create_all)
        print(f'We have logged in as {self.user}')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        if message.author == self.user:
            return

        await self.checkin_from_message(message)

        if message.content.startswith('$roll-call'):
            await message.channel.send('Users who have responded to the roll call:')

    async def checkin_from_message(self, message):
        async with self.session_maker.begin() as session:
            check_in = CheckIn(
                user_id=message.author.id,
                user_name=message.author.name,
                message_id=message.id,
                channel_id=message.channel.id,
                guild_id=message.guild.id
            )
            session.add(check_in)

            await session.commit()

