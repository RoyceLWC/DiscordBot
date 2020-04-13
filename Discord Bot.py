import os

import discord
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

try:  # See if there is already a pre-existing prefix file.
    with open("prefix.txt", "r") as botprefix:
        PREFIX = botprefix.readlines()[0]
except:  # If not, create one with a given prefix from the prompt.
    with open("prefix.txt", "w") as setprefix:
        PREFIX = input("Please enter a prefix: ")
        setprefix.write(PREFIX)

client = discord.Client()
client = Bot(command_prefix=PREFIX)


@client.command(
    brief=f"Changes the current prefix `{PREFIX}`")  # Brief is the command descriptor displayed, whereas description
# is the full description displayed after specified command.
async def prefix(ctx, *, prefix):
    global PREFIX

    with open("prefix.txt", "w") as newprefix:
        newprefix.write(prefix)

    PREFIX = prefix

    client.command_prefix = PREFIX  # Change the prefix (update).

    await ctx.send(f"Prefix has been changed to `{prefix}`.")


cog_count = 0

# Initialising a dictionary with each cog's status (loaded/unloaded)
cog_status = {
    "fun": False,
    "moderation": False,
    "utility": False
}

# Hello Alternatives
greetings = ["hello", "hey", "hi", "Hello", "Hey", "Hi", "hola", "Hola"]


def is_me():  # Creates a function decorator "@is_me()" that acts as a check().
    def predicate(ctx):
        return ctx.message.author.id == 338406004356022283

    return commands.check(predicate)


@client.command(brief="Shows the number of users on the server")
async def users(ctx):
    id = client.get_guild(626436080672964628)

    await ctx.send(f"""```nimrod\nTotal Users: {id.member_count}```""")


@client.command(brief="Shows available cogs")
async def cogs(ctx):
    cogs = []

    for filename in os.listdir("./cogs"):
        cogs.append(filename)

    await ctx.send(f"""
    ```
Cogs available:```
    """)

    for file in cogs[0:len(cogs) - 1]:  # Remove __pycach in the list index
        await ctx.send(f"`{file[:-3]}`")  # Index slicing to remove .py


@client.command(brief="Loads cogs")
@is_me()
async def load(ctx, extension):
    """
        for filename in os.listdir("./cogs"):
        print("test")
        if filename.endswith(".py"):
            client.load_extension(f"cogs.{filename[:-3]}")
    """
    global cog_count
    global cog_status

    if extension == "all":
        await ctx.send("All cogs have been loaded.")

        # Go to the /cogs directory and load each one.
        for filename in os.listdir("./cogs")[
                        0:len(os.listdir("./cogs")) - 1]:  # Load all except the last file (__pycach)

            if cog_status[filename[:-3]] == False:
                client.load_extension(f"cogs.{filename[:-3]}")
                cog_count += 1  # Add 1 (total) to the cog count to indicate how many cogs have been loaded.
            elif cog_status[filename[:-3]] == True:
                continue
            else:
                continue

        # Loop through each value and set it to True (loaded).
        for cog in cog_status:
            cog_status[cog] = True

        print("-" * 30)
        print("Bot Name: " + client.user.name)
        print("Bot ID: " + str(client.user.id))
        print(f"Prefix: {PREFIX}")
        print("-" * 30)
        print(f"Cogs loaded: {cog_count}")
        print("Cog Status:")
        print()

        for cog in cog_status:
            if cog_status[cog] == False:
                cog_stat = "Unloaded"
            elif cog_status[cog] == True:
                cog_stat = "Loaded"
            else:
                continue

            print(cog, "-", cog_stat)

        print("-" * 30)
    else:
        client.load_extension(f"cogs.{extension}")
        await ctx.send(f"`{extension}` cog has been loaded.")
        cog_count += 1

        cog_status[extension] = True  # Set the cog's value to True (loaded)

        print("-" * 30)
        print("Bot Name: " + client.user.name)
        print("Bot ID: " + str(client.user.id))
        print(f"Prefix: {PREFIX}")
        print("-" * 30)
        print(f"Cogs loaded: {cog_count}")
        print("Cog Status:")
        print()

        for cog in cog_status:
            if cog_status[cog] == False:
                cog_stat = "Unloaded"
            elif cog_status[cog] == True:
                cog_stat = "Loaded"
            else:
                break

            print(cog, "-", cog_stat)

        print("-" * 30)


@client.command(brief="Unloads cogs")
@is_me()
# @commands.has_role('RoleName')
async def unload(ctx, extension):
    global cog_count
    global cog_status

    if extension == "all":
        await ctx.send("All cogs have been unloaded.")

        # Go to the /cogs directory and unload each one.
        for filename in os.listdir("./cogs")[
                        0:len(os.listdir("./cogs")) - 1]:  # Unload all except the last file (__pycach)

            if cog_status[filename[
                          :-3]] == True:  # Search dictionary with the filename without .py as the key (rather than looping through dictionary).
                client.unload_extension(f"cogs.{filename[:-3]}")
                cog_count -= 1  # Add 1 (total) to the cog count to indicate how many cogs have been loaded.
            elif cog_status[filename[:-3]] == False:
                continue
            else:
                continue

        # Loop through each value and set it to False (unloaded).
        for cog in cog_status:
            cog_status[cog] = False

        print("-" * 30)
        print("Bot Name: " + client.user.name)
        print("Bot ID: " + str(client.user.id))
        print(f"Prefix: {PREFIX}")
        print("-" * 30)
        print(f"Cogs loaded: {cog_count}")
        print("Cog Status:")
        print()

        for cog in cog_status:
            if cog_status[cog] == False:
                cog_stat = "Unloaded"
            elif cog_status[cog] == True:
                cog_stat = "Loaded"
            else:
                continue

            print(cog, "-", cog_stat)

        print("-" * 30)
    else:
        client.unload_extension(f"cogs.{extension}")
        await ctx.send(f"`{extension}` cog has been unloaded.")
        cog_count -= 1

        cog_status[extension] = False  # Set the cog's value to False (unloaded).

        print("-" * 30)
        print("Bot Name: " + client.user.name)
        print("Bot ID: " + str(client.user.id))
        print(f"Prefix: {PREFIX}")
        print("-" * 30)
        print(f"Cogs loaded: {cog_count}")
        print("Cog Status:")
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


# Help (Embed)
@client.command(brief="Shows the more refined help prompt.")
async def nhelp(ctx, cog="all"):
    # Preparing embed
    if cog == "all":
        cog_help = "General"
    else:
        cog_help = cog.capitalize()  # Make first letter capital

    help_embed = discord.Embed(
        title=f"Help | {cog_help}",  # Specified cog title (or general).
        colour=colours["BLURPLE"]
    )
    help_embed.set_thumbnail(url=client.user.avatar_url)
    help_embed.set_footer(
        text=f"Requested by {ctx.message.author.name}",
        icon_url=client.user.avatar_url
    )

    # Get a list of all cogs
    cogs = []

    for filename in os.listdir("./cogs")[0:len(cogs) - 1]:
        cogs.append(filename)

    if cog == "all":

        all_cog_commands = []

        # General commands

        try:
            for c in cogs:
                cog_commands = client.get_cog(c[:-3]).get_commands()

                for cogname in cog_commands:  # Loop through each object command and append the name of the command.
                    all_cog_commands.append(cogname.name)
        except:
            pass

        general_commands = ""
        for command in client.commands:

            if str(command) == "help":  # Compensate for the "help" command (which has None as brief).
                general_commands += f"`{command.name}` - *Shows the basic help prompt*\n"
            elif str(
                    command) not in all_cog_commands:  # Get rid of commands within the cogs (str() needed for
                # all_cog_commands list).
                general_commands += f"`{command.name}` - *{command.brief}*\n"

        help_embed.add_field(
            name="General",
            value=general_commands,
            inline=False
        )

        for cog in cogs:

            try:
                # Get a list of all commands under each cog
                cog_commands = client.get_cog(cog[:-3]).get_commands()
                commands_list = ""

                for command in cog_commands:
                    commands_list += f"`{command.name}` - *{command.brief}*\n"

                # Add the details above to the embed
                help_embed.add_field(
                    name=cog[:-3].capitalize(),
                    value=commands_list,
                    inline=False
                )  # .add_field(
                # name = "\u200b", value = "\u200b", inline = False -- Add a whitespace character (blank field).
                # )

            except:
                pass

        # Extra info
        help_embed.add_field(
            name="---",
            value=f"For more information on each cog, use `{PREFIX}nhelp [cog]`.",
            inline=False
        )

        await ctx.send(embed=help_embed)
        pass

    else:  # Cog specified...

        try:
            lower_cogs = [cog.lower() for cog in cogs]
            lower_cogs_py = [x[:-3] for x in lower_cogs]  # Get rid of .py (separately).

            if cog.lower() in lower_cogs_py:  # Check if cog exists.

                commands_list = client.get_cog(lower_cogs_py[lower_cogs.index(
                    cog.lower() + ".py")]).get_commands()  # Cog must be loaded and index referenced must have full file name.
                help_text = ""

                for command in commands_list:
                    help_text += f"`{command.name}`\n*{command.description}*\n"

                    # Formatting of command
                    help_text += f"**Format: ** `{PREFIX}{command.name} {command.usage if command.usage is not None else ''}`\n"  # Name/usage under command via the decorator (paraneters) - Return blank if no usage given.

                    # If there are aliases, add them
                    if len(command.aliases) > 0:
                        help_text += f"**Aliases: ** `{'`, `'.join(command.aliases)}`\n\n"
                    else:
                        help_text += "\n"

                help_embed.description = help_text

                await ctx.send(embed=help_embed)

            else:
                await ctx.send("Invalid cog specified.\nUse `?cogs` to view the avaiable cogs.")
        except:
            await ctx.send("Make sure the cog is loaded first!")


# Confirmation of login.
@client.event  # Command - Function Decorator
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("Hello"):
        await message.channel.send("Hello, I'm Royce's Bot.")

    await client.process_commands(
        message)  # Preventing the on_message default overriding and forbidding extra commands from running.

    # The default on_message contains a call to this coroutine, but when you override it with your own on_message,
    # you need to call it yourself.


@client.event
async def on_member_join(member):  # Event will run when a member joins the server.

    for channel in member.guild.channels:
        if str(channel) == "general":
            await channel.send(
                f"Welcome {member.mention} to the server! Have fun.")  # Member does not have any attributes;
            # channel.send used instead.


@client.event
async def on_ready():
    global PREFIX

    status = True

    if status:
        stat = "Online"
    else:
        stat = "Offline"

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
    print(f"Status: {stat}")
    print(f"Prefix: {PREFIX}")
    print(f"Cogs loaded: {cog_count}")
    print("-" * 30)
    print("Cog Status:")
    print()

    for cog in cog_status:
        if cog_status[cog] == False:
            cog_stat = "Unloaded"
        elif cog_status[cog] == True:
            cog_stat = "Loaded"
        else:
            continue

        print(cog, "-", cog_stat)

    print("-" * 30)


client.run("Njk1MzY2MDM3NDY5OTIxNDU0.XoZKow.4i74qydWR1u0p5JgF16jlzrbDYo")

# Add a cog count and boolean values to keep console posted.
