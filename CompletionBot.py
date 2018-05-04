import discord
from discord.ext import commands
import asyncio
import shutil
import os
from operator import itemgetter

#TOKEN = 'NDM5MzQ2NDQ2Njk3ODg5Nzky.DcR0yA.EjGPqA1pyaHVBxcnHCxLTDtwMkY'
client = commands.Bot(command_prefix='$')

scoring_dictionary = {}
total_words = 0
total_points = 0
total_player_points = 0
player_points = {}
needs_update = False
game_in_progress = False

bot_message_channel = 395765134171308032

# Client events

@client.event
async def on_ready():
    client.loop.create_task(background_update())

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


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
                await message.channel.send("The game has ended.\n Final scores:\n" + get_scores())
                reset_game()
                await message.channel.send("Type '$start' to begin again")
    await client.process_commands(message)


@client.event
async def on_guild_join(guild):
    make_guild_data(guild)

# Client commands


# Other functions
async def background_update():
    await client.wait_until_ready()
    while not client.is_closed():
        for guild_id in client.guilds:  # Just Id
            if guild_id in current_games.keys():  # Currently playing game
                game_update(guild_id)   # update game
        await asyncio.sleep(60)


# Bot updates game data files
async def game_update(guild_id):
    game = current_games[guild_id]
    if game.is_changed:
        update_data(game)   # update guild data

    else:
        if not game.is_messaged:  # No messages have been sent to the server
            game.increase_messageless_counter()  # Increase messageless counter and reset id_messaged field
            if game.messageless_counter == 10:    # If no messages to the server in the last 10 minutes
                remove(game)    # Remove game from current_games list.


# Make necessary directory and files
async def make_guild_data(guild_id):
    shutil.copytree(src="original_data_files", dst=str(guild_id))



async def update_data(guild_id):  # Backup guild data
    x=0


# GameInstance class

class GameInstance:
    def __init__(self, guild_id: int):
        if client.get_guild(guild_id) in client.guilds:
            self.all_data = get_game_data(guild_id)  # Return tuple

            self.is_messaged = False
            self.messageless_counter = 0

    def increase_messageless_counter(self):
        self.messageless_counter += 1

    def received_message(self):
        self.is_messaged = True
        self.messageless_counter = 0
