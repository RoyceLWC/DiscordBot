import asyncio
import os
import json

import discord
from discord.ext.commands import has_permissions
from discord.ext import commands
from discord.ext.commands import Bot

colours = {
    'DEFAULT': 0x000000,
    'WHITE': 0xFFFFFF,
    'AQUA': 0x1ABC9C,
    'GREEN': 0x2ECC71,
    'BLUE': 0x3498DB,
    'PURPLE': 0x9B59B6,
    'LUMINOUS_VIVID_PINK': 0xE91E63,
    'GOLD': 0xF1C40F,
    'ORANGE': 0xE67E22,
    'RED': 0xE74C3C,
    'GREY': 0x95A5A6,
    'NAVY': 0x34495E,
    'DARK_AQUA': 0x11806A,
    'DARK_GREEN': 0x1F8B4C,
    'DARK_BLUE': 0x206694,
    'DARK_PURPLE': 0x71368A,
    'DARK_VIVID_PINK': 0xAD1457,
    'DARK_GOLD': 0xC27C0E,
    'DARK_ORANGE': 0xA84300,
    'DARK_RED': 0x992D22,
    'DARK_GREY': 0x979C9F,
    'DARKER_GREY': 0x7F8C8D,
    'LIGHT_GREY': 0xBCC0C0,
    'DARK_NAVY': 0x2C3E50,
    'BLURPLE': 0x7289DA,
    'GREYPLE': 0x99AAB5,
    'DARK_BUT_NOT_BLACK': 0x2C2F33,
    'NOT_QUITE_BLACK': 0x23272A
}


# Get prefix per server
def get_prefix(client, message):
    with open("prefixes.json", "r") as f:
        r_prefixes = json.load(f)

    return commands.when_mentioned_or(*r_prefixes[str(message.guild.id)])(client,
                                                                          message)  # *Prevent list of lists from callable


client = discord.Client()
client = Bot(command_prefix=get_prefix)

with open("prefixes.json", "r") as read_prefix:
    prefixes = json.load(read_prefix)


# Brief = Command descriptor
# Description - Full text displayed after specified cog/command.
@client.command(brief=f"Changes or shows the current prefix",
                description="Changes or shows the server's current prefix",
                aliases=["setprefix", "pref"],
                usage="<prefix>")
async def prefix(ctx, *, pref=None):
    global prefixes, multiple

    def check(react, user):  # Check if reacted to
        return str(react.emoji) in reaction_emoji_list and user == ctx.message.author

    if pref is None:  # No prefix provided, display prefix list

        display_prefix_list = ""

        for p in prefixes[str(ctx.guild.id)]:  # Go through each prefix that belongs to the server
            display_prefix_list += f"`{p}`\n"

        display_embed = discord.Embed(  # No prefix change - info
            title="Prefix list:",
            description=f"<@{client.user.id}>\n{display_prefix_list}",
            colour=0x7289DA
        )

        await ctx.send(embed=display_embed)
        return

    if prefixes[str(ctx.guild.id)] == ["+"]:  # Default prefix ('+')
        prefix_embed = discord.Embed(
            title=f"Default prefix: `+`",
            description=f"Replace default prefix with `{pref}` or add it as an extra prefix?",
            colour=0x7289DA
        )

    else:
        if len(prefixes[str(ctx.guild.id)]) > 2:  # More than one custom prefix

            multiple = True
            display_prefix_list = ""

            for p in prefixes[str(ctx.guild.id)][:-1]:  # Go through each prefix that belongs to the server

                if p != "+":  # Remove default prefix
                    display_prefix_list += f"`{p}`, "

            display_prefix_list += f"`{prefixes[str(ctx.guild.id)][-1]}`"

            title = f"There are already pre-existing custom prefixes: {display_prefix_list}"

        else:  # One custom prefix
            multiple = False
            try:
                title = f"There is already a pre-existing custom prefix: `{prefixes[str(ctx.guild.id)][1]}`"
            except:  # If there is only one custom prefix (without default prefix)
                title = f"There is already a pre-existing custom prefix: `{prefixes[str(ctx.guild.id)][0]}`"

        prefix_embed = discord.Embed(
            title=title,
            description=f"Replace prefix with `{pref}` or add as a new extra prefix?",
            colour=0x7289DA
        )

    custom_embed = await ctx.send(embed=prefix_embed)

    await custom_embed.add_reaction(emoji='\U0001f501')  # "Repeat" emoji (overwrite) reaction
    await custom_embed.add_reaction(emoji='\U0001f195')  # "New" emoji (add) reaction

    reaction_emoji_list = ['\U0001f501', '\U0001f195']

    # Team name section of embed (edit)
    try:
        reacting, confirm_user = await ctx.bot.wait_for('reaction_add', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        # If user takes too long - timeout
        error_embed = discord.Embed(  # Error embed
            title="Error!",
            colour=0xe74c3c
        )
        error_embed.add_field(
            name="Timed out! Exiting setup...",
            value=f"`{prefixes[str(ctx.guild.id)]}prefix [new prefix]`",
            inline=False
        )
        await ctx.send(embed=error_embed)
        return

    if reacting.emoji == "\U0001f501":  # If the .emoji is the overwrite reaction...
        try:
            if multiple:  # If there are more than one custom prefixes
                multiple_embed = discord.Embed(
                    title="Multiple custom prefixes...",
                    description="Which prefix would you like to override?",
                    colour=0xe74c3c
                )

                lined_prefix_list = ""

                for p in prefixes[str(ctx.guild.id)]:  # Go through each prefix that belongs to the server
                    lined_prefix_list += f"`{p}`\n"

                multiple_embed.add_field(
                    name="Prefix list:",
                    value=f"<@{client.user.id}>\n{lined_prefix_list}",
                    inline=False
                )

                await ctx.send(embed=multiple_embed)

                try:
                    response = await ctx.bot.wait_for('message', timeout=90.0, check=lambda
                            message: message.author == ctx.author)  # Receive an input (check if it's the same user).
                    response = response.content
                except:
                    # If user takes too long - timeout
                    error_embed = discord.Embed(  # Error embed
                        title="Error | Timed out",
                        description=f"`{prefixes[str(ctx.guild.id)][0]}prefix [prefix]`",
                        colour=0xe74c3c
                    )
                    await ctx.send(embed=error_embed)
                    return

                if response in prefixes[str(ctx.guild.id)]:
                    prefixes[str(ctx.guild.id)] = [p.replace(response, pref) if p == response else p for p in prefixes[str(ctx.guild.id)]]
                else:
                    error_embed = discord.Embed(  # Error embed
                        title="Error | No matching prefix found",
                        colour=0xe74c3c
                    )

                    error_embed.add_field(  # No prefix change - info
                        name="Prefix list:",
                        value=f"<@{client.user.id}>\n{lined_prefix_list}",
                        inline=False
                    )

                    await ctx.send(embed=error_embed)
                    return

                set_prefix_embed = discord.Embed(
                    description=f" Prefix `{response}` overwritten [Server ID: {ctx.guild.id}]",
                    colour=0x7289DA
                )

            else:
                prefixes[str(ctx.guild.id)] = pref  # Change key-value to user's prefix input

                set_prefix_embed = discord.Embed(
                    description=f" Prefix `{prefixes[str(ctx.guild.id)][0]}` overwritten [Server ID: {ctx.guild.id}]",
                    colour=0x7289DA
                )
        except:  # No custom prefixes
            prefixes[str(ctx.guild.id)] = pref  # Change key-value to user's prefix input

            set_prefix_embed = discord.Embed(
                description=f" Prefix `{prefixes[str(ctx.guild.id)][0]}` overwritten [Server ID: {ctx.guild.id}]",
                colour=0x7289DA
            )

    elif reacting.emoji == '\U0001f195':

        prefixes[str(ctx.guild.id)].append(pref)  # Append prefix to key in dictionary (list)

        prefix_list_str = ""

        for added_prefix in prefixes[str(ctx.guild.id)]:  # Loop through each prefix in the added list
            prefix_list_str += f"`{added_prefix}`\n"

        set_prefix_embed = discord.Embed(  # Add-on embed
            title="Prefix added!",
            colour=0x7289DA
        )

        set_prefix_embed.add_field(
            name="Prefix list:",
            value=f"<@{client.user.id}>\n{prefix_list_str}",
            inline=False
        )
    else:
        retracted_embed = discord.Embed(  # Error embed
            description="Prefix change retracted",
            colour=0xe74c3c
        )
        await ctx.send(embed=retracted_embed)
        return

    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f, indent=4)

    await ctx.send(embed=set_prefix_embed)


@client.command(brief=f"Deletes a pre-existing prefix",
                description="Deletes a pre-existing prefix from the list",
                aliases=["delprefix", "delpref"],
                usage="[prefix]")
async def deleteprefix(ctx, *, pref=None):
    global prefixes

    if pref is None:
        error_embed = discord.Embed(  # Error embed
            title="Error!",
            colour=0xe74c3c
        )
        error_embed.add_field(
            name="No prefix provided!",
            value=f"`{prefixes[str(ctx.guild.id)][0]}delprefix [prefix]`",
            inline=False
        )

        await ctx.send(embed=error_embed)
        return

    if len(prefixes[str(ctx.guild.id)]) != 1:
        if pref in prefixes[str(ctx.guild.id)]:
            prefixes[str(ctx.guild.id)].remove(pref)  # Remove specified element from prefix list

            with open("prefixes.json", "w") as f:
                json.dump(prefixes, f, indent=4)

            delete_prefix_embed = discord.Embed(
                description=f"Prefix `{pref}` removed",
                colour=0x7289DA
            )

            await ctx.send(embed=delete_prefix_embed)

        else:

            error_embed = discord.Embed(  # Error embed
                title="Error | No matching prefix found",
                colour=0xe74c3c
            )

            display_prefix_list = ""

            for p in prefixes[str(ctx.guild.id)]:  # Go through each prefix that belongs to the server
                display_prefix_list += f"`{p}`\n"

            error_embed.add_field(  # No prefix change - info
                name="Prefix list:",
                value=f"<@{client.user.id}>\n{display_prefix_list}",
                inline=False
            )

            await ctx.send(embed=error_embed)
            return

    else:
        error_embed = discord.Embed(  # Error embed
            title="Error!",
            colour=0xe74c3c
        )
        error_embed.add_field(
            name="Only one default prefix present",
            value=f"Add an extra custom prefix first: `{prefixes[str(ctx.guild.id)][0]}prefix [prefix]`",
            inline=False
        )

        await ctx.send(embed=error_embed)
        return


cog_count = 0

# Initialising a dictionary with each cog's status (loaded/unloaded)
cog_status = {
    "f1": False,
    "fun": False,
    "moderation": False,
    "music": False,
    "utility": False
}

# Get a list of all cogs
cogs_list = []

for filename in os.listdir("./cogs")[0:len(cogs_list) - 1]:
    filename = filename[:-3]  # Index slicing to remove .py
    cogs_list.append(filename)


def is_me():  # Creates a function decorator "@is_me()" that acts as a check().

    def predicate(ctx):
        return ctx.message.author.id == 338406004356022283  # Royce's User ID

    return commands.check(predicate)


@client.command(brief="Displays information about the server",
                description="Displays an informative embed about the current server.", aliases=["server"])
async def serverinfo(ctx):
    global prefixes

    server_id = ctx.guild.id

    server_info_embed = discord.Embed(
        title="Server Info:",
        colour=0x7289DA
    )

    # Author - Server name and region
    server_info_embed.set_author(
        name=f"{ctx.guild.name} | {str(ctx.guild.region).capitalize()}",
        icon_url=ctx.guild.icon_url
    )

    # Owner
    server_info_embed.add_field(
        name="Owner",
        value=f"<@{ctx.guild.owner.id}>\n{ctx.guild.owner}",
        inline=True
    )

    # Prefix(es)
    display_prefix_list = ""

    for p in prefixes[str(ctx.guild.id)]:  # Go through each prefix that belongs to the server
        display_prefix_list += f"`{p}`\n"

    server_info_embed.add_field(  # No prefix change - info
        name="Prefixes",
        value=f"<@{client.user.id}>\n{display_prefix_list}",
        inline=True
    )

    # Boosts
    level = ctx.guild.premium_tier
    boosts = ctx.guild.premium_subscription_count

    if level == 0:
        out_of = 2
    elif level == 1:
        out_of = 15
    elif level == 2 or level == 3:
        out_of = 30
    else:
        out_of = 0

    server_info_embed.add_field(
        name="Boosts",
        value=f"Level {level}\n{boosts}/{out_of} boosts",
        inline=True
    )

    # Channels
    categories = ctx.guild.categories
    text_channels = ctx.guild.text_channels
    voice_channels = ctx.guild.voice_channels

    # - Locked Channels
    locked_text_channels = 0
    locked_voice_channels = 0

    for text in text_channels:
        # Return bool of @everyone's permission to read messages of each text channel object (None if neutral).
        read_messages = text.overwrites_for(ctx.guild.default_role).read_messages

        if not read_messages and read_messages is not None:  # If @everyone can't view channel (Strictly false - Locked)
            locked_text_channels += 1  # Add 1 to the total locked channel count

    for voice in voice_channels:
        # Return bool of @everyone's permission to view each voice channel (object - .Permissions)
        connect_permission = voice.overwrites_for(ctx.guild.default_role).connect

        if not connect_permission and connect_permission is not None:  # If @everyone can't connect to channel (False - Locked)
            locked_voice_channels += 1

    server_info_embed.add_field(
        name="Channels",
        value=f"[Categories: {len(categories)}]\n**Text:** {len(text_channels)} ({locked_text_channels} locked)\n**Voice:** {len(voice_channels)} ({locked_voice_channels} locked)",
        inline=True
    )

    # Roles
    roles = ctx.guild.roles  # List of server's roles in hierarchy order - List[Role]

    server_info_embed.add_field(
        name="Roles",
        value=str(len(roles)),
        inline=True
    )

    # Members
    members_list = ctx.guild.members
    member_count = len(members_list)  # Includes bots
    true_member_count = len([m for m in ctx.guild.members if not m.bot])  # Doesn't include bots
    bot_count = len([m for m in ctx.guild.members if m.bot])  # Only bots

    status_keys = ["Online", "Away", "Do Not Disturb", "Offline"]
    status_dict = {key: 0 for key in status_keys}

    for member in members_list:
        # Use class discord.Status to determine each member's status
        if member.status == discord.Status.online:
            status_dict["Online"] += 1
        elif member.status == discord.Status.idle:
            status_dict["Away"] += 1
        elif member.status == discord.Status.dnd:
            status_dict["Do Not Disturb"] += 1
        elif member.status == discord.Status.offline:
            status_dict["Offline"] += 1

    server_info_embed.add_field(
        name="Members",
        value=f""":green_circle: {status_dict['Online']} :yellow_circle: {status_dict['Away']} :red_circle: {
        status_dict['Do Not Disturb']} :black_circle: {status_dict['Offline']}
            **Total:** {member_count}
            **Humans:** {true_member_count}
            **Bots:** {bot_count}""",
        inline=True
    )

    # Thumbnail
    server_info_embed.set_thumbnail(url=ctx.guild.icon_url)

    # Footer - ID / Date created
    creation_date = ctx.guild.created_at

    server_info_embed.set_footer(
        text=f"ID: {server_id} | Created • {creation_date.strftime('%A')}, {creation_date.strftime('%B %d %Y').lstrip('0').replace(' 0',' ')} {creation_date.strftime('%I:%M %p')}"
    )

    await ctx.send(embed=server_info_embed)


@client.command(brief="Shows available cogs", description="Shows all the available cogs/extensions that are (un)loadable.")
async def cogs(ctx):
    global prefixes, cogs_list

    cogs_embed = discord.Embed(
        title=f"Cogs",
        colour=colours["BLURPLE"]
    )

    cogs_embed.set_footer(
        text=f"Requested by {ctx.message.author.name}",
        icon_url=client.user.avatar_url
    )

    available_cogs = ""

    for cog in cogs_list:
        available_cogs += f"`{cog}`\n"

    cogs_embed.add_field(
        name="Available cogs:",
        value=available_cogs,
        inline=False
    )
    extra_help = discord.Embed(
        color=colours["BLURPLE"]
    )
    extra_help.add_field(
        name="To view each cog's commands, ensure the cog is loaded and use:",
        value=f"`{prefixes[str(ctx.guild.id)][0]}nhelp [cog]`",
        inline=False
    )

    await ctx.send(embed=cogs_embed)
    await ctx.send(embed=extra_help)


@client.command(brief="Shows the current status of each cog",
                description="Shows the current status of each cog [loaded/unloaded].", aliases=["cogstatus", "stat"])
async def status(ctx):
    global prefixes

    status_embed = discord.Embed(
        title="Cog status:",
        colour=0x7289DA
    )

    loaded = ""
    unloaded = ""

    for cog in cog_status:
        if cog_status[cog]:
            loaded += f"`{cog}`\n"
        else:
            unloaded += f"`{cog}`\n"

    if loaded != "":
        status_embed.add_field(
            name=f":white_check_mark: __*Loaded:*__",
            value=loaded,
            inline=True
        )

    if unloaded != "":
        status_embed.add_field(
            name=f":x: __*Unloaded:*__",
            value=unloaded,
            inline=True
        )

    status_embed.set_footer(
        text=f"Load/unload cogs using '{prefixes[str(ctx.guild.id)][0]}load'/'{prefixes[str(ctx.guild.id)][0]}unload'")

    await ctx.send(embed=status_embed)


@client.command(brief="Loads cogs", description="Loads (all) cogs or a specified cog in order to be used.", usage="[cog/'all']")
@is_me()
async def load(ctx, extension):
    global cog_count, cog_status, cogs_list

    if extension == "all":
        # Setting variable to check if all cogs are already loaded
        loaded = 0

        # Go to the /cogs directory and load each one.
        for file in os.listdir("./cogs")[
                    0:len(os.listdir("./cogs")) - 1]:  # Load all except the last file (__pycach)

            if file.startswith("song"):
                pass

            else:
                if not cog_status[file[:-3]]:
                    client.load_extension(f"cogs.{file[:-3]}")
                    cog_count += 1  # Add 1 (total) to the cog count to indicate how many cogs have been loaded.

                elif cog_status[file[:-3]]:
                    loaded += 1
                else:
                    continue

        if loaded != 5:
            status_embed = discord.Embed(
                title="Cog status:",
                colour=0x7289DA
            )

            # Loop through each value and set it to True (loaded) and add to its respective field.
            loaded = ""
            for cog in cog_status:
                cog_status[cog] = True
                loaded += f"`{cog}`\n"

            status_embed.add_field(
                name=f":white_check_mark: __*Loaded:*__",
                value=loaded,
                inline=True
            )

            status_embed.set_author(
                name="All cogs have been loaded",
                icon_url="https://i.imgur.com/Elzmh5o.png"
            )

            await ctx.send(embed=status_embed)

        else:
            error_embed = discord.Embed(
                description=f"All cogs have already been loaded!",
                colour=0xe74c3c
            )

            await ctx.send(embed=error_embed)

    else:
        try:
            client.load_extension(f"cogs.{extension}")
            cog_status[extension] = True  # Set the cog's value to True (loaded)
            cog_count += 1

            status_embed = discord.Embed(
                title="Cog status:",
                colour=0x7289DA
            )

            loaded = ""
            unloaded = ""

            for cog in cog_status:
                if cog_status[cog]:
                    loaded += f"`{cog}`\n"
                else:
                    unloaded += f"`{cog}`\n"

            if loaded != "":  # Check if there are any loaded cogs to add to field
                status_embed.add_field(
                    name=f":white_check_mark: __*Loaded:*__",
                    value=loaded,
                    inline=True
                )

            if unloaded != "":  # Check if there are any unloaded cogs to add to field
                status_embed.add_field(
                    name=f":x: __*Unloaded:*__",
                    value=unloaded,
                    inline=True
                )

            status_embed.set_author(
                name=f"{extension.capitalize()} cog has been loaded",
                icon_url="https://i.imgur.com/Elzmh5o.png"
            )

            await ctx.send(embed=status_embed)

        except:
            if extension in cog_status:  # If cog exists, but is already loaded
                error_embed = discord.Embed(
                    description=f"`{extension}` has already been loaded!",
                    colour=0xe74c3c
                )

                await ctx.send(embed=error_embed)

            else:  # If cog not found
                error_embed = discord.Embed(
                    title="Error!",
                    description="Invalid cog!",
                    colour=0xe74c3c
                )

                available_cogs = ""

                for cog in cogs_list:
                    available_cogs += f"`{cog}`\n"

                error_embed.add_field(
                    name="Available cogs:",
                    value=available_cogs,
                    inline=False
                )

                await ctx.send(embed=error_embed)


@client.command(brief="Unloads cogs", description="Unloads (all) cogs or a specified cog to disable it from use.", usage="[cog/'all']")
@is_me()
async def unload(ctx, extension):  # Extension = Cog
    global cog_count, cog_status, cogs_list

    if extension == "all":
        # Setting variable to check if all cogs are already unloaded
        unloaded = 0

        # Go to the /cogs directory and unload each one.
        for file in os.listdir("./cogs")[
                    0:len(os.listdir("./cogs")) - 1]:  # Unload all except the last file (__pycach)

            if cog_status[file[
                          :-3]]:  # Search dictionary with the filename without .py as the key (rather than looping
                # through dictionary).

                client.unload_extension(f"cogs.{file[:-3]}")
                cog_count -= 1  # Add 1 (total) to the cog count to indicate how many cogs have been loaded.

            elif not cog_status[file[:-3]]:  # If cog is unloaded (False)
                unloaded += 1

            else:
                continue

        if unloaded != 5:
            status_embed = discord.Embed(
                title="Cog status:",
                colour=0x7289DA
            )

            # Loop through each value and set it to False (unloaded) and add to its respective field.
            unloaded = ""

            for cog in cog_status:
                cog_status[cog] = False
                unloaded += f"`{cog}`\n"

            status_embed.add_field(
                name=f":x: __*Unloaded:*__",
                value=unloaded,
                inline=True
            )

            status_embed.set_author(
                name="All cogs have been unloaded",
                icon_url="https://i.imgur.com/Elzmh5o.png"
            )

            await ctx.send(embed=status_embed)

        else:
            error_embed = discord.Embed(
                description=f"All cogs have already been unloaded!",
                colour=0xe74c3c
            )

            await ctx.send(embed=error_embed)

    else:
        try:
            client.unload_extension(f"cogs.{extension}")
            cog_status[extension] = False  # Set the cog's value to False (unloaded).
            cog_count -= 1

            status_embed = discord.Embed(
                title="Cog status:",
                colour=0x7289DA
            )

            loaded = ""
            unloaded = ""
            for cog in cog_status:
                if cog_status[cog]:
                    loaded += f"`{cog}`\n"
                else:
                    unloaded += f"`{cog}`\n"

            if loaded != "":
                status_embed.add_field(
                    name=f":white_check_mark: __*Loaded:*__",
                    value=loaded,
                    inline=True
                )

            if unloaded != "":
                status_embed.add_field(
                    name=f":x: __*Unloaded:*__",
                    value=unloaded,
                    inline=True
                )

            status_embed.set_author(
                name=f"{extension.capitalize()} cog has been unloaded",
                icon_url="https://i.imgur.com/Elzmh5o.png"
            )

            await ctx.send(embed=status_embed)

        except:
            if extension in cog_status:
                error_embed = discord.Embed(
                    description=f"`{extension}` has already been unloaded!",
                    colour=0xe74c3c
                )

                await ctx.send(embed=error_embed)

            else:
                error_embed = discord.Embed(
                    title="Error!",
                    description="Invalid cog!",
                    colour=0xe74c3c
                )

                available_cogs = ""

                for cog in cogs_list:
                    available_cogs += f"`{cog}`\n"

                error_embed.add_field(
                    name="Available cogs:",
                    value=available_cogs,
                    inline=False
                )

                await ctx.send(embed=error_embed)


# Rules (Embed)
@client.command(brief="Displays an ideal rule-set or specific rule if given",
                description="Displays an embed containing standard rules or a specific rule if a rule number is given.",
                aliases=["rule"], usage="<num>")
@has_permissions(manage_messages=True)  # Validate permissions of the user
async def rules(ctx, *, num=None):
    global prefixes

    # Initialising embed
    rules_embed = discord.Embed(
        title=f"Discord Rules",  # Specified cog title (or general).
        colour=0x7289DA
    )

    with open("rules.txt", "r", encoding="utf-8") as rule:  # Open rules.txt
        rules_text = rule.readlines()

    headings = []

    for rule in range(0, len(rules_text) - 1,
                      2):  # Go through every second index (heading) and add the heading and rule description to the 2D-array.
        headings.extend([[rules_text[rule], rules_text[rule + 1]]])

    if num is None:  # If no specific rule is provided...
        for x in range(len(headings)):
            rules_embed.add_field(
                name=f"{x + 1}. " + headings[x][0],  # Rules no. with heading
                value=headings[x][1],  # Rule description
                inline=False
            )

        await ctx.send(embed=rules_embed)

        try:
            await ctx.message.delete()
        except:
            pass

    else:  # If specific rule is provided...
        try:
            num = int(num)

            rules_embed.add_field(
                name=f"{num}. " + headings[num - 1][0],
                value=headings[num - 1][1],
                inline=False
            )

            rules_embed.set_footer(
                text=f"Requested by {ctx.message.author.name}",
                icon_url=client.user.avatar_url
            )

            await ctx.send(embed=rules_embed)

        except:
            error_embed = discord.Embed(  # Error embed
                title="Error!",
                colour=colours["BLURPLE"]
            )
            error_embed.add_field(
                name="Invalid rule number provided!",
                value=f"`{prefixes[str(ctx.guild.id)][0]}rules <num>`",
                inline=False
            )

            await ctx.send(embed=error_embed)


# Help (Embed)
@client.command(brief="Shows the more refined help prompt", description="Shows this help prompt; more refined and descriptive.")
async def nhelp(ctx, cog="all"):
    global prefixes

    # Preparing embed
    if cog == "all" or cog.lower() == "general":  # + General commands
        cog_help = "General"
    else:
        cog_help = cog.capitalize()  # Make first letter capital

    help_embed = discord.Embed(
        title=f"Help | {cog_help}",  # Specified cog title (or general).
        colour=0x7289DA
    )

    if cog == "all":
        help_embed.set_footer(
            text=f"Requested by {ctx.message.author.name}",
            icon_url=client.user.avatar_url
        )
    else:
        help_embed.set_footer(
            text=f"Requested by {ctx.message.author.name} | [] = Required, <> = Optional",
            # Add guidance for command usage if provided.
            icon_url=client.user.avatar_url
        )

    if cog == "all":
        all_cog_commands = []  # Cog commands
        general_cog_commands_list = []  # All commands (separated into 5 elements)

        for cog in cogs_list:  # Loop through each cog (outside of the try statement to exclude other unloaded cogs).
            try:
                commands_list = ""
                cog_commands = client.get_cog(cog).get_commands()

                for command in cog_commands:  # Loop through each object command and append the name of the command.
                    commands_list += f"`{command.name}` - *{command.brief}*\n"

                    all_cog_commands.append(command.name)

                general_cog_commands_list.append(commands_list)  # Add the list of commands for each cog to the list (indexed).

            except AttributeError:
                general_cog_commands_list.append(None)

        # General commands
        general_commands = ""
        for command in client.commands:
            if str(command) == "help":  # Compensate for the "help" command (which has None as brief).
                general_commands += f"`{command.name}` - *Shows the basic help prompt*\n"
            elif str(
                    command) not in all_cog_commands:  # Get rid of commands within the cogs (str() needed for
                # all_cog_commands list).
                general_commands += f"`{command.name}` - *{command.brief}*\n"

        general_cog_commands_list.insert(0, general_commands)

        help_embed.add_field(
            name="General",
            value=general_commands,
            inline=False
        )

        # Extra info
        help_embed.add_field(
            name="───────────────",
            value=f"For more information on each cog, use `{prefixes[str(ctx.guild.id)][0]}nhelp [cog]`.",
            inline=False
        )

        initial_help = await ctx.send(embed=help_embed)

        general_cogs_list = [  # Separate list of cogs + general (capitalised)
            "General",
            "F1",
            "Fun",
            "Moderation",
            "Music",
            "Utility"
        ]

        def check(react, user):  # Check if reacted to
            return str(react.emoji) in reaction_emoji_list and user == ctx.message.author

        index = 0

        while True:
            await initial_help.add_reaction(emoji='\U00002b05')  # Left arrow reaction
            await initial_help.add_reaction(emoji='\U000027a1')  # Right arrow reaction

            reaction_emoji_list = ['\U00002b05', '\U000027a1']

            try:
                reacting, confirm_user = await ctx.bot.wait_for('reaction_add', timeout=180.0, check=check)
            except asyncio.TimeoutError:
                break

            if reacting.emoji == "\U00002b05":  # Previous help page
                if index == 0:  # If there isn't a previous page, start the next iteration
                    continue
                else:
                    index -= 1  # Previous index (cog/general)

                    next_help_embed = discord.Embed(
                        title=f"Help | RoyceBot",
                        colour=0x7289DA
                    )

                    if cog_status[general_cogs_list[index].lower()]:  # If the cog is loaded
                        next_help_embed.add_field(
                            name=general_cogs_list[index],
                            value=general_cog_commands_list[index],
                            inline=False
                        )

                    else:
                        next_help_embed.add_field(
                            name=general_cogs_list[index],
                            value=f"This cog is not loaded; please load this cog first to view its commands.\n`{prefixes[str(ctx.guild.id)][0]}load {general_cogs_list[index].lower()}`"
                        )

                    next_help_embed.set_footer(
                        text=f"Page {index + 1}/5 • Requested by {ctx.message.author.name}",
                        icon_url=client.user.avatar_url
                    )

                    await initial_help.edit(embed=next_help_embed)

            elif reacting.emoji == "\U000027a1":  # Next help page
                if index == 5:  # Final page
                    continue
                else:
                    index += 1  # Next index (cog)

                    next_help_embed = discord.Embed(
                        title=f"RoyceBot | Help",
                        colour=0x7289DA
                    )

                    if cog_status[general_cogs_list[index].lower()]:  # If the cog is loaded
                        next_help_embed.add_field(
                            name=general_cogs_list[index],
                            value=general_cog_commands_list[index],
                            inline=False
                        )

                    else:
                        next_help_embed.add_field(
                            name=general_cogs_list[index],
                            value=f"This cog is not loaded; please load this cog first to view its commands.\n`{prefixes[str(ctx.guild.id)][0]}load {general_cogs_list[index].lower()}`"
                        )

                    next_help_embed.set_footer(
                        text=f"Page {index + 1}/6 • Requested by {ctx.message.author.name}",
                        icon_url=client.user.avatar_url
                    )

                    await initial_help.edit(embed=next_help_embed)
            else:
                continue

    else:  # Cog specified...
        try:
            lower_cogs = [cog.lower() for cog in cogs_list]
            lower_cogs_py = [x for x in lower_cogs]  # Get rid of .py (separately).

            if cog.lower() in lower_cogs_py:  # Check if cog exists.
                commands_list = client.get_cog(lower_cogs_py[lower_cogs.index(
                    cog.lower())]).get_commands()  # Cog must be loaded and have its index referenced (without .py)
                # file name.
                help_text = ""

                for command in commands_list:
                    if command.usage is not None:  # Extra space between command and its usage (if there is one)
                        space = " "
                    else:
                        space = ""

                    help_text += f"`{command.name}`\n*{command.description}*\n"

                    # Formatting of command
                    help_text += f"**Format: ** `{prefixes[str(ctx.guild.id)][0]}{command.name}{space}{command.usage if command.usage is not None else ''}`\n"
                    # Name/usage under command via the decorator (parameters) - Return blank if no usage given.

                    # If there are aliases, add them
                    if len(command.aliases) > 0:
                        help_text += f"**Aliases: ** `{'`, `'.join(command.aliases)}`\n\n"
                    else:
                        help_text += "\n"

                help_embed.description = help_text

                await ctx.send(embed=help_embed)

            elif cog.lower() == "general":
                all_cog_commands = []

                for cog in cogs_list:  # Loop through each cog (outside of the try statement to exclude other unloaded cogs).
                    try:
                        cog_commands = client.get_cog(cog[:-3]).get_commands()
                        for cog_name in cog_commands:  # Loop through each object command and append the name of the command.
                            all_cog_commands.append(cog_name.name)

                    except AttributeError:
                        pass

                # General commands
                help_text = ""
                for command in client.commands:
                    if command.usage is not None:
                        space = " "
                    else:
                        space = ""

                    if str(command) not in all_cog_commands and str(command) != "help":
                        help_text += f"`{command.name}`\n*{command.description}*\n"

                        # Formatting of command
                        help_text += f"**Format: ** `{prefixes[str(ctx.guild.id)][0]}{command.name}{space}{command.usage if command.usage is not None else ''}`\n"
                        # Name/usage under command via the decorator (parameters) - Return blank if no usage given.

                        # If there are aliases, add them
                        if len(command.aliases) > 0:
                            help_text += f"**Aliases: ** `{'`, `'.join(command.aliases)}`\n\n"
                        else:
                            help_text += "\n"

                help_embed.description = help_text

                await ctx.send(embed=help_embed)

            else:
                error_embed = discord.Embed(  # Error embed
                    title="Error!",
                    colour=colours["BLURPLE"]
                )
                error_embed.add_field(
                    name="Invalid cog provided",
                    value=f"Use `{prefixes[str(ctx.guild.id)][0]}cogs to view the available cogs.`",
                    inline=False
                )

                await ctx.send(embed=error_embed)

        except AttributeError:
            await ctx.send("`Make sure the cog is loaded first!`")


# Confirmation of login.
@client.event  # Command - Function Decorator
async def on_message(message):
    await client.process_commands(
        message)  # Preventing the on_message default overriding and forbidding extra commands from running.

    # The default on_message contains a call to this coroutine, but when you override it with your own on_message,
    # you need to call it yourself.


# Console/terminal info
@client.event
async def on_ready():
    global cog_count, cog_status

    # Go to the /cogs directory and load each one beforehand.
    for file in os.listdir("./cogs")[
                0:len(os.listdir("./cogs")) - 1]:  # Load all except the last file (__pycach)

        if file.startswith("song"):
            pass

        else:
            try:
                if not cog_status[file[:-3]]:
                    client.load_extension(f"cogs.{file[:-3]}")
                    cog_count += 1  # Add 1 (total) to the cog count to indicate how many cogs have been loaded.
                elif cog_status[file[:-3]]:
                    continue
                else:
                    continue
            except:  # __pycach
                continue

    # Loop through each value and set it to True (loaded).
    for cog in cog_status:
        cog_status[cog] = True

    # Setting up the mutes and mute_ids text files.
    open("mutes.txt", 'a').close()
    open("mutedids.txt", 'a').close()

    # Playing [name]
    # await client.change_presence(activity=discord.CustomActivity(name="Testing..."))
    # - Discord's Payload will not allow custom activities for bots yet.
    await client.change_presence(activity=discord.Game("Testing..."))
    print("-" * 30)
    print("Bot Name: " + client.user.name)
    print("Bot ID: " + str(client.user.id))
    print(f"Cogs loaded: {cog_count}")
    print("-" * 30)
    print("Initial Cog Status:")
    print()

    for cog in cog_status:
        if not cog_status[cog]:
            cog_stat = "Unloaded"
        elif cog_status[cog]:
            cog_stat = "Loaded"
        else:
            continue

        print(cog, "-", cog_stat)

    print("-" * 30)


# Manipulate JSON file with prefixes
@client.event
async def on_guild_join(guild):
    with open("prefixes.json", "r") as f:
        r_prefixes = json.load(f)

    # Create the default prefix for the server on join.
    r_prefixes[str(guild.id)] = ["+"]

    with open("prefixes.json", "w") as f:
        json.dump(r_prefixes, f, indent=4)


@client.event
async def on_guild_remove(guild):
    with open("prefixes.json", "r") as f:
        r_prefixes = json.load(f)

    # Remove the prefix of the server if kicked/banned.
    r_prefixes.pop(str(guild.id))

    with open("prefixes.json", "w") as f:
        json.dump(r_prefixes, f, indent=4)


client.run("Njk1MzY2MDM3NDY5OTIxNDU0.XuaQOw.iYqocdVCwEMOyVbrG3CTzuu-Iuc")
