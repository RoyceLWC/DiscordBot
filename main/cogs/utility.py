import time
import json

import discord
from discord.ext import commands
from discord.ext.commands import Bot

client = discord.Client()


def get_prefix(client, message):
    with open("prefixes.json", "r") as read:
        r_prefixes = json.load(read)

    return r_prefixes[str(message.guild.id)]


client = Bot(command_prefix=get_prefix)


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

        before = time.monotonic()
        await ctx.send("Pong!")
        ping = (time.monotonic() - before) * 1000

        await ctx.send(f"{round(ping, 2)} ms")


def setup(client):
    client.add_cog(Utility(client))
