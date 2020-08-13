import random
import json

import discord
import json
import asyncio
import numpy as np
from discord.ext.commands import has_permissions
from urllib.request import urlopen
from discord.ext import commands
from discord.ext.commands import Bot

client = discord.Client()

def get_prefix(message):
    with open("prefixes.json", "r") as read:
        r_prefixes = json.load(read)

    return r_prefixes[str(message.guild.id)]


client = Bot(command_prefix=get_prefix)

with open("prefixes.json", "r") as f:
    prefixes = json.load(f)


class Fun(commands.Cog, name="fun"):

    def __init__(self, client):
        """

        :type client: object
        """
        self.client = client

    def bet_error_message(self, ctx):  # Error message for bet command.

        global prefixes

        error_embed = discord.Embed(  # Error embed
            title="Error!",
            colour=0x7289DA
        )
        error_embed.add_field(
            name="Invalid bet provided!",
            value=f"`{prefixes[str(ctx.guild.id)]}bet <[minutes]m> <[seconds]s>`",
            inline=False
        )

        return error_embed

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        pass

    # Commands
    @commands.command(brief="Places a bet", description="Places a bet via Discord.", usage="<[minutes]m> <[seconds]s> <name>")
    async def bet(self, ctx, *, bet=None):

        if bet is None:
            await ctx.send(embed=self.bet_error_message(ctx))
            return

        bet_time = 0  # Reset added bet_time to list.

        # find() returns -1 if not found - checks if 'm' and/or 's' is provided.

        min_index = bet.find("m")  # Find where the m cuts off (minutes)
        sec_index = bet.find("s")  # Find where the s cuts off (seconds)

        if min_index > sec_index and sec_index != -1:  # If no minutes are provided but m appears later on (e.g. Name) - second check needed if only minutes are provided.
            min_index = -1

        try:
            if bet[sec_index-1].isalpha() or bet[sec_index-1] == " " or bet[sec_index-1] == "'":  # If an identified "s" has a character or space straight before, the seconds are invalid (e.g. appears in name - [PREFIX]bet 4m Sam)
                sec_index = -1
            else:
                pass
        except:
            pass

        space = 1
        while True:  # Detect name after mis-typed spaces.
            if space < 50:
                try:
                    if bet[sec_index+space].isalpha():
                        name = bet[sec_index+space:len(bet)]
                        if name[0:2] == "m ":  # Get rid of the "m " if sec_index is either -1 or later on in name.
                            name = name[2:len(name)]
                        if name == "m":  # If user bets for him/herself (e.g. [PREFIX]bet 1m) with no follow up name.
                            name = None
                        break
                    else:
                        space += 1
                        continue
                except IndexError:
                    name = None
                    break
            else:
                name = None
                break

        try:
            if min_index != -1 and sec_index != -1:  # If both minutes and seconds are provided.
                bet_time = 0

                mins = int(
                    bet[0:min_index])  # Identify the section of the string that comes before 'm' for the minutes.

                space = 1

                while True:
                    try:
                        secs = int(bet[
                                   min_index + space:sec_index])  # Identify the section of the string that comes before 's' for the seconds (and after 'm').
                        break
                    except ValueError:
                        space += 1
                        continue

                bet_time += ((mins * 60) + secs)

            elif min_index == -1 and sec_index != -1:  # If only seconds are provided/betted.

                secs = int(bet[0:sec_index])

                bet_time += secs

            elif min_index != -1 and sec_index == -1:  # If only minutes are provided/betted.

                mins = int(bet[0:min_index])

                bet_time += (mins * 60)

            elif "no" in bet.lower() or bet == "0":  # No gulag bet
                bet_time = 0
                name = None

            elif min_index == -1 and sec_index == -1:
                await ctx.send(embed=self.bet_error_message(ctx))
                return
            else:
                await ctx.send(embed=self.bet_error_message(ctx))
                return

        except:
           await ctx.send(embed=self.bet_error_message(ctx))
           return

        bet_embed = discord.Embed(  # Error embed
            title="Bet submitted!",
            colour=0x7289DA
        )
        if bet_time == 0:
            bet_embed.add_field(
                name=ctx.author,
                value=f"Time betted: `No gulag`",
                inline=False
            )
        else:
            bet_embed.add_field(
                name=ctx.author,
                value=f"Time betted: `{bet_time // 60}m {bet_time % 60}s`",
                inline=False
            )

        await ctx.send(embed=bet_embed)

        if name is not None:
            with open("bets.txt", "a") as bets:
                bets.write(f"{name} - {bet_time // 60}m {bet_time % 60}s\n")
        else:
            with open("bets.txt", "a") as bets:
                bets.write(f"{ctx.author.id} - {bet_time // 60}m {bet_time % 60}s\n")

    @commands.command(brief="Clears the current bets", description="Removes all Discord bets.", aliases=["clearbet", "cb", "clearlist", "cl"])
    @has_permissions(manage_messages=True)  # Validate permissions of the user
    async def clearbets(self, ctx):
        open('bets.txt', 'w').close()

        clear_embed = discord.Embed(  # Error embed
            title="Bets cleared!",
            colour=0x7289DA
        )

        await ctx.send(embed=clear_embed)


    @commands.command(brief="Finds the GulagBets winner!", description="Finds the #GulagBets winner!", aliases=["gw","gulagwinner","win", "wintime"], usage="[winning time]")
    @has_permissions(manage_messages=True)  # Validate permissions of the user
    async def winner(self, ctx, *, time=None):

        global prefixes

        if time == None:
            await ctx.send(f"`Invalid input! {prefixes[str(ctx.guild.id)]}win_time [winning time] needed.`") # If winning time isn't provided (default None)
            return
        else:
            pass

        try:
            win_time = int(time) # Ensure win_time provided is an actual time.
        except ValueError:
            min_index = time.find("m")  # Find where the m cuts off (minutes)
            sec_index = time.find("s")  # Find where the s cuts off (seconds)

            if min_index == -1 and sec_index == -1:
                await ctx.send("Invalid input!")
                return
            else:
                win_time = 0
                if min_index != -1 and sec_index != -1:  # If both minutes and seconds are provided.

                    mins = int(
                        time[
                        0:min_index])  # Identify the section of the string that comes before 'm' for the minutes.

                    space = 1

                    while True:
                        try:
                            secs = int(time[
                                       min_index + space:sec_index])  # Identify the section of the string that comes before 's' for the seconds (and after 'm').
                            break
                        except ValueError:
                            space += 1
                            continue

                    win_time += ((mins * 60) + secs)

                elif min_index == -1 and sec_index != -1:  # If only seconds are provided/betted.

                    secs = int(time[0:sec_index])

                    win_time += secs

                elif min_index != -1 and sec_index == -1:  # If only minutes are provided/betted.

                    mins = int(time[0:min_index])

                    win_time += (mins * 60)

                elif "no" in win_time.lower() or win_time == "0":  # No gulag bet
                    win_time = 0

                elif min_index == -1 and sec_index == -1:
                    error_embed = discord.Embed(  # Error embed
                        title="Error!",
                        colour=0x7289DA
                    )
                    error_embed.add_field(
                        name="Invalid bet provided!",
                        value=f"`{prefixes[str(ctx.guild.id)]}winner [win_time]`",
                        inline=False
                    )
                    await ctx.send(embed=error_embed)
                    return

                else:
                    error_embed = discord.Embed(  # Error embed
                        title="Error!",
                        colour=0x7289DA
                    )
                    error_embed.add_field(
                        name="Invalid bet provided!",
                        value=f"`{prefixes[str(ctx.guild.id)]}winner [win_time]`",
                        inline=False
                    )
                    await ctx.send(embed=error_embed)
                    return


        with urlopen('https://twitch.center/customapi/quote/list?token=453c4f16&no_id=1') as f: # Open Twitch entries list webpage.
            b_bets = f.readlines()

        bets = []

        for x in b_bets:
            x = x.decode('utf-8') # Convert bytes-literal to string.
            bets.append(x)

        with open("bets.txt", "r") as discord_bets:
            d_bets = discord_bets.readlines()

        for y in d_bets:
            bets.append(y)

        full_times = []
        user_entries = []
        duplicate = set(user_entries)

        for bet in bets:
            bet_time = 0 # Reset added bet_time to list.

            # find() returns -1 if not found - checks if 'm' and/or 's' is provided.

            index = bet.find("-") # Find the section of the line after the username (-)
            min_index = bet.find("m", index) # Find where the m cuts off (minutes)
            sec_index = bet.find("s", index) # Find where the s cuts off (seconds)

            if min_index != -1 and sec_index != -1: # If both minutes and seconds are provided.
                bet_time = 0

                mins = int(bet[index+2:min_index]) # Identify the section of the string that comes before 'm' for the minutes.

                space = 1

                while True:
                    try:
                        secs = int(bet[min_index+space:sec_index]) # Identify the section of the string that comes before 's' for the seconds (and after 'm').
                        break
                    except ValueError:
                        space += 1
                        continue

                bet_time += ((mins*60) + secs)

            elif min_index == -1 and sec_index != -1: # If only seconds are provided/betted.

                secs = int(bet[index+2:sec_index])

                bet_time += secs

            elif min_index != -1 and sec_index == -1: # If only minutes are provided/betted.

                mins = int(bet[index+2:min_index])

                bet_time += (mins*60)

            else:
                bet_time = 0

            if bet[0:index-1] not in duplicate: # Get rid of duplicate bets and take their first bet only.
                duplicate.add(bet[0:index-1])
                full_times.extend([[bet[0:index-1], bet_time]]) # Add the person who bet and time betted to the list.


        """
        columnIndex = 1
        np_full_times = np.array(np_full_times)
        np_full_times = np_full_times[np_full_times[:, columnIndex].argsort()] # Sort the list by index 1.
        """

        full_times.sort(key=lambda x: x[1])

        print(full_times)

        times = []

        for x in range(len(full_times)):
            times.append(full_times[x][1]) # Add the times to a separate list.

        print(times)

        """
        times = numpy.asarray(times)
        idx = (numpy.abs(times - win_time)).argmin() # Find the closest value in array using numpy.
        winner = array[idx]
        """

        if win_time == 0: # Ensure a 'no gulag' win is solely 'no gulag' bets (and not closer bets if there aren't any 'no gulag' bets).
            winning_time = 0
        else:
            times = [value for value in times if value != 0] # If there is a gulag time, make sure 'no gulag' bets are removed (list comprehension).
            winning_time = times[min(range(len(times)), key = lambda i: abs(times[i]-win_time))] # Find closest value to win_time.

        winning_users = []
        duplicate = set(winning_users)

        for x in range(len(full_times)):
            if full_times[x][1] == winning_time and full_times[x][0] not in duplicate: # Find bet that matches the winning (closest) time and check if it isn't a duplicate.
                duplicate.add(full_times[x][0]) # Add item to duplicate set.
                winning_users.append(full_times[x][0]) # Add winning user to the list.

        if len(winning_users) == 0: # If no 'no gulag' bets are placed (empty list).
            await ctx.send("`No winners this round! No 'no gulag' bets were placed.`")
        elif win_time == True: # Get rid of return value.
            pass
        else:
            for winning_user in winning_users: # Loop through to display multiple users if there are overlapping bets.
                if winning_user.isdigit():
                    await ctx.send(f"<@{winning_user}> has won #GulagBets - Bet: `{winning_time // 60}m {winning_time % 60}s`! ({winning_time} seconds)")
                    #await ctx.send(f"<@602263598240235531> has won #GulagBets - Bet: `{winning_time // 60}m {winning_time % 60}s`! ({winning_time} seconds)")
                else:
                    await ctx.send(f"`{winning_user}` has won #GulagBets - Bet: `{winning_time // 60}m {winning_time % 60}s`! ({winning_time} seconds)")
                    #await ctx.send(
                        #f"<@602263598240235531> has won #GulagBets - Bet: `{winning_time // 60}m {winning_time % 60}s`! ({winning_time} seconds)")

        # Bets (Results) Embed

        results_embed = discord.Embed(
            title="Bets",
            colour=0x7289DA
        )
        results_embed.set_thumbnail(url="https://i.ya-webdesign.com/images/dice-png-icon-3.png")
        results_embed.set_footer(
            text=f"Requested by {ctx.message.author.name}"
        )

        bets_list = ""
        for x in range(len(full_times)):
            if full_times[x][0].isdigit():
                bets_list += f"*<@{full_times[x][0]}>* - `{full_times[x][1]//60}m {full_times[x][1]%60}s`\n"
            else:
                bets_list += f"*{full_times[x][0]}* - `{full_times[x][1] // 60}m {full_times[x][1] % 60}s`\n"

        results_embed.add_field(
            name="Results | Times",
            value=bets_list,
            inline=False
        )

        await ctx.send(embed=results_embed)

        return results_embed

    @commands.command(brief="Displays the bets list", description="Displays non-duplicate bets from the bets list.",
                      aliases=["bl", "betlist"])
    async def betslist(self, ctx):

        # Call the winner function containing the bets list (from extracted data [website/.txt]
        """
        from multiprocessing import Pool
        pool = Pool(processes=1)  # Start a worker processes.
        bets_list = pool.apply_async(winner, [0], callback)  # Evaluate "f(10)" asynchronously calling callback when finished.
        """
        await self.winner(ctx, time=True)

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

        await ctx.send(f"**Question:** {question}\n**Answer:** {random.choice(responses)}")

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
