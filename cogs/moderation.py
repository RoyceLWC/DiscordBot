import discord
from discord.ext import commands
from discord.ext.commands import Bot

client = discord.Client()
# noinspection PyRedeclaration
client = Bot(command_prefix="?")

id_check = False
muted = False
muteduser = ""


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
        muterole = discord.utils.get(user.guild.roles, name="Muted")
        await user.add_roles(muterole)
        await ctx.send(f"`{user} has been muted.`")

    # Muting a user
    @commands.command(brief="Mutes an individual", description="Mutes a user via chat.", usage="[user] <reason>")
    @is_me()
    async def mute(self, ctx, user: discord.Member, *, reason="None"):

        if user.id == 695366037469921454:
            await ctx.send("You can't mute me!")
        else:
            muteduser_id = str(user.id)

            try:
                with open("mutes.txt", "a", encoding="utf-8") as newentry:
                    newentry.write(
                        f"User: {user}\nID: {muteduser_id}\nReason: {reason}\n")  # [3:len(muteduser_id)-1] for <@!>
                    # if present.
                    newentry.write("-" * 30 + "\n")
            except:
                with open("mutes.txt", "w", encoding="utf-8") as newentry:
                    newentry.write(f"User: {user}\nID: {muteduser_id}\nReason: {reason}\n")
                    newentry.write("-" * 30 + "\n")

            try:
                with open("mutedids.txt", "a", encoding="utf-8") as newentry:
                    newentry.write(muteduser_id + "\n")
            except:
                with open("mutedids.txt", "w", encoding="utf-8") as newentry:
                    newentry.write(muteduser_id + "\n")

            global muted
            muted = True

            global muteduser
            muteduser = user.id

            await ctx.send(f"`{user} has been muted.`")

    # Un-muting a user
    @commands.command(brief="Unmutes an individual", description="Unmutes a user via chat.", usage="[user] <reason>")
    @is_me()
    async def unmute(self, ctx, user: discord.Member, *, reason="None"):

        global muted
        muted = False

        global muteduser
        muteduser = user.id

        await ctx.send(f"`{user} has been unmuted.`")

    @commands.Cog.listener()
    async def on_message(self, message):

        global muted
        global muteduser
        global mute_ids

        with open("mutedids.txt", "r") as readmutes:
            mute_ids = []

            nmutes = readmutes.readlines()

            for id in nmutes:
                id = int(id[0:len(id) - 1])  # Get rid of the new line in the text file and convert it to an integer.
                mute_ids.append(id)  # Add it to the mute_ids list to be checked later.

        tk_possibilities = ["tk", "tK", "TK", "Tk", "TeaKay", "teakay"]

        for tk in tk_possibilities:
            if message.content.startswith(tk):
                await message.channel.send("<@297897016007196674> Lara poo poo")

        if "krunker.io" in message.content:  # Checks to see if the given " " is in the message (rather than
            # startswith).
            await message.delete()
            await message.channel.send("No.")

        if message.content.startswith("`__pycach`"):
            await message.delete()

        if message.author.id == 338406004356022283 and id_check == True:  # Makes sure the author is (Royce) and that
            # the response is validated.
            await message.channel.send("Royce's ID: 338406004356022283")

        if message.author.id in mute_ids and muted == True:
            await message.delete()

        if message.author.id in mute_ids:
            sentid = message.author.id
            await sentid.edit(mute=True)


def setup(client):
    client.add_cog(Moderation(client))
