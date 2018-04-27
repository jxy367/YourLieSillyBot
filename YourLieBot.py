import discord
from discord.ext import commands
import asyncio
from operator import itemgetter
from pysubs2 import *
import unidecode
import os


TOKEN = ''
client = commands.Bot(command_prefix='$')

scoring_dictionary = {}
total_words = 0
total_points = 0
total_player_points = 0
player_points = {}
needs_update = False
game_in_progress = False


def get_dictionary_from_file(file_name: str):
    my_dict = {}
    with open(file_name, 'r') as my_file:
        for my_line in my_file:
            my_line = my_line.strip()
            my_line = my_line.split(":")
            key = my_line[0]
            value = int(my_line[1])
            my_dict[key] = value
    return my_dict


def set_dictionary_to_file(my_dict: dict, file_name: str):
    with open(file_name, 'w') as my_file:
        for key in my_dict.keys():
            my_file.write(key + ":" + str(my_dict[key] + "\n"))


def get_progress():
    line1 = "Your server has found " + str(total_words - len(scoring_dictionary)) + " / " + str(total_words) + " words!\n"
    line2 = "Your server has found " + str(total_player_points) + " / " + str(total_points) + " points\n"
    return line1+line2


def get_scores():
    global needs_update
    needs_update = True
    update()
    scores_string = ""
    for key, value in sorted(player_points.items(), key=itemgetter(1), reverse=True):
        scores_string = scores_string + key + " : " + str(value) + "\n"
    return scores_string


def calculate_scoring():
    global total_points
    global total_words
    global scoring_dictionary
    subtitle_file = open("YourLieSubtitlesV2.txt", 'r')
    values_file = open("YourLieSubtitlesValues.txt", 'w')
    score_file = open("YourLieSubtitlesScores.txt", 'w')
    player_file = open("PlayerScores.txt", 'w')

    for subtitle_line in subtitle_file:
        subtitle_line = subtitle_line.strip()
        subtitle_line = subtitle_line.split(":")
        key = subtitle_line[0]
        value = 25 - int(subtitle_line[1])
        if value < 1:
            value = 1
        new_line = key + ":" + str(value) + "\n"
        values_file.write(new_line)
        score_file.write(new_line)
        scoring_dictionary[key] = value
    subtitle_file.close()
    total_points = sum(scoring_dictionary.values())
    total_words = len(scoring_dictionary)
    score_file.close()
    values_file.close()
    player_file.close()


def update():
    global needs_update
    if needs_update:
        set_dictionary_to_file(scoring_dictionary, "YourLieSubtitlesScores.txt")
        set_dictionary_to_file(player_points, "PlayerScores.txt")
        needs_update = False


def reset():
    global current_points
    global total_player_points
    global player_points
    global game_in_progress
    current_points = 0
    total_player_points = 0
    original_dict = get_dictionary_from_file("YourLieSubtitlesValues.txt")
    set_dictionary_to_file(original_dict, "YourLieSubtitlesScores.txt")
    player_points = {}
    set_dictionary_to_file(player_points, "PlayerScores.txt")
    game_in_progress = False


def increment_player_score(user_id: str, points: int):
    if user_id in player_points.keys():
        player_points[user_id] += points
    else:
        player_points[user_id] = points


def attempt_word(user_id: str, word: str):
    global total_player_points
    global needs_update
    if word in scoring_dictionary.keys():
        points_scored = scoring_dictionary[word]
        increment_player_score(user_id, points_scored)
        total_player_points += points_scored
        del scoring_dictionary[word]
        needs_update = True
        return points_scored
    return 0


def attempt_message(user_id: str, message: str):
    message = message.lower()
    for character in message:
        if not character.isalpha() and character is not "'":
            message = message.replace(character, " ")
    words = message.split(" ")
    for word in words:
        if word is not "":
            value = attempt_word(user_id, word)
            if value > 0:
                return value, word
    return 0, ""


# Bot Commands

@client.command()
async def start(ctx):
    global game_in_progress
    if game_in_progress:
        await ctx.send("Game already in progress")
    else:
        calculate_scoring()
        game_in_progress = True
        await ctx.send("Game has begun")


@client.command()
async def progress(ctx):
    if game_in_progress:
        await ctx.send(get_progress())
    else:
        await ctx.send("No game in progress")


@client.command()
async def scores(ctx):
    if game_in_progress:
        await ctx.send(get_scores())
    else:
        await ctx.send("No game in progress")


@client.command()
async def reset(ctx, reset_phrase):
    if game_in_progress:
        if reset_phrase is "AILYLIA":
            reset()
            await ctx.send("You have reset the game. Type '$start' to begin again")
        else:
            await ctx.send("Contact Jonathan to reset game")
    else:
        await ctx.send("No game in progress")


@client.command()
async def end(ctx, end_phrase):
    global game_in_progress
    if game_in_progress:
        if end_phrase is "Thank you for watching!":
            await ctx.send("The game has ended.\n Final scores:\n" + get_scores())
            reset()
            await ctx.send("Type '$start' to begin again")
        else:
            await ctx.send("Contact Jonathan to end game")
    else:
        await ctx.send("No game in progress")

client.remove_command('help')


@client.command()
async def help(ctx):
    embed = discord.Embed(title="Completion Bot", description="List of commands:", color=0xeee657)

    embed.add_field(name="$start", value="Attempts to start game", inline=False)
    embed.add_field(name="$progress", value="Gives completion percentage", inline=False)
    embed.add_field(name="$scores", value="Lists the current scores from highest to lowest", inline=False)
    embed.add_field(name="$reset reset_phrase", value="Resets game", inline=False)
    embed.add_field(name="$end end_phrase", value="Ends game and posts scores", inline=False)
    embed.add_field(name="$help", value="Gives this message", inline=False)

    await ctx.send(embed=embed)


async def background_update():
    await client.wait_until_ready()
    while not client.is_closed():
        update()
        await asyncio.sleep(60)


@client.event
async def on_message(message):
    global game_in_progress
    if game_in_progress:
        points, word = attempt_message(str(message.author.id), message.content)
        if points > 0:
            await message.channel.send(message.author.name + " scored " + str(points)
                                       + " points for the word '" + word + "' !")
            if len(scoring_dictionary) == 0:
                await message.channel.send("The game has ended.\n Final scores:\n" + get_scores())
                reset()
                await message.channel.send("Type '$start' to begin again")
    await client.process_commands(message)


@client.event
async def on_ready():
    global player_points
    global total_player_points
    global total_words
    global total_points
    global scoring_dictionary
    global game_in_progress
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    possible_player_scores = get_dictionary_from_file("PlayerScores.txt")
    if len(possible_player_scores) > 0:
        player_points = possible_player_scores
        total_player_points = sum(player_points.values())
        scoring_dictionary = get_dictionary_from_file("YourLieSubtitlesScores.txt")
        total_points = total_player_points + sum(scoring_dictionary.values())
        subtitles = get_dictionary_from_file("YourLieSubtitlesV2.txt")
        total_words = len(subtitles)
        game_in_progress = True

