import asyncio
import csv
import json

import discord
from discord.ext import commands
from discord.ext.commands import Bot, has_permissions

client = discord.Client()
# noinspection PyRedeclaration


def get_prefix(client, message):
    with open("prefixes.json", "r") as read:
        r_prefixes = json.load(read)

    return r_prefixes[str(message.guild.id)]


client = Bot(command_prefix=get_prefix)

with open("prefixes.json", "r") as f:
    prefixes = json.load(f)


def is_me():  # Creates a function decorator "@is_me()" that acts as a check().
    def predicate(ctx):
        return ctx.message.author.id == 338406004356022283

    return commands.check(predicate)


class Moderation(commands.Cog, name="moderation"):

    def __init__(self, client):
        self.client = client

    @commands.command(description="Base command to show that the 'filter' is on.")
    async def filter(self, ctx):
        """
        ON
        """

        await ctx.send("Filter: ON")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        pass

    @commands.command(brief="Creates and saves a list of your server's moderation team",
                      description="Creates and saves a list of your server's moderation team [overwrites pre-existing lists].",
                      aliases=["createmods", "cml"])
    @has_permissions(manage_messages=True)  # Validate permissions of the user
    async def createmodlist(self, ctx):

        global prefixes

        # Local variable referencing
        global admin_name, reacting, str_admins, mods_list, colour_hex

        def check(react, user):  # Check if reacted to
            return str(react.emoji) in reaction_emoji_list and user == ctx.message.author

        def channel_check(m):  # Check if in channel
            return m.channel == ctx.channel

        # Setup team name - Embed
        mod_embed = discord.Embed(
            title="Initialising...",
            colour=0x7289DA
        )
        mod_embed.add_field(
            name="Setup",
            value="Include Discord team name?",
            inline=False
        )

        custom_embed = await ctx.send(embed=mod_embed)

        await custom_embed.add_reaction(emoji='\U00002B06')  # Up-arrow reaction
        await custom_embed.add_reaction(emoji='\U00002B07')  # Down-arrow reaction

        reaction_emoji_list = ['\U00002B06', '\U00002B07']

        # Team name section of embed (edit)
        try:
            reacting, confirm_user = await ctx.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("`Took too long! Neglecting team name response...`")  # If user takes too long - timeout.

        if reacting.emoji == "\U00002B06":  # If the .emoji is the up-arrow...
            mods_bool = True  # Make mods_bool True in order to implement mods to the embed.
        elif reacting.emoji == '\U00002B07':
            mods_bool = False
        else:
            mods_bool = False

        if mods_bool:
            await ctx.send("`Enter your moderation team's name:`")

            try:
                team_name = await ctx.bot.wait_for('message', timeout=30.0, check=channel_check)
                team_name = team_name.content
            except asyncio.TimeoutError:
                await ctx.send("`Took too long! Neglecting team name response...`")  # If user takes too long - timeout.
                return
        else:
            team_name = None

        # Custom Colour

        mod_embed = discord.Embed(  # Initialise first mod_embed (setup).
            title="Initialising...",
            colour=0x7289DA
        )
        mod_embed.add_field(
            name="Setup",
            value="Custom embed colour?",
            inline=False
        )

        await custom_embed.edit(embed=mod_embed)

        try:
            reacting, confirm_user = await ctx.bot.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("`Took too long! Neglecting colour response...`")  # If user takes too long - timeout.
        else:
            print(reacting)

        if reacting.emoji == "\U00002B06":  # If the .emoji is the up-arrow...
            embed_colour = True  # Make admins_bool True in order to implement admins to the embed.
        else:
            embed_colour = False

        if embed_colour:
            await ctx.send("Enter the hex of the colour prefixed by `0x`:")
            try:
                colour_hex = await ctx.bot.wait_for('message', timeout=60.0)  # Receive colour hex.
                colour_hex = int(colour_hex.content, 16)
            except asyncio.TimeoutError:
                await ctx.send("`Took too long! Neglecting custom colour response...`")
        else:
            colour_hex = None

        # Setup admin section - Embed
        mod_embed = discord.Embed(
            title="Initialising...",
            colour=0x7289DA
        )
        mod_embed.add_field(
            name="Setup",
            value="Include admin team?",
            inline=False
        )
        await custom_embed.edit(embed=mod_embed)

        try:  # Check if custom hex is valid.
            if team_name is not None:
                final_mod_embed = discord.Embed(
                    title=team_name,
                    colour=discord.Colour(colour_hex)
                )
            else:
                final_mod_embed = discord.Embed(
                    title="Discord Moderation Team",
                    colour=discord.Colour(colour_hex)
                )
        except:  # Default colour
            if team_name is not None:
                final_mod_embed = discord.Embed(
                    title=team_name,
                    colour=0x7289DA
                )
            else:
                final_mod_embed = discord.Embed(
                    title="Discord Moderation Team",
                    colour=0x7289DA
                )

        # Admin section of embed
        try:
            reacting, confirm_user = await ctx.bot.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("`Took too long! Neglecting admin response...`")  # If user takes too long - timeout.
        else:
            pass

        if reacting.emoji == "\U00002B06":  # If the .emoji is the up-arrow...
            admins_bool = True  # Make admins_bool True in order to implement admins to the embed.
        else:
            admins_bool = False

        if admins_bool:  # If admins need to be included.
            await ctx.send("`Mention a list of the current server admins - delimited by commas.`")
            try:
                admins_list = await ctx.bot.wait_for('message', timeout=30.0,
                                                     check=channel_check)  # Receive list of admins.

                try:
                    admins_list = [x.strip() for x in admins_list.content.split(",")]  # Split the message via the commas and strip whitespaces - create a list.
                    print(admins_list)
                except:
                    await ctx.send("`Error! Please try again.`")
                    return

                await ctx.send(
                    "`Is there a specific name for the team? [Y/N]`")  # Prompt for a specific admin team name.

                admin_name = await ctx.bot.wait_for('message', timeout=30.0, check=channel_check)

                if "y" in admin_name.content.lower():
                    await ctx.send("`Enter the name of the admin team:`")
                    admin_name = await ctx.bot.wait_for('message', timeout=30.0, check=channel_check)
                    admin_name = admin_name.content
                else:
                    admin_name = "Admins"

                str_admins = ""

                for admin in admins_list:
                    str_admins += f"{admin}\n"

                final_mod_embed.add_field(  # Add the admin embed section.
                    name=admin_name,
                    value=str_admins,
                    inline=False
                )
            except asyncio.TimeoutError:
                await ctx.send("`Took too long! Neglecting admin response...`")  # If user takes too long - timeout.
        else:
            admin_name = None  # Mark that there is no admin section to be displayed.
            str_admins = None

        # Setup mod section - Embed
        mod_embed = discord.Embed(
            title="Initialising...",
            colour=0x7289DA
        )
        mod_embed.add_field(
            name="Setup",
            value="Include mod team?",
            inline=False
        )
        await custom_embed.edit(embed=mod_embed)  # Edit the initialising embed - Mod section (retain reactions from last).

        # Mod section of embed (edit)
        try:
            reacting, confirm_user = await ctx.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("`Took too long! Neglecting mod response...`")  # If user takes too long - timeout.

        if reacting.emoji == "\U00002B06":  # If the .emoji is the up-arrow...
            mods_bool = True  # Make mods_bool True in order to implement mods to the embed.
        elif reacting.emoji == '\U00002B07':
            mods_bool = False
        else:
            mods_bool = False

        # Mod section of embed
        if mods_bool:

            await ctx.send("`Mention a list of the current moderators - delimited by commas.`")

            try:
                mods_list = await ctx.bot.wait_for('message', timeout=30.0, check=channel_check)
            except asyncio.TimeoutError:
                await ctx.send("`Took too long! Neglecting mod list response...`")  # If user takes too long - timeout.

            try:
                mods_list = [x.strip() for x in mods_list.content.split(",")]
                print(mods_list)
            except asyncio.TimeoutError:
                error_embed = discord.Embed(  # Error embed
                    title="Error!",
                    colour=0xe74c3c
                )
                error_embed.add_field(
                    name=f"{prefixes[str(ctx.guild.id)][0]}createmodlist",
                    value=f"`Ensure the list of moderators given is separated by commas and the list is not empty.`",
                    inline=False
                )
                await ctx.send(embed=error_embed)
                return

            await ctx.send("`Is there a specific name for the moderation team? [Y/N]`")

            try:
                mod_name = await ctx.bot.wait_for('message', timeout=30.0, check=channel_check)
            except asyncio.TimeoutError:
                await ctx.send("`Took too long! Neglecting custom mod team name...`")  # If user takes too long - timeout.
                mod_name = None

            if "y" in mod_name.content.lower():
                await ctx.send("`Enter the name of the moderation team:`")
                mod_name = await ctx.bot.wait_for('message', timeout=30.0, check=channel_check)
                mod_name = mod_name.content
            else:
                mod_name = "Moderators"

            str_mods = ""

            for mod in mods_list:
                str_mods += f"{mod}\n"

            final_mod_embed.add_field(  # Add mod section (string of mods/mod name)
                name=mod_name,
                value=str_mods,
                inline=False
            )
        else:
            mod_name = None
            str_mods = None

        await ctx.send(embed=final_mod_embed)

        if admin_name is not None or mod_name is not None:  # Write the file if at least one section is filled in.
            try:  # See if there is already a pre-existing file.

                lines = []
                with open('mod-teams.csv', 'r') as read:
                    reader = csv.reader(read)

                    for row in reader:

                        try:
                            if row[0] != str(ctx.guild.id):  # Remove any pre-existing moderator list entries
                                lines.append(row)
                        except:
                            pass

                with open('mod-teams.csv', 'w') as mod_file:

                    writer = csv.writer(mod_file)
                    writer.writerows(lines)  # Add all the other moderator lists from other servers.

                    # Add on the current server's updated moderator list.
                    write = csv.writer(mod_file, delimiter=",")
                    write.writerow([ctx.guild.id, str(admin_name), str(str_admins), str(mod_name),
                                    str(str_mods), colour_hex, team_name])  # Write the guild ID and mod embed to the CSV file.

            except FileNotFoundError:  # If not, create one.
                with open("mod-teams.csv", "w") as mod_file:
                    write = csv.writer(mod_file, delimiter=",")
                    write.writerow([ctx.guild.id, str(admin_name), str(str_admins), str(mod_name), str(str_mods), colour_hex, team_name])  # .content for discord.Message class.
        else:
            error_embed = discord.Embed(  # Error embed
                title="Error!",
                colour=0xe74c3c
            )
            error_embed.add_field(
                name="Moderation list not saved...",
                value="`Empty`",
                inline=False
            )
            await ctx.send(embed=error_embed)

    @commands.command(brief="Edits a pre-existing moderation list embed with the current one", description="Edits and updates a pre-existing moderation list embed of a given message ID with the current updated moderation list.", usage="[message ID]")
    async def editmodlist(self, ctx, message_id=None):

        global prefixes, edit_embed

        if message_id is None:
            error_embed = discord.Embed(  # Error embed
                title="Error!",
                colour=0xe74c3c
            )
            error_embed.add_field(
                name="No message ID provided!",
                value=f"`{prefixes[str(ctx.guild.id)][0]}editmodlist [message ID]`",
                inline=False
            )

            await ctx.send(embed=error_embed)
            return

        try:  # Try to open the file.
            with open("mod-teams.csv",
                      "r+") as read_mods:  # Open and read the mod-teams.csv file, containing the mod list.
                reader = csv.reader(read_mods)

                sent = False

                for server in reader:
                    print(server)
                    try:
                        if server[0] == str(ctx.guild.id):  # If the server ID matches the current server.
                            sent = True

                            try:
                                if server[5] is not None:  # If there is a custom colour for embed...
                                    if server[6] is not None:
                                        edit_embed = discord.Embed(
                                            title=server[6],
                                            colour=discord.Colour(int(server[5]))
                                        )
                                    else:
                                        edit_embed = discord.Embed(
                                            title="Discord Moderation Team",
                                            colour=discord.Colour(int(server[5]))
                                        )
                                else:
                                    if server[6] is not None:
                                        edit_embed = discord.Embed(
                                            title=server[6],
                                            colour=0x7289DA
                                        )
                                    else:
                                        edit_embed = discord.Embed(
                                            title="Discord Moderation Team",
                                            colour=0x7289DA
                                        )
                            except:
                                edit_embed = discord.Embed(
                                    title="Discord Moderation Team",
                                    colour=0x7289DA
                                )

                            if server[1] == "None" or server[2] == "None":  # If there is no admin team (None - string)
                                pass
                            else:
                                edit_embed.add_field(  # Admin List
                                    name=server[1],
                                    value=server[2],
                                    inline=False
                                )

                            if server[3] == "None" or server[4] == "None":  # If there is no mod team (None - string)
                                pass
                            else:
                                edit_embed.add_field(  # Mod List
                                    name=server[3],
                                    value=server[4],
                                    inline=False
                                )

                    except IndexError:
                        continue

                if not sent:  # If no guild ID matches the current guild.
                    error_embed = discord.Embed(  # Error embed
                        title="Error!",
                        colour=0xe74c3c
                    )
                    error_embed.add_field(
                        name="There is no pre-existing moderation list!",
                        value=f"`{prefixes[str(ctx.guild.id)][0]}createmodlist`",
                        inline=False
                    )

                    await ctx.send(embed=error_embed)
                    return

        except FileNotFoundError:  # If the file is not found, return an error.
            error_embed = discord.Embed(  # Error embed
                title="Error!",
                colour=0xe74c3c
            )
            error_embed.add_field(
                name="There is no pre-existing moderation list!",
                value=f"`{prefixes[str(ctx.guild.id)][0]}createmodlist`",
                inline=False
            )

            await ctx.send(embed=error_embed)
            return

        try:
            msg_edit = await ctx.fetch_message(message_id)
            await msg_edit.edit(embed=edit_embed)
        except:
            error_embed = discord.Embed(  # Error embed
                title="Error!",
                colour=0xe74c3c
            )
            error_embed.add_field(
                name="Invalid message ID provided!",
                value=f"`{prefixes[str(ctx.guild.id)][0]}editmodlist [message ID]`",
                inline=False
            )

            await ctx.send(embed=error_embed)

        await ctx.message.delete()

    @commands.command(brief="Displays the current moderation team",
                      description="Lists the current moderation team (with their respective time zones).",
                      aliases=["mods", "team", "admins"])
    async def moderators(self, ctx):

        global prefixes

        try:  # Try to open the file.
            with open("mod-teams.csv",
                      "r+") as read_mods:  # Open and read the mod-teams.csv file, containing the mod list.
                reader = csv.reader(read_mods)

                sent = False

                for server in reader:
                    print(server)
                    try:
                        if server[0] == str(ctx.guild.id):  # If the server ID matches the current server.
                            sent = True

                            try:
                                if server[5] is not None:  # If there is a custom colour for embed...
                                    if server[6] is not None:
                                        server_mod_embed = discord.Embed(
                                            title=server[6],
                                            colour=discord.Colour(int(server[5]))
                                        )
                                    else:
                                        server_mod_embed = discord.Embed(
                                            title="Discord Moderation Team",
                                            colour=discord.Colour(int(server[5]))
                                        )
                                else:
                                    if server[6] is not None:
                                        server_mod_embed = discord.Embed(
                                            title=server[6],
                                            colour=0x7289DA
                                        )
                                    else:
                                        server_mod_embed = discord.Embed(
                                            title="Discord Moderation Team",
                                            colour=0x7289DA
                                        )
                            except:
                                server_mod_embed = discord.Embed(
                                    title="Discord Moderation Team",
                                    colour=0x7289DA
                                )

                            if server[1] == "None" or server[2] == "None":  # If there is no admin team (None - string)
                                pass
                            else:
                                server_mod_embed.add_field(  # Admin List
                                    name=server[1],
                                    value=server[2],
                                    inline=False
                                )

                            if server[3] == "None" or server[4] == "None":  # If there is no mod team (None - string)
                                pass
                            else:
                                server_mod_embed.add_field(  # Mod List
                                    name=server[3],
                                    value=server[4],
                                    inline=False
                                )

                            await ctx.send(embed=server_mod_embed)  # Send embed with mod field (and/or admin field).
                    except IndexError:
                        continue

                if not sent:  # If no guild ID matches the current guild.
                    error_embed = discord.Embed(  # Error embed
                        title="Error!",
                        colour=0xe74c3c
                    )
                    error_embed.add_field(
                        name="There is no pre-existing moderation list!",
                        value=f"`{prefixes[str(ctx.guild.id)][0]}createmodlist`",
                        inline=False
                    )

                    await ctx.send(embed=error_embed)

        except FileNotFoundError:  # If the file is not found, return an error.
            error_embed = discord.Embed(  # Error embed
                title="Error!",
                colour=0xe74c3c
            )
            error_embed.add_field(
                name="There is no pre-existing moderation list!",
                value=f"`{prefixes[str(ctx.guild.id)][0]}createmodlist`",
                inline=False
            )

            await ctx.send(embed=error_embed)

    # Muting a user (voice chat) through a role with restrictions.
    @commands.command(brief="Server mutes a user (voice chat)", description="Mutes a user via voice chat.",
                      usage="[user]")
    @is_me()
    async def vcmute(self, ctx, user: discord.Member):
        muted_role = discord.utils.get(user.guild.roles, name="Muted")
        await user.add_roles(muted_role)
        await ctx.send(f"`{user} has been muted.`")

    # Muting a user
    @commands.command(brief="Mutes an individual", description="Mutes a user via chat.", usage="[user] <reason>")
    @is_me()
    async def mute(self, ctx, user: discord.Member = None, *, reason="None"):

        already_muted = False

        if user:
            if user.id == 695366037469921454:
                await ctx.send("You can't mute me!")
            else:
                muteduser_id = str(user.id)

                with open("mutes.txt", "r") as check:  # First check to see if the user hasn't already been muted.

                    lines = check.readlines()

                    for line in lines:
                        if muteduser_id in line:
                            already_muted = True
                            await ctx.send(f"`{user} has already been muted.`")

                if not already_muted:
                    try:
                        with open("mutes.txt", "a", encoding="utf-8") as new_entry:

                            new_entry.write(
                                f"User: {user}\nID: {muteduser_id}\nReason: {reason}\n")  # [3:len(muteduser_id)-1] for <@!>
                            # if present.
                            new_entry.write("-" * 30 + "\n")
                    except FileNotFoundError:
                        with open("mutes.txt", "w", encoding="utf-8") as new_entry:
                            new_entry.write(f"User: {user}\nID: {muteduser_id}\nReason: {reason}\n")
                            new_entry.write("-" * 30 + "\n")

                    try:
                        with open("mutedids.txt", "a", encoding="utf-8") as new_entry:
                            new_entry.write(muteduser_id + "\n")
                    except FileNotFoundError:
                        with open("mutedids.txt", "w", encoding="utf-8") as new_entry:
                            new_entry.write(muteduser_id + "\n")

                    await ctx.send(f"`{user} has been muted.`")
                else:
                    print("User already muted.")
        else:
            await ctx.send("`Invalid user!`")

    # Un-muting a user
    @commands.command(brief="Unmutes an individual", description="Unmutes a user via chat.", usage="[user] <reason>")
    @is_me()
    async def unmute(self, ctx, user: discord.Member):

        with open("mutedids.txt", "r") as unmuting:
            ids = unmuting.readlines()
            muted_id = ""

            for line in ids:
                if str(user.id) == line[:-1]:
                    muted_id = str(user.id)

        with open("mutedids.txt", "w") as unmuting:  # Write the file separately.

            if muted_id == "":  # If the ID isn't in "mutedids.txt", do 'nothing'.
                await ctx.send(f"`{user} has not been muted.`")
                for line in ids:
                    unmuting.write(line)  # Write the whole file again as usual.
            else:
                for line in ids:
                    if str(line[:-1]) != muted_id:
                        unmuting.write(line)

                await ctx.send(f"`{user} has been unmuted.`")

        with open('mutes.txt', "r") as unmuting:  # Create separate reading for "mutes.txt".
            m_ids = unmuting.readlines()
            muted_user = ""

            for sec in m_ids:
                if str(user) in sec:
                    muted_user = str(user)

        with open("mutes.txt", "w") as unmuting:  # Write the file with previously read lines.

            if muted_user == "":
                for line in m_ids:
                    unmuting.write(line)
            else:
                for line in m_ids[::4]:  # Loop through every fourth line to check the starting line of the report.
                    if str(muted_user) in line:  # If the user tag is in the file, 'delete' it by skipping through.
                        continue
                    else:
                        index = m_ids.index(line)
                        for section in m_ids[index:index + 4]:  # Write the whole section [index:index+4] - 4 lines.
                            unmuting.write(section)

    @commands.Cog.listener()
    async def on_message(self, message):

        global mute_ids

        with open("mutedids.txt", "r") as read_mutes:
            mute_ids = []

            nmutes = read_mutes.readlines()

            for mute_id in nmutes:
                mute_id = int(mute_id[0:len(
                    mute_id) - 1])  # Get rid of the new line in the text file and convert it to an integer.
                mute_ids.append(mute_id)  # Add it to the mute_ids list to be checked later.

        if message.content.startswith("`__pycach`"):
            await message.delete()

        if message.author.id in mute_ids:
            await message.delete()


def setup(client):
    client.add_cog(Moderation(client))
