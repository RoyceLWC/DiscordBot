import asyncio
import json
import pytz
import pandas as pd
import datetime
from datetime import timedelta

import discord
from discord.ext import commands
from discord.ext.commands import Bot

client = discord.Client()
now = datetime.datetime.now()


# Prefix per server
def get_prefix(client, message):
    with open("prefixes.json", "r") as read:
        r_prefixes = json.load(read)

    return r_prefixes[str(message.guild.id)]


client = Bot(command_prefix=get_prefix)

with open("prefixes.json", "r") as f:
    prefixes = json.load(f)

prompts = [  # Each stored prompt to be looped through [GLOBAL].
            "`Enter the full name of the GP + country:`",
            "`Enter the <Round No. | Race weekend dates>:`",
            "`Enter the time of FP1 (local track time):`",
            "`Enter the time of FP2 (local track time):`",
            "`Enter the time of FP3 (local track time):`",
            "`Enter the time of qualifying (local track time):`",
            "`Enter the time of the race (local track time):`",
            "`Enter the image URL of the country's flag:`",
            "`Enter the time zone of the country [EXAMPLE+1]:`",
            "`Enter the image URL of the track:`",
            "`Enter the track's name:`",
            "`[Timezone Setting] Enter the starting date of the race weekend [yyyy/mm/dd]:`",
            "`[Timezone Setting] Enter the TZ database name of the region:`"
        ]


class F1(commands.Cog, name="f1"):
    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        pass

    # Commands

    # Setting a user's timezone for future timings
    @commands.command(brief="Sets your current timezone",
                      description="Setup your current timezone which can be referenced when using commands that display timed events.",
                      aliases=["stz"], usage="[timezone]")
    async def settimezone(self, ctx, *, timezone=None):

        global prefixes, response

        with open("timezones.json", "r") as read_timezones:
            tz = json.load(read_timezones)

        if timezone is None:

            setup_embed = discord.Embed(
                title="Timezones | Setup",
                description="Please enter your city (TZ database name):",
                colour=0xe74c3c
            )

            setup_embed.set_footer(text="More info: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")

            await ctx.send(embed=setup_embed)

            response = await ctx.bot.wait_for('message', timeout=120.0,
                                              check=lambda message: message.author == ctx.author)

        matches = []

        for zone in pytz.all_timezones:
            try:
                if response.content.lower() in zone.lower():  # If the given TZ database name is valid and in the full TZ list, update the timezone variable.
                    matches.append(zone)  # Add 1 to the total matches (check).
            except:
                if timezone.lower() in zone.lower():  # If the user entered the timezone alongside the command, execute
                    matches.append(zone)

        print(matches)

        if len(matches) == 0:
            error_embed = discord.Embed(  # Error embed
                title="Error!",
                colour=0xe74c3c
            )
            error_embed.add_field(
                name="No timezone match found!",
                value=f"`{prefixes[str(ctx.guild.id)][0]}settimezone [TZ database name*]`",
                inline=False
            )
            error_embed.set_footer(text="*More info: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")

            await ctx.send(embed=error_embed)
            return
        elif len(matches) == 1:  # Only one match found (pinpointed - completed)
            pass
        else:  # More than one match found
            timezone_dict = {}

            # timezones = ""
            # timezones += f"{sub_matches[1]}\n"

            for match in matches:
                sub_matches = match.split('/')  # Split TZ database name into sub-strings

                # Duplicates added onto the unique timezone prefix key.
                if len(sub_matches) == 2:
                    # Get sub-string after given target character (2 sub-strings)
                    timezone_dict[sub_matches[0]] = timezone_dict.get(sub_matches[0], []) + [f"{sub_matches[1]}"]
                elif len(match.split('/')) == 3:
                    # Get sub-string after given target character (3 sub-strings)
                    timezone_dict[sub_matches[0]] = timezone_dict.get(sub_matches[0], []) + [f"{sub_matches[1]}/{sub_matches[2]}"]
                else:
                    timezone_dict[sub_matches[0]] = timezone_dict.get(sub_matches[0], []) + [f"{match}"]

            # Setting TZ prefix heading
            prefix_heading = ""

            first_loop = True  # Setting first prefix without '|'

            for prefix in timezone_dict:  # Loop through each key (TZ prefix)
                if first_loop:
                    prefix_heading += f"{prefix} "
                    first_loop = False
                else:
                    prefix_heading += f"| {prefix} "

            multiple_timezones_embed = discord.Embed(
                title="Multiple timezones detected",
                description="Please retry with a more specific timezone:",
                colour=0xe74c3c
            )

            for key, values in timezone_dict.items():  # Loop through each key (unique timezone prefix) and its values (list of TZ database names of the same prefix).

                zones = ""
                for value in values:
                    zones += f"{value}\n"

                multiple_timezones_embed.add_field(
                    name=key,
                    value=zones,
                    inline=False
                )

            multiple_timezones_embed.set_author(name="► Error!")

            if timezone is None:
                multiple_timezones_embed.set_footer(text=f"Regions found for '{response.content}': {prefix_heading}")
            else:
                multiple_timezones_embed.set_footer(text=f"Regions found for {timezone}: {prefix_heading}")

            await ctx.send(embed=multiple_timezones_embed)
            return

        check_timezone_embed = discord.Embed(
            title="Selected timezone:",
            description=matches[0],
            colour=0xe74c3c
        )
        check_timezone_embed.set_footer(text="Confirm?")

        react = await ctx.send(embed=check_timezone_embed)

        def check(user_react, user):  # Check if reacted to
            return str(user_react.emoji) in reaction_emoji_list and user == ctx.message.author

        await react.add_reaction(emoji='\U00002B06')  # Up-arrow reaction
        await react.add_reaction(emoji='\U00002B07')  # Down-arrow reaction

        reaction_emoji_list = ['\U00002B06', '\U00002B07']

        # Team name section of embed (edit)
        try:
            reacting, confirm_user = await ctx.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("`Timed out - exiting setup (unsaved)`")  # If user takes too long - timeout.
            return

        if reacting.emoji == "\U00002B06":  # If the .emoji is the up-arrow...
            set_timezone_embed = discord.Embed(
                title="Timezone set!",
                description=f"<@{ctx.author.id}> - {matches[0]}",
                colour=0xe74c3c
            )

            if str(ctx.author.id) in tz:
                set_timezone_embed.set_footer(text=f"Timezone overwritten [ID: {ctx.author.id}]")

            await ctx.send(embed=set_timezone_embed)

        elif reacting.emoji == '\U00002B07':  # If the .emoji is the down-arrow...
            await ctx.send("`Timezone not set.`")
            return
        else:
            await ctx.send("`Timezone not set.`")
            return

        # Writing to JSON file (logging user's TZ database name)
        tz[str(ctx.author.id)] = matches[0]

        with open("timezones.json", "w") as write_timezones:
            json.dump(tz, write_timezones, indent=4)

    @commands.command(brief="Displays user's current timezone", description="Displays user's current TZ database name.", aliases=["tz"])
    async def timezone(self, ctx):

        with open("timezones.json", "r") as user_timezones:
            timezones_dict = json.load(user_timezones)

        user_timezone = timezones_dict[str(ctx.author.id)]

        timezone_embed = discord.Embed(
            description=f"**Current timezone:** `{user_timezone}`",
            colour=0xe74c3c
        )

        timezone_embed.set_footer(text=f"User ID: {ctx.author.id}")

        await ctx.send(embed=timezone_embed)

    # F1 Calendar
    @commands.command(brief="Setup the next upcoming F1 race command", description="Configure the values for the upcoming F1 embed.")
    async def setupcoming(self, ctx):

        global prompts, prefixes

        responses = []

        inputs = await ctx.send("``")

        for prompt in prompts:
            await inputs.edit(content=prompt)  # Edit the inputs message above to reduce clutter.

            try:
                user_response = await ctx.bot.wait_for('message', timeout=90.0,
                                                       check=lambda message: message.author == ctx.author)  # Receive an input (check if it's the same user).
                user_response = str(user_response.content)
                responses.append(user_response)
                try:
                    await ctx.message.delete()
                except:
                    continue
            except:
                # If user takes too long - timeout
                error_embed = discord.Embed(  # Error embed
                    title="Error!",
                    colour=0xe74c3c
                )
                error_embed.add_field(
                    name="Inputs failed! Try again...",
                    value=f"`{prefixes[str(ctx.guild.id)][0]}editupcoming [message ID]`",
                    inline=False
                )
                await ctx.send(embed=error_embed)
                return

        upcoming_embed = discord.Embed(
            title=responses[0],
            description=responses[1],
            colour=0xe74c3c
        )

        # upcoming_embed.set_footer(text=f"Times displayed are track times [{responses[8][:-1]}]")
        upcoming_embed.set_image(
            url=responses[9])
        upcoming_embed.set_thumbnail(
            url=responses[7])
        upcoming_embed.set_author(
            name=f"► F1 Schedule {now.year} | Upcoming",
            icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/F1.svg/1280px-F1.svg.png"
        )

        # Setting up timezone adjustments [absolute]
        start_date = responses[11]

        dates = pd.date_range(start=start_date,
                              periods=3).date.tolist()  # Generate range of dates from start date (race weekend period) - convert to list from class method.

        times = [time.split("-")[0].strip() for time in
                 responses[2:7]]  # Slice responses to get session times and get starting time (without whitespaces).

        fp1_time = datetime.datetime.strptime(f"{dates[0]} {times[0]}",
                                              "%Y-%m-%d %H:%M")  # Convert to datetime object from start time string
        fp2_time = datetime.datetime.strptime(f"{dates[0]} {times[1]}", "%Y-%m-%d %H:%M")
        fp3_time = datetime.datetime.strptime(f"{dates[1]} {times[2]}", "%Y-%m-%d %H:%M")
        qualifying_time = datetime.datetime.strptime(f"{dates[1]} {times[3]}", "%Y-%m-%d %H:%M")
        race_time = datetime.datetime.strptime(f"{dates[2]} {times[4]}", "%Y-%m-%d %H:%M")

        upcoming_embed.add_field(name=f"**FP1 | {fp1_time.strftime('%a').upper()}**", value=f"`{responses[2]}`",
                                 inline=True)
        upcoming_embed.add_field(name=f"**FP2 | {fp2_time.strftime('%a').upper()}**", value=f"`{responses[3]}`",
                                 inline=True)
        upcoming_embed.add_field(name=f"**FP3 | {fp3_time.strftime('%a').upper()}**", value=f"`{responses[4]}`",
                                 inline=True)
        upcoming_embed.add_field(name=f"**Qualifying | {qualifying_time.strftime('%a').upper()}**",
                                 value=f"`{responses[5]}`", inline=True)
        upcoming_embed.add_field(name=f"**Race | {race_time.strftime('%a').upper()}**", value=f"`{responses[6]}`",
                                 inline=True)
        upcoming_embed.add_field(name=f"[Track Time]",
                                 value=f"{str(responses[12]).split('/')[1]} | {responses[8]}", inline=True)

        # Getting track info
        try:
            with open("tracks.txt", "r+", encoding="utf-8") as read_tracks:
                lines_n = read_tracks.readlines()
        except:
            with open("tracks.txt", "r+", encoding="latin-1") as read_tracks:
                lines_n = read_tracks.readlines()

        lines = []

        for line in lines_n:
            lines.append(line[:-1])  # Get rid of the newline escape sequence.

        tracks = []  # Get a list of all tracks

        for line in lines[1::11]:
            tracks.append(line)

        index = 11 * tracks.index(responses[10])
        info = ""

        info += f"**First Grand Prix**: `{lines[index + 5]}`\n"
        info += f"**Number of Laps**: `{lines[index + 6]}`\n"
        info += f"**Circuit Length**: `{lines[index + 7]}km`\n"
        info += f"**Race Distance**: `{lines[index + 8]}km`\n"
        info += f"**Lap Record**: `{lines[index + 9]}` {lines[index + 10]}\n"

        upcoming_embed.add_field(name="───Track Info:───", value=f"{info}\n**{responses[10].rstrip()}:**", inline=False)

        await ctx.send(embed=upcoming_embed)

        with open("upcoming.txt", "w+") as upcoming:

            for r in responses:
                upcoming.write(r+"\n")

        success_embed = discord.Embed(  # Completion embed
            title="Success!",
            colour=0xe74c3c
        )
        success_embed.add_field(
            name="The upcoming F1 race embed has been saved.",
            value=f"Use `{prefixes[str(ctx.guild.id)][0]}upcoming` to view the embed.",
            inline=False
        )

        await ctx.send(embed=success_embed)

    @commands.command(brief="Edits a previous upcoming F1 race embed with the current one", description="Edits a previous upcoming F1 race embed (used for dedicated channels) with the current upcoming embed.", usage="[message ID]")
    async def editupcoming(self, ctx, user_id=None):

        global response, prompts, now, prefixes

        if user_id is None:
            error_embed = discord.Embed(  # Error embed
                title="Error!",
                colour=0xe74c3c
            )
            error_embed.add_field(
                name="Invalid message ID provided!",
                value=f"`{prefixes[str(ctx.guild.id)][0]}editupcoming [message ID]`",
                inline=False
            )

            await ctx.send(embed=error_embed)
            return

        try:
            with open("upcoming.txt", "r+", encoding="utf-8") as read_upcoming:  # Open the upcoming.txt and create a list with each line to substitute into each embed field.
                responses = read_upcoming.readlines()
        except:
            with open("upcoming.txt", "r+", encoding="latin-1") as read_upcoming:  # Latin-1 encoding for "ñ" and other latin characters in track/GP names.
                responses = read_upcoming.readlines()

        upcoming_embed = discord.Embed(
            title=responses[0],
            description=responses[1],
            colour=0xe74c3c
        )

        # upcoming_embed.set_footer(text=f"Times displayed are track times [{responses[8][:-1]}]")
        upcoming_embed.set_image(
            url=responses[9])
        upcoming_embed.set_thumbnail(
            url=responses[7])
        upcoming_embed.set_author(
            name=f"► F1 Schedule {now.year} | Upcoming",
            icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/F1.svg/1280px-F1.svg.png"
        )

        # Setting up timezone adjustments [absolute]
        start_date = responses[11]

        dates = pd.date_range(start=start_date,
                              periods=3).date.tolist()  # Generate range of dates from start date (race weekend period) - convert to list from class method.

        times = [time.split("-")[0].strip() for time in
                 responses[2:7]]  # Slice reponses to get session times and get starting time (without whitespaces).

        fp1_time = datetime.datetime.strptime(f"{dates[0]} {times[0]}",
                                              "%Y-%m-%d %H:%M")  # Convert to datetime object from start time string
        fp2_time = datetime.datetime.strptime(f"{dates[0]} {times[1]}", "%Y-%m-%d %H:%M")
        fp3_time = datetime.datetime.strptime(f"{dates[1]} {times[2]}", "%Y-%m-%d %H:%M")
        qualifying_time = datetime.datetime.strptime(f"{dates[1]} {times[3]}", "%Y-%m-%d %H:%M")
        race_time = datetime.datetime.strptime(f"{dates[2]} {times[4]}", "%Y-%m-%d %H:%M")

        upcoming_embed.add_field(name=f"**FP1 | {fp1_time.strftime('%a').upper()}**", value=f"`{responses[2]}`",
                                 inline=True)
        upcoming_embed.add_field(name=f"**FP2 | {fp2_time.strftime('%a').upper()}**", value=f"`{responses[3]}`",
                                 inline=True)
        upcoming_embed.add_field(name=f"**FP3 | {fp3_time.strftime('%a').upper()}**", value=f"`{responses[4]}`",
                                 inline=True)
        upcoming_embed.add_field(name=f"**Qualifying | {qualifying_time.strftime('%a').upper()}**",
                                 value=f"`{responses[5]}`", inline=True)
        upcoming_embed.add_field(name=f"**Race | {race_time.strftime('%a').upper()}**", value=f"`{responses[6]}`",
                                 inline=True)
        upcoming_embed.add_field(name=f"[Track Time]",
                                 value=f"{str(responses[12][:-1]).split('/')[1]} | {responses[8][:-1]}", inline=True)

        # Getting track info
        with open("tracks.txt", "r+", encoding="utf-8") as read_tracks:
            lines_n = read_tracks.readlines()

        lines = []

        for line in lines_n:
            lines.append(line[:-1])  # Get rid of the newline escape sequence.

        tracks = []  # Get a list of all tracks

        for line in lines[1::11]:
            tracks.append(line)

        index = 11 * tracks.index(responses[10][:-1])
        info = ""

        info += f"**First Grand Prix**: `{lines[index + 5]}`\n"
        info += f"**Number of Laps**: `{lines[index + 6]}`\n"
        info += f"**Circuit Length**: `{lines[index + 7]}km`\n"
        info += f"**Race Distance**: `{lines[index + 8]}km`\n"
        info += f"**Lap Record**: `{lines[index + 9]}` {lines[index + 10]}\n"

        upcoming_embed.add_field(name="───Track Info:───", value=f"{info}\n**{responses[10].rstrip()}:**", inline=False)

        msg = await ctx.fetch_message(user_id)
        await msg.edit(embed=upcoming_embed)

        try:
            await ctx.message.delete()  # Delete user's message after execution
        except:
            pass

    @commands.command(brief="Displays the upcoming race", description="Provides the full details on the next F1 Grand Prix.")
    async def upcoming(self, ctx):

        global prefixes

        with open("timezones.json", "r") as user_timezones:
            timezones_dict = json.load(user_timezones)

        try:
            with open("upcoming.txt", "r+", encoding="utf-8") as read_upcoming:  # Open the upcoming.txt and create a list with each line to substitute into each embed field.
                responses = read_upcoming.readlines()
        except:
            with open("upcoming.txt", "r+", encoding="latin-1") as read_upcoming:  # Latin-1 encoding for "ñ" and other latin characters in track/GP names.
                responses = read_upcoming.readlines()

        # Setting up timezone adjustments

        time_format = "%H:%M"  # Time format (hours:minutes)
        start_date = responses[11]
        track_timezone = pytz.timezone(responses[12][:-1])  # Set track timezone using pytz (without newline).

        dates = pd.date_range(start=start_date, periods=3).date.tolist()  # Generate range of dates from start date (race weekend period) - convert to list from class method.

        times = [time.split("-")[0].strip() for time in responses[2:7]]  # Slice reponses to get session times and get starting time (without whitespaces).

        fp1_time = datetime.datetime.strptime(f"{dates[0]} {times[0]}", "%Y-%m-%d %H:%M")  # Convert to datetime object from start time string
        fp2_time = datetime.datetime.strptime(f"{dates[0]} {times[1]}", "%Y-%m-%d %H:%M")
        fp3_time = datetime.datetime.strptime(f"{dates[1]} {times[2]}", "%Y-%m-%d %H:%M")
        qualifying_time = datetime.datetime.strptime(f"{dates[1]} {times[3]}", "%Y-%m-%d %H:%M")
        race_time = datetime.datetime.strptime(f"{dates[2]} {times[4]}", "%Y-%m-%d %H:%M")

        print(f"{fp1_time} | {fp2_time} | {fp3_time} | {qualifying_time} | {race_time}")

        if str(ctx.author.id) in timezones_dict:  # If user has set their timezone.

            user_timezone = pytz.timezone(timezones_dict[str(ctx.author.id)])

            # Localise track time to track's timezone and convert to user's timezone.
            user_fp1 = track_timezone.localize(fp1_time).astimezone(user_timezone)
            user_fp2 = track_timezone.localize(fp2_time).astimezone(user_timezone)
            user_fp3 = track_timezone.localize(fp3_time).astimezone(user_timezone)
            user_qualifying = track_timezone.localize(qualifying_time).astimezone(user_timezone)
            user_race = track_timezone.localize(race_time).astimezone(user_timezone)

            print(f"{user_fp1} | {user_fp2} | {user_fp3} | {user_qualifying} | {user_race}")

        # Upcoming embed, using responses list.
        upcoming_embed = discord.Embed(
            title=responses[0],
            description=responses[1],
            colour=0xe74c3c
        )

        with open("tracks.txt", "r+", encoding="utf-8") as read_tracks:
            lines_n = read_tracks.readlines()

        lines = []

        for line in lines_n:
            lines.append(line[:-1])  # Get rid of the newline escape sequence.

        tracks = []  # Get a list of all tracks

        for line in lines[1::11]:
            tracks.append(line)

        index = 11 * tracks.index(responses[10][:-1])
        info = ""

        info += f"**First Grand Prix**: `{lines[index + 5]}`\n"
        info += f"**Number of Laps**: `{lines[index + 6]}`\n"
        info += f"**Circuit Length**: `{lines[index + 7]}km`\n"
        info += f"**Race Distance**: `{lines[index + 8]}km`\n"
        info += f"**Lap Record**: `{lines[index + 9]}` {lines[index + 10]}\n"

        upcoming_embed.set_image(
            url=responses[9])
        upcoming_embed.set_thumbnail(
            url=responses[7])
        upcoming_embed.set_author(
            name="► F1 Schedule 2020 | Upcoming",
            icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/F1.svg/1280px-F1.svg.png"
        )
        upcoming_embed.add_field(name=f"**FP1 | {fp1_time.strftime('%a').upper()}**", value=f"`{responses[2]}`", inline=True)
        upcoming_embed.add_field(name=f"**FP2 | {fp2_time.strftime('%a').upper()}**", value=f"`{responses[3]}`", inline=True)
        upcoming_embed.add_field(name=f"**FP3 | {fp3_time.strftime('%a').upper()}**", value=f"`{responses[4]}`", inline=True)
        upcoming_embed.add_field(name=f"**Qualifying | {qualifying_time.strftime('%a').upper()}**", value=f"`{responses[5]}`", inline=True)
        upcoming_embed.add_field(name=f"**Race | {race_time.strftime('%a').upper()}**", value=f"`{responses[6]}`", inline=True)
        upcoming_embed.add_field(name=f"[Track Time]", value=f"{str(responses[12][:-1]).split('/')[1]} | {responses[8][:-1]}", inline=True)

        upcoming_embed.add_field(name="───Track Info:───", value=f"{info}\n**{responses[10].rstrip()}:**", inline=False)

        if str(ctx.author.id) in timezones_dict:  # If user has set their timezone.
            upcoming_embed.set_footer(text=f"React to convert track times to your local time [clock emoji].")

        # upcoming_embed.set_footer(text=f"Times displayed are track times [{responses[8][:-1]}]")

        track_time_embed = await ctx.send(embed=upcoming_embed)

        if str(ctx.author.id) in timezones_dict:

            def check(react, user):  # Check if reacted to
                return str(react.emoji) in reaction_emoji_list and user == ctx.message.author

            while True:
                await track_time_embed.add_reaction(emoji='\U0001F3CE')  # Racecar reaction [Track time]
                await track_time_embed.add_reaction(emoji='\U0001F552')  # Clock reaction [Local time]

                reaction_emoji_list = ['\U0001F3CE', '\U0001F552']

                try:
                    reacting, confirm_user = await ctx.bot.wait_for('reaction_add', timeout=180.0, check=check)
                except asyncio.TimeoutError:
                    break

                if reacting.emoji == "\U0001F3CE":
                    await track_time_embed.edit(embed=upcoming_embed)

                elif reacting.emoji == "\U0001F552":
                    local_upcoming_embed = discord.Embed(
                        title=responses[0],
                        description=responses[1],
                        colour=0xe74c3c
                    )
                    local_upcoming_embed.set_image(
                        url=responses[9])
                    local_upcoming_embed.set_thumbnail(
                        url=responses[7])
                    local_upcoming_embed.set_author(
                        name="► F1 Schedule 2020 | Upcoming",
                        icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/F1.svg/1280px-F1.svg.png"
                    )

                    # Adjusting session times to user's local time.
                    hour_half = timedelta(hours=1.5)
                    hour = timedelta(hours=1)
                    two_hours = timedelta(hours=2)

                    local_upcoming_embed.add_field(name=f"**FP1 | {user_fp1.strftime('%a').upper()}**", value=f"`{user_fp1.strftime(time_format)} - {(user_fp1 + hour_half).strftime('%H:%M')}`", inline=True)
                    local_upcoming_embed.add_field(name=f"**FP2 | {user_fp2.strftime('%a').upper()}**", value=f"`{user_fp2.strftime(time_format)} - {(user_fp2 + hour_half).strftime('%H:%M')}`", inline=True)
                    local_upcoming_embed.add_field(name=f"**FP3 | {user_fp3.strftime('%a').upper()}**", value=f"`{user_fp3.strftime(time_format)} - {(user_fp3 + hour).strftime('%H:%M')}`", inline=True)
                    local_upcoming_embed.add_field(name=f"**Qualifying | {user_qualifying.strftime('%a').upper()}**", value=f"`{user_qualifying.strftime(time_format)} - {(user_qualifying + hour).strftime('%H:%M')}`", inline=True)
                    local_upcoming_embed.add_field(name=f"**Race | {user_race.strftime('%a').upper()}**", value=f"`{user_race.strftime(time_format)} - {(user_race + two_hours).strftime('%H:%M')}`", inline=True)

                    try:
                        local_upcoming_embed.add_field(name=f"[Local Time]", value=str(timezones_dict[str(ctx.author.id)]).split('/')[1], inline=True)
                    except:
                        local_upcoming_embed.add_field(name=f"[Local Time]",
                                                       value=str(timezones_dict[str(ctx.author.id)]).split('/')[0],
                                                       inline=True)

                    local_upcoming_embed.add_field(name="───Track Info:───", value=f"{info}\n**{responses[10].rstrip()}:**", inline=False)

                    local_upcoming_embed.set_footer(text="React to convert local time back to track time [racecar emoji].")

                    # local_time_str = f"Times displayed are local times | {str(timezones_dict[str(ctx.author.id)])}\n"

                    await track_time_embed.edit(embed=local_upcoming_embed)

                else:
                    continue

    # F1 Info
    @commands.command(brief="Provides information on a given circuit", description="Displays detailed circuit information from given track/country.", usage="[circuit name/country]", aliases=["circuit"])
    async def track(self, ctx, *, circuit=None):

        global prefixes

        if circuit is None:
            error_embed = discord.Embed(  # Error embed
                title="Error!",
                colour=0xe74c3c
            )
            error_embed.add_field(
                name="No track provided!.",
                value=f"`{prefixes[str(ctx.guild.id)][0]}track [circuit name/country]`",
                inline=False
            )
            error_embed.set_footer(
                text=f"To view the all the available circuits, type {prefixes[str(ctx.guild.id)][0]}tracks."
            )
            await ctx.send(embed=error_embed)
            return

        with open("tracks.txt", "r+", encoding="utf-8") as read_tracks:
            lines_n = read_tracks.readlines()

        lines = []

        for line in lines_n:
            lines.append(line[:-1])  # Get rid of the newline escape sequence.

        tracks = []  # Get a list of all tracks

        for line in lines[::11]:
            tracks.append(line)

        print(tracks)

        # Validate whether or not a circuit has been found (and ensure there aren't overlapping search terms).
        indices = [i for i, s in enumerate(lines[::11]) if circuit.lower() in s.lower()]

        if len(indices) != 1:  # If more than one track is identified (or none)
            # Set error messages depending on count
            if len(indices) > 1:
                error_string = "Too vague of a track input! Please try again..."
            else:
                error_string = "No track found! Please try again..."

            error_embed = discord.Embed(  # Error embed
                title="Error!",
                colour=0xe74c3c
            )
            error_embed.add_field(
                name=error_string,
                value=f"`{prefixes[str(ctx.guild.id)][0]}track [circuit name/country]`",
                inline=False
            )
            error_embed.set_footer(
                text=f"To view the all the available tracks, type {prefixes[str(ctx.guild.id)][0]}tracks."
            )
            await ctx.send(embed=error_embed)
            return

        index = 11 * indices[0]  # Align the index with the full tracks.txt file

        # Track Embed
        track_embed = discord.Embed(
            title=lines[index+1],
            description=lines[index+2],
            colour=0xe74c3c
        )

        print(lines[index+4])

        track_embed.set_footer(text=f"Last updated: 14/08/2020")
        track_embed.set_image(
            url=str(lines[index+4]))
        track_embed.set_thumbnail(
            url=str(lines[index+3]))
        track_embed.set_author(
            name="► F1 2020 | Circuits",
            icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/F1.svg/1280px-F1.svg.png"
        )

        info = ""

        info += f"**First Grand Prix**: `{lines[index+5]}`\n"
        info += f"**Number of Laps**: `{lines[index+6]}`\n"
        info += f"**Circuit Length**: `{lines[index+7]}km`\n"
        info += f"**Race Distance**: `{lines[index+8]}km`\n"
        info += f"**Lap Record**: `{lines[index+9]}` {lines[index+10]}\n"

        track_embed.add_field(name="───Track Info:───", value=info, inline=False)

        await ctx.send(embed=track_embed)

    @commands.command(brief="Displays all available circuits", description=f"Displays all circuits on the F1 calendar {[now.year]}")
    async def tracks(self, ctx):

        global prefixes

        with open("tracks.txt", "r+", encoding="utf-8") as read_tracks:
            lines_n = read_tracks.readlines()

        lines = []

        for line in lines_n:
            lines.append(line[:-1])  # Get rid of the newline escape sequence.

        tracks = ""  # Get a string of all the available tracks.

        for line in lines[::11]:
            tracks += f"`{line}`\n"

        track_embed = discord.Embed(
            description=tracks,
            colour=0xe74c3c

        )

        track_embed.set_footer(text=f"Last updated: 14/08/2020")
        track_embed.set_author(
            name="► F1 2020 | Circuits",
            icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/F1.svg/1280px-F1.svg.png"
        )

        await ctx.send(embed=track_embed)


def setup(bot):
    bot.add_cog(F1(bot))
