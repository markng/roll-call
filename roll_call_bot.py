import os
from datetime import datetime

import discord
import timeago
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from models import Base, CheckIn

load_dotenv()
engine = create_async_engine(os.environ['DATABASE_URL'], echo=True)

session_maker = async_sessionmaker(engine)


class RollCallBot(commands.Bot):
    conn = None
    session = None

    def __init__(self):
        super().__init__(
            command_prefix={"!"},
            intents=discord.Intents.all(),
            case_insensitive=True,
        )
        self.commands()

    async def on_ready(self):
        self.conn = await engine.connect()
        await self.conn.run_sync(Base.metadata.create_all)
        await self.conn.commit()
        await self.conn.close()
        print(f'We have logged in as {self.user}')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        if message.author == self.user:
            return

        await self.process_commands(message)

        await self.checkin_from_message(message)

    def commands(self):
        @self.command(name='last', pass_context=True)
        async def last(ctx, arg):
            async with (session_maker.begin() as session):
                guild = ctx.guild.id
                member_ids = map(lambda member: member.id, ctx.message.mentions)

                # get latest check in for every member
                stmt = select(
                    CheckIn
                ).filter(
                    CheckIn.user_id.in_(member_ids)
                ).order_by(CheckIn.user_id).order_by(
                    CheckIn.at.desc()
                ).distinct(
                    CheckIn.user_id
                )

                for check_in in await session.execute(stmt):
                    await ctx.send(
                        f'{check_in[0].user_name} last checked in {timeago.format(check_in[0].at, datetime.now().astimezone())}')

    async def checkin_from_message(self, message):
        if message.content.startswith('!last'):
            return
        async with session_maker() as session:
            check_in = CheckIn(
                user_id=message.author.id,
                user_name=message.author.name,
                message_id=message.id,
                channel_id=message.channel.id,
                guild_id=message.guild.id,

            )
            session.add(check_in)
            await session.commit()
