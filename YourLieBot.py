import discord
from discord.ext import commands
import asyncio
from operator import itemgetter

TOKEN = 'NDM5MzQ2NDQ2Njk3ODg5Nzky.DcR0yA.EjGPqA1pyaHVBxcnHCxLTDtwMkY'
client = commands.Bot(command_prefix='$')

scoring_dictionary = {}
subtitle_frequency = {}
num_ordered_words_found = 0
total_words = 0
total_points = 0
total_player_points = 0
next_word = ""
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
            my_file.write(key + ":" + str(my_dict[key]) + "\n")


def get_progress():
    line1 = "Your server has found " + str(total_words - len(scoring_dictionary)) + " / " + str(total_words) + " words!\n"
    line2 = "Your server has found " + str(total_player_points) + " / " + str(total_points) + " points\n"
    line3 = "Your server has found the " + str(num_ordered_words_found) + " most frequent words\n"
    return line1+line2+line3


def get_scores():
    global needs_update
    needs_update = True
    update()
    scores_string = ""
    for key, value in sorted(player_points.items(), key=itemgetter(1), reverse=True):
        scores_string = scores_string + client.get_user(int(key)).display_name + " : " + str(value) + "\n"
    return scores_string


def get_hint():
    print(next_word)
    print(subtitle_frequency[next_word])
    line1 = "The next most frequent word was used " + str(subtitle_frequency[next_word]) + " times.\n"
    line2 = "This word begins with '" + next_word[0] + " and has a length of " + str(len(next_word)) + "." + "'\n"
    return line1+line2


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


def reset_game():
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
        if word == next_word:
            find_next_word()
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


def find_next_word():
    global next_word
    global subtitle_frequency
    global scoring_dictionary
    global num_ordered_words_found
    count = 0
    for key, value in sorted(subtitle_frequency.items(), key=lambda x: (-x[1], x[0])):
        if key in scoring_dictionary.keys():
            next_word = key
            num_ordered_words_found = count
            print(next_word)
            break
        else:
            count += 1
    next_word = ""
    num_ordered_words_found = count


async def reset_display_name():
    for changed_guild in client.guilds:
        if changed_guild.me.display_name != "Nicer Completion Bot":
            print(changed_guild.name)
            print(changed_guild.me.display_name)
            print("---")
            await changed_guild.me.edit(nick=None)

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
async def hint(ctx):
    if game_in_progress:
        await ctx.send(get_hint())
    else:
        await ctx.send("No game in progress")


@client.command()
async def reset(ctx, reset_phrase):
    if game_in_progress:
        if reset_phrase == "AILYLIA":
            reset_game()
            await ctx.send("You have reset the game. Type '$start' to begin again")
        else:
            await ctx.send("Contact Jonathan to reset game")
    else:
        await ctx.send("No game in progress")


@client.command()
async def end(ctx, end_phrase):
    global game_in_progress
    if game_in_progress:
        if end_phrase == "ThankYouForWatching!":
            await ctx.send("The game has ended.\n Final scores:\n" + get_scores())
            reset_game()
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
    embed.add_field(name="$progress", value="Gives completion in various forms", inline=False)
    embed.add_field(name="$scores", value="Lists the current scores from highest to lowest", inline=False)
    embed.add_field(name="$hint", value="Gives the first letter and frequency of the next most frequent word")
    embed.add_field(name="$reset reset_phrase", value="Resets game", inline=False)
    embed.add_field(name="$end end_phrase", value="Ends game and posts scores", inline=False)
    embed.add_field(name="$help", value="Gives this message", inline=False)

    await ctx.send(embed=embed)


async def background_update():
    await client.wait_until_ready()
    while not client.is_closed():
        update()
        await reset_display_name()
        await asyncio.sleep(60)


@client.event
async def on_message(message):
    await client.wait_until_ready()
    if message.author.bot:
        return
    global game_in_progress
    if game_in_progress:
        points, word = attempt_message(str(message.author.id), message.content)
        if points > 0:
            if points == 1:
                msg = message.author.name + " scored " + str(points)+ " point for the word '" + word + "' !"
            else:
                msg = message.author.name + " scored " + str(points) + " points for the word '" + word + "' !"
            channel = client.get_channel(395765134171308032)  # Bot Test Channel
            await channel.send(msg)
            if len(scoring_dictionary) == 0:
                await message.channel.send("Congratulations! You said most of the words in Your Lie in April!")
                await message.channel.send("Since the game began, Jonathan completed the series 4 times!")
                await message.channel.send("The game has ended.\n Final scores:\n" + get_scores())
                reset_game()
                await message.channel.send("Type '$start' to begin again\n")
                await message.channel.send("And then everyone important died.")
                await message.channel.send("Have fun Noah!")

    await client.process_commands(message)


@client.event
async def on_ready():
    global player_points
    global subtitle_frequency
    global total_player_points
    global total_words
    global total_points
    global scoring_dictionary
    global game_in_progress

    subtitle_frequency = get_dictionary_from_file("SortedYourLieSubtitles.txt")
    possible_player_scores = get_dictionary_from_file("PlayerScores.txt")
    if len(possible_player_scores) > 0:
        player_points = possible_player_scores
        total_player_points = sum(player_points.values())
        scoring_dictionary = get_dictionary_from_file("YourLieSubtitlesScores.txt")
        total_points = total_player_points + sum(scoring_dictionary.values())
        subtitles = get_dictionary_from_file("YourLieSubtitlesV2.txt")
        total_words = len(subtitles)
        find_next_word()
        game_in_progress = True

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    client.loop.create_task(background_update())

client.run(TOKEN)
