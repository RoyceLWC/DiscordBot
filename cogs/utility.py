import time

import discord
from discord.ext import commands
from discord.ext.commands import Bot

client = discord.Client()
client = Bot(command_prefix="?")

user_ids = ["<@200095402085580800>", "<@325554582321365003>", "<@297897016007196674>", "<@454756148092993536>",
            "<@107203298771124224>", "<@617408635747696642>"]


class Utility(commands.Cog, name="utility"):

    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_message(self, message):
        pass

    # Commands
    @commands.command(brief="Checks your ping", description="Checks your ping (latency).")
    async def ping(self, ctx):
        global user_ids

        before = time.monotonic()
        await ctx.send("Pong!")
        ping = (time.monotonic() - before) * 1000

        await ctx.send(f"{round(ping, 2)} ms")


def setup(client):
    client.add_cog(Utility(client))
