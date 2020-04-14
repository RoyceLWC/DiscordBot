import discord
from discord.ext import commands
from discord.ext.commands import Bot

client = discord.Client()
client = Bot(command_prefix="?")


class Music(commands.Cog, name="music"):

    def __init__(self, client):
        self.client = client

    @commands.command(brief="A test command.", description="A test command.", usage="")
    async def test(self, ctx):
        await ctx.send("Hello")

    @commands.command(brief="Joins a voice channel", description="Joins the current voice channel that you're in.")
    async def join(self, ctx):
        channel = ctx.message.author.voice.channel
        await channel.connect()

    @commands.command(brief="Leaves a voice channel", description="Leaves the current voice channel.")
    async def leave(self, ctx):
        server = ctx.message.guild

        try:
            voice_client = client.voice_client_in(server)
            await ctx.voice_client.disconnect()
        except:
            await ctx.send("I am not in a voice channel!")


def setup(client):
    client.add_cog(Music(client))
