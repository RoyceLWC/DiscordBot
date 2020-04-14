import youtube_dl
import os
import discord
from discord import VoiceClient, ClientException
from discord.ext import commands
from discord.ext.commands import Bot
from discord.utils import get

client = discord.Client()
client = Bot(command_prefix="?")

players = {}


class Music(commands.Cog, name="music"):

    def __init__(self, client):
        self.client = client

    @commands.command(brief="A test command.", description="A test command.", usage="")
    async def test(self, ctx):
        await ctx.send("Hello")

    @commands.command(brief="Joins a voice channel", description="Joins the current voice channel that you're in.")
    async def join(self, ctx):

        try:
            global voice
            channel = ctx.message.author.voice.channel  # Gets the channel the user (author) is in.
            voice = get(client.voice_clients, guild=ctx.guild)

            if voice and voice.is_connected():  # If user is in a voice channel and bot is in a (different) channel, ...
                await voice.move_to(channel)  # Move to the channel the author is in.
            else:
                voice = await channel.connect()  # Else, connect to the channel.
                await ctx.send(f"The bot has connected to {channel}.\n")

            await ctx.send(f"`Joined {channel}.`")

        except ClientException:
            await ctx.send(f"I am already in a voice channel!")  # Correct this error to move to a different channel.

    @commands.command(brief="Leaves a voice channel", description="Leaves the current voice channel.")
    async def leave(self, ctx):
        channel = ctx.message.author.voice.channel  # Gets the channel the user (author) is in.

        def is_connected(ctx):
            voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
            return voice_client and voice_client.is_connected()

        if is_connected(ctx):
            await ctx.voice_client.disconnect()
            print(f"The bot has left {channel}.\n")
            await ctx.send(f"`Left {channel}.`")
        else:
            print("Leave command executed; bot was not in a voice channel")
            await ctx.send("I am not in a voice channel!")

    @commands.command(brief="Plays music", description="Plays music received from YouTube.", usage="[url]",
                      aliases=["p"])
    async def play(self, ctx, url: str):
        song_there = os.path.isfile("song.mp3")  # Create a variable of a song current playing (if there is one).

        try:
            if song_there:  # Try to remove the current song being played.
                os.remove("song.mp3")
                await ctx.send("Song has been removed.")
        except PermissionError:
            await ctx.send("Tried to remove song file, but it's currently being played.")
            return

        await ctx.send("`Loading...`")

        # Play the music requested
        voice = get(client.voice_clients, guild=ctx.guild)

        ydl_opts = { # YouTube Download Options
            "format": "bestaudio/best",   # Get the best audio file.
            "postprocessors": [{ # Setting preferred qualities.
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",  # MP3 file
                "preferredquality": "192"  # Quality of MP3
        }]
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl: # Make it all to "ydl"
            await ctx.send("`Downloading audio...`")
            ydl.download([url])  # Get the full URL ([])

        for file in os.listdir("./"): # Go into the current directory
            if file.endswith(".mp3"):
                name = file
                print(f"Renamed file: {file}")
                os.rename(file, "song.mp3")

        # Play song and send message when song has finished.
        voice.play(discord.FFmpegAudio("song.mp3"), after=lambda e: print(f"{name} has finished playing."))
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = 0.1  # Sets the volume of the song.

        new_name = name.rsplit("-", 2)
        await ctx.send(f"Playing: {new_name}")
        print("Playing...")


def setup(client):
    client.add_cog(Music(client))
