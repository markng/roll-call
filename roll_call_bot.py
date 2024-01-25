import discord
from discord.ext import commands
from discord.utils import format_dt
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from models import Base, CheckIn

engine = create_async_engine('sqlite+aiosqlite:///roll_call_bot.db', echo=True, future=True)


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
        self.session_maker = async_sessionmaker(engine, expire_on_commit=False)
        await self.conn.run_sync(Base.metadata.create_all)
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
            guild = ctx.guild.id
            member_ids = map(lambda member: member.id, ctx.message.mentions)
            # get the last checkin for each member
            stmt = select(CheckIn).where(CheckIn.guild_id == guild).where(CheckIn.user_id.in_(member_ids)).group_by(
                CheckIn.user_id).order_by(func.max(CheckIn.at))

            for check_in in await self.conn.execute(stmt):
                await ctx.send(f'{check_in.user_name} last checked in at {format_dt(check_in.at)}')

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