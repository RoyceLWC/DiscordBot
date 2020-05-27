import random

import discord
from discord.ext import commands
from discord.ext.commands import Bot

client = discord.Client()

try:  # See if there is already a pre-existing prefix file.
    with open("prefix.txt", "r") as bot_prefix:
        PREFIX = bot_prefix.readlines()[0]
except FileNotFoundError:  # If not, create one with a given prefix from the prompt.
    with open("prefix.txt", "w") as set_prefix:
        PREFIX = input("Please enter a prefix: ")
        set_prefix.write(PREFIX)

client = Bot(command_prefix=PREFIX)


class Fun(commands.Cog, name="fun"):

    def __init__(self, client):
        """

        :type client: object
        """
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        pass

    # Commands
    @commands.command(brief="Gives an answer to your question",
                      description="The Magic 8-Ball used for fortune-telling or seeking advice. Ask it a question!",
                      aliases=["8ball", "ball"], usage="[question]")
    async def _8ball(self, ctx, *,
                     question="?"):  # "Context" added as a parameter to be used in the function; must be the first 
        # parameter. 

        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes",
            "Signs point to yes.",
            "Definitely",
            "Almost certainly.",
            "Reply hazy, try again.",
            "Too hard to tell",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "It is not looking likely",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
            "It's a strong no",
            "No",
        ]

        await ctx.send(f"Question: {question}\nAnswer: {random.choice(responses)}")

    """
    @client.command(brief="Test for Marcus")
    async def level(self, ctx, user: discord.Member):

        levelid = str(user.id)

        print(levelid)

        with open("mutedids.txt", "r") as readlevel:
            lines = readlevel.readlines()
            levelid2 = str(lines[0])
            levels = lines[1]

            print(levelid,levelid2)

        print(levelid,levelid2)

        if str(levelid) == str(levelid2):
            print('test')
            await ctx.send(f"<@{levelid2}> is {levels}")
    """


def setup(client):
    client.add_cog(Fun(client))
