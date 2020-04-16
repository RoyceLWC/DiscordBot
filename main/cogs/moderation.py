import discord
from discord.ext import commands
from discord.ext.commands import Bot

client = discord.Client()
# noinspection PyRedeclaration
client = Bot(command_prefix="?")

id_check = False


def is_me():  # Creates a function decorator "@is_me()" that acts as a check().
    def predicate(ctx):
        return ctx.message.author.id == 338406004356022283

    return commands.check(predicate)


class Moderation(commands.Cog, name="moderation"):

    def __init__(self, client):
        self.client = client

    @client.command(description="Base command to show that the 'filter' is on.")
    async def filter(self, ctx):
        """
        ON
        """

        await ctx.send("Filter: ON")

    @client.command(brief="Royce's ID Check", description="Royce's temporary ID check switch command.",
                    usage="[on/off]")
    @is_me()
    async def id(self, ctx, *, switch):  # Switch is the message after the command (either input on/off).

        global id_check

        if switch == "on":
            await ctx.send("Royce's ID: ON")
            id_check = True  # If command is followed by "on", make id_check True (so that the ID_check executes).
        else:
            await ctx.send("Royce's ID: OFF")
            id_check = False

        return id_check

    # Muting a user (voice chat) through a role with restrictions.
    @client.command(brief="Server mutes a user (voice chat)", description="Mutes a user via voice chat.",
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
                        for section in m_ids[index:index+4]:  # Write the whole section [index:index+4] - 4 lines.
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

        if message.author.id == 338406004356022283 and id_check == True:  # Makes sure the author is (Royce) and that
            # the response is validated.
            await message.channel.send("Royce's ID: 338406004356022283")

        if message.author.id in mute_ids:
            await message.delete()


def setup(client):
    client.add_cog(Moderation(client))
