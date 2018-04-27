import discord
from discord.ext import commands

TOKEN = 'NDM5MjQ5MzkwODE4MDMzNjc0.DcQaag.yYxS2Efa_eMqu1vmQCUNrLy8AmI'
client = commands.Bot(command_prefix='$')

# normal functions #


def get_next_word(current_string):
    split_string = current_string.split(" ")
    new_string = ""
    while new_string is "":
        if len(split_string) > 0:
            new_string = split_string[0]
            del split_string[0]

            new_string = new_string.replace("?", "")
            new_string = new_string.replace("!", "")
            new_string = new_string.replace(".", "")
            new_string = new_string.replace('"', "")
            end_index = current_string.find(new_string) + len(new_string)
            if "'" in new_string:
                split_word = new_string.split("'")
                if not is_english_word(split_word[0]):  # Contraction
                    new_string = ""
            else:
                if not is_english_word(new_string):  # Actual English word
                    new_string = ""
        else:
            print("Woo! New line!")
            return "", ""  # Ran out of possible words

    print("new word: " + new_string)
    print("new partial line: " + current_string[end_index:])
    return new_string, current_string[end_index:]


def is_english_word(word):
    return word.lower() in english_words


def current_percentage():
    return str("%.2f" % (100 * current_line_num / total_lines)) + "%"

# Bot Commands


@client.command()
async def progress(ctx):
    await ctx.send(current_percentage() + " Complete!")


@client.command()
async def line(ctx):
    if current_line_num > 30:
        start_css = "```css\n"
        end_css = "\n```"
        finished_text = current_line.rstrip(current_partial_line).rstrip(current_word)
        current_text = " [" + current_word + "] "
        unfinished_text = current_partial_line
        msg = start_css + finished_text + current_text + unfinished_text + end_css
        await ctx.send(msg)
    else:
        await ctx.send("Complete more to unlock this!")


@client.command()
async def reset(ctx, reset_phrase):
    global current_line_num
    global current_word
    global current_partial_line
    global current_line
    global your_lie_subtitles
    if reset_phrase == "AILYLIA":
        current_line_num = 0
        with open("YourLieBotCurrentLocation.txt", 'w') as position_file:
            position_file.write("0")
            position_file.close()
        current_word = ""
        current_partial_line = ""
        current_line = ""
        your_lie_subtitles.close()
        your_lie_subtitles = open("YourLieSubtitles.txt",'r')
        current_line = your_lie_subtitles.readline().strip()
        current_word, current_partial_line = get_next_word(current_line)
        await ctx.send("You have reset completion progress")

client.remove_command('help')


@client.command()
async def help(ctx):
    embed = discord.Embed(title="Completion Bot", description="List of commands:", color=0xeee657)

    embed.add_field(name="$progress", value="Gives completion percentage", inline=False)
    embed.add_field(name="$line", value="Gives current line and highlights current word in orange", inline=False)
    embed.add_field(name="$reset reset_phrase", value="Resets completion progress", inline=False)
    embed.add_field(name="$help", value="Gives this message", inline=False)

    await ctx.send(embed=embed)


# Bot events


@client.event
async def on_message(message):
    global current_line_num
    global current_word
    global current_partial_line
    global current_line

    if message.author.bot:
        return

    if current_word is "":
        return

    if current_word.lower() in message.content.lower():
        await message.channel.send('```YAY! You used the word "' + current_word.lower() + '"!```')
        current_word = ""
        while current_word is "":
            current_word, current_partial_line = get_next_word(current_partial_line)
            if current_word is "":  # Move to next line
                current_line_num += 1
                if current_line_num == total_lines:
                    await message.channel.send('```CONGRATULATIONS! YOU COMPLETED YOUR LIE IN APRIL!```')
                    return
                else:
                    with open("YourLieBotCurrentLocation.txt", 'w') as line_num_file:
                        line_num_file.write(str(current_line_num))
                        line_num_file.close()
                    current_line = your_lie_subtitles.readline()
                    current_partial_line = current_line

    await client.process_commands(message)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


# Setup
total_lines = 6216

with open("EnglishWords.txt") as word_file:
    english_words = set(word.strip().lower() for word in word_file)

with open("YourLieBotCurrentLocation.txt", 'r') as current_file:
    current_line_num = int(current_file.read())
    current_file.close()

your_lie_subtitles = open("YourLieSubtitles.txt", 'r')
current_line = ""
num = 0
while num < current_line_num:
    your_lie_subtitles.readline()
    num += 1

current_word = ""
current_partial_line = ""
while current_word is "":
    current_line = your_lie_subtitles.readline().strip()
    current_word, current_partial_line = get_next_word(current_line)
    if current_word is "":
        current_line_num += 1

# Check we have values
print(current_word)
print(current_partial_line)
print(current_line)

client.run(TOKEN)
