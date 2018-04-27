import discord
from discord.ext import commands

TOKEN = ''
bot = commands.Bot(command_prefix='$')

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
            if "'" in new_string:
                split_word = new_string.split("'")
                if not is_english_word(split_word[0]):  # Contraction
                    new_string = ""
            else:
                if not is_english_word(new_string):  # Actual English word
                    new_string = ""
        else:
            return "", ""  # Ran out of possible words

    return new_string, "".join(split_string)


def is_english_word(word):
    return word.lower() in english_words


def current_percentage():
    return str(100 * current_line_num / total_lines) + "%"

# Bot Commands


@bot.command
async def progress(ctx):
    await ctx.send(current_percentage() + " Complete!")


@bot.command
async def line(ctx):
    start_css = "```css\n"
    end_css = "\n```"
    finished_text = current_line.rstrip(current_partial_line).rstrip(current_word)
    current_text = " [" + current_word + "] "
    unfinished_text = current_partial_line
    msg = start_css + finished_text + current_text + unfinished_text + end_css
    ctx.send(msg)

bot.remove_command('help')


@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Completion Bot", description="List of commands:", color=0xeee657)

    embed.add_field(name="$progress", value="Gives completion percentage", inline=False)
    embed.add_field(name="$line", value="Gives current line and highlights current word in orange", inline=False)
    embed.add_field(name="$help", value="Gives this message", inline=False)

    await ctx.send(embed=embed)


# Bot events


@bot.event
async def on_message(message):
    global current_line_num
    global current_word
    global current_partial_line
    global current_line

    if message.author.bot:
        return

    if current_word.lower() in message.content.lower():
        current_word = ""
        while current_word is "":
            current_word, current_partial_line = get_next_word(current_partial_line)
            if current_word is "":
                current_line_num += 1
                current_line = your_lie_subtitles.readline()
                current_partial_line = current_line


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


# Setup
total_lines = 6216

with open("EnglishWords.txt") as word_file:
    english_words = set(word.strip().lower() for word in word_file)

with open("YourLieBotCurrentLocation", 'r') as current_file:
    current_line_num = int(current_file.read())
current_file.close()

with open("YourLieSubtitles.txt", 'r') as your_lie_subtitles:
    current_line = ""
    num = 0
    while num < current_line_num:
        your_lie_subtitles.readline()
        num += 1

current_word = ""
current_partial_line = ""
while current_word is "":
    current_line_num += 1
    current_line = your_lie_subtitles.readline().strip()
    current_word, current_partial_line = get_next_word(current_line)

# Check we have values
print(current_word)
print(current_partial_line)
print(current_line)

bot.run(TOKEN)
