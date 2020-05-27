import asyncio
import os

import discord
import youtube_dl
import shutil
from discord import ClientException
from discord.ext import commands
from discord.ext.commands import Bot
from discord.utils import get

client = discord.Client()

try:  # See if there is already a pre-existing prefix file.
    with open("prefix.txt", "r") as bot_prefix:
        PREFIX = bot_prefix.readlines()[0]
except FileNotFoundError:  # If not, create one with a given prefix from the prompt.
    with open("prefix.txt", "w") as set_prefix:
        PREFIX = input("Please enter a prefix: ")
        set_prefix.write(PREFIX)

client = Bot(command_prefix=PREFIX)

players = {}
queues = {}
q_song_names = []


class Music(commands.Cog, name="music"):

    def __init__(self, client):
        self.client = client

    @commands.command(brief="Joins a voice channel", description="Joins the current voice channel that you're in.",
                      aliases=["j"])
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

    @commands.command(brief="Leaves a voice channel", description="Leaves the current voice channel.", aliases=["l"])
    async def leave(self, ctx):
        channel = ctx.message.author.voice.channel  # Gets the channel the user (author) is in.

        def is_connected(ctx):
            voice_client = ctx.guild.voice_client
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
        global name

        def check_queue():
            global left_in_queue
            queue_in_file = os.path.isdir("./queue")
            if queue_in_file is True:
                DIR = os.path.abspath(os.path.realpath("queue"))
                length = len(os.listdir(DIR))
                left_in_queue = length - 1
                try:
                    first_file = os.listdir(DIR)[0]  # First file inside of the directory.
                except IndexError:
                    print("No more queued song(s).")
                    queues.clear()
                    q_song_names.clear()
                    return
                main_location = os.path.dirname("./main")  # os.path.realpath(__file__)
                song_path = os.path.abspath(os.path.realpath("queue") + "\\" + first_file)
                if length != 0:
                    q_song_names.pop(0)

                    print("Song finished, playing next queued song...")
                    message = ctx.send("`Song finished, playing next queued song...`")

                    # How to use an await statement within a synchronous function.
                    fut = asyncio.run_coroutine_threadsafe(message, client.loop)
                    try:
                        fut.result()
                    except:
                        pass

                    song_present = os.path.isfile("song.mp3")  # Make sure song is there.
                    if song_present:
                        os.remove("song.mp3")

                    shutil.move(song_path, main_location)  # Move our queued song to our main directory
                    for song_file in os.listdir("./"):
                        if song_file.endswith(".mp3"):
                            os.rename(song_file, "song.mp3")  # Rename the new song.

                    # Play song and send message when song has finished.
                    p_voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())  # Make it recursive.
                    p_voice.source = discord.PCMVolumeTransformer(p_voice.source)
                    p_voice.source.volume = 0.1  # Sets the volume of the song.

                else:
                    queues.clear()
                    q_song_names.clear()
                    return

            else:  # If there is no queue folder...
                queues.clear()
                q_song_names.clear()
                print("No songs were queued before the ending of the last song.")

        song_there = os.path.isfile("song.mp3")  # Create a variable of a song current playing (if there is one).

        try:
            if song_there:  # Try to remove the current song being played.
                os.remove("song.mp3")
                queues.clear()
                q_song_names.clear()
                print("Song has been removed.")
        except PermissionError:
            print("Tried to remove song file, but it's currently being played.")
            return

        queue_infile = os.path.isdir("./queue")  # Check for an old queue folder (if stop command used).
        try:
            queue_folder = "./queue"
            if queue_infile is True:
                print("Removed old queue.")
                shutil.rmtree(queue_folder)  # Remove folder (even if it has contents within [shutil]).
        except FileNotFoundError:
            print("No old queue folder.")

        await ctx.send("`Loading...`")

        # Play the music requested

        p_voice = ctx.guild.voice_client

        ydl_opts = {  # YouTube Download Options
            "format": "bestaudio/best",  # Get the best audio file.
            "quiet": True,  # Suppresses downloading information in console.
            "postprocessors": [{  # Setting preferred qualities.
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",  # MP3 file
                "preferredquality": "192"  # Quality of MP3
            }]
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:  # Make it all to "ydl"
            await ctx.send("`Downloading audio...`")
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', None)
            ydl.download([url])  # Get the full URL ([])

        for file in os.listdir("./"):  # Go into the current directory
            if file.endswith(".mp3"):
                name = file
                # new_name = name.rsplit("-", 2)
                print(f"Renamed file: {file}")
                os.rename(file, "song.mp3")

        # Play song and send message when song has finished.
        p_voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
        p_voice.source = discord.PCMVolumeTransformer(p_voice.source)
        p_voice.source.volume = 0.1  # Sets the volume of the song.

        await ctx.send(f"`Playing: {video_title}`")
        print("Playing...")

    @commands.command(brief="Pauses the current song playing", description="Pauses the current song playing.")
    async def pause(self, ctx):

        pause_voice = ctx.guild.voice_client

        if pause_voice and pause_voice.is_playing():  # Checks if the bot is in a voice channel and playing music.
            voice.pause()
            print("Music paused.")
            await ctx.send("`Music paused.`")
        else:
            print("Music not playing [failed pause].")
            await ctx.send("`There is currently no music playing to pause.`")

    @commands.command(brief="Resumes a paused song", description="Resumes a paused song.", aliases=["r"])
    async def resume(self, ctx):

        resume_voice = ctx.guild.voice_client

        if resume_voice and resume_voice.is_paused():  # Checks if there is music that has been paused.
            resume_voice.resume()
            print("Music resumed.")
            await ctx.send("`Music resumed.`")
        else:
            print("No music paused.")
            await ctx.send("There is no paused music to resume!")

    @commands.command(brief="Stops the bot from playing music", description="Stop the bot from playing music.",
                      aliases=["s"])
    async def stop(self, ctx):

        stop_voice = ctx.guild.voice_client

        queues.clear()  # Clear queue when session stops.
        q_song_names.clear()  # Also, clear the song names list.

        if stop_voice and stop_voice.is_playing():
            stop_voice.stop()
            print("Music has been stopped.")
            await ctx.send("The music has been stopped.")
        else:
            print("There is no music playing.")
            await ctx.send("There is no music playing to stop!")

        for x in os.listdir("./"):
            if x.endswith(".mp3") or x.endswith(".webm"):
                os.remove(x)

    @commands.command(brief="Views the queue", description="Views the current queue of music.", aliases=["vq", "view"])
    async def viewqueue(self, ctx):
        try:
            global q_song_names

            DIR = os.path.abspath(os.path.realpath("queue"))
            length = len(os.listdir(DIR))
            still_in_link = length

            queue = discord.Embed(
                title="Music | Queue",
                color=0x7289DA  # Blurple
            )
            queue.set_footer(
                text=f"Requested by {ctx.message.author.name}",
            )
            queue.add_field(
                name="Songs left in queue:",
                value=f"{still_in_link}\n",
                inline=False
            )
            songs = ""
            n = 1

            for song in q_song_names:
                songs += f"{n}. {song}\n"
                n += 1

            queue.add_field(
                name="Queue",
                value=songs,
                inline=False
            )

            await ctx.send(embed=queue)
        except:
            await ctx.send("`There are no queued songs!`")

    @commands.command(brief="Adds a song to the queue", description="Adds a song to the current queue.", usage="[url]", aliases=["q"])
    async def queue(self, ctx, url: str):
        queue_infile = os.path.isdir("./queue")
        if queue_infile is False:  # Check to see if the directory exists (if not, create one).
            os.mkdir("queue")
        DIR = os.path.abspath(os.path.realpath("queue"))
        q_num = len(os.listdir(DIR))  # Get the amount of files in the queue and count them (if there are any).
        q_num += 1  # Add the song
        add_queue = True

        while add_queue:
            if q_num in queues:  # Check to see if it's not in the queues dictionary
                q_num += 1
            else:
                add_queue = False
                queues[q_num] = q_num  # Put it into the dictionary (queue number).

        queue_path = os.path.abspath(os.path.realpath("queue") + f"\song{q_num}.%(ext)s")  # Gets the real path of queue and gives a number attached to the song.

        ydl_opts = {  # YouTube Download Options
            "format": "bestaudio/best",  # Get the best audio file.
            "quiet": True,  # Suppresses downloading information in console.
            "outtmpl": queue_path,  # Where it's going to output to.
            "postprocessors": [{  # Setting preferred qualities.
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",  # MP3 file
                "preferredquality": "192"  # Quality of MP3
            }]
        }

        # Download the song
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:  # Make it all to "ydl"
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', None)
            ydl.download([url])  # Get the full URL ([])

        await ctx.send(f"`Adding song to queue...`")

        q_song_names.append(video_title) # Add song name to q_song_names list.

        await ctx.send("`Song added!`")

def setup(client):
    client.add_cog(Music(client))
