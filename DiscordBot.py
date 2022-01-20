from dis import disco
from operator import ne
from tracemalloc import start
from urllib import response

import discord
import os
import requests
import json
import random
from discord.ext import commands
from dotenv import load_dotenv



load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
client = discord.Client()

words_relatedTo_Movies = ["Movie", "Movies", "movie", "movies"]
starter_recommendedMovies = ["Edge Of Tomorrow", "The Arq", "The Tomorrows War"]


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event 
async def on_message(message):
    msg = message.content
    if message.author == client.user:
        return
    
    if msg.startswith('hi'):
        await message.channel.send('Hello {}! Have fun!'.format(message.author))
        
    if msg.startswith("inspire me"):
        newQuote = get_quote()
        await message.channel.send(newQuote)

    if msg.startswith("$addMovie"):
        newMovie = msg.split("$addMovie ",1)[1]
        update_recommendedMovie(newMovie) 
        await message.channel.send("New recommended movie added!")
    elif msg.startswith("$delMovie"):
        index = int(msg.split("$delMovie ",1)[1])
        if len(starter_recommendedMovies) > index:
            delete_recommendedMovie(index)
        await message.channel.send(starter_recommendedMovies)
    elif msg.startswith("$listMovies"):
        await message.channel.send(starter_recommendedMovies)
    elif any(word in msg for word in words_relatedTo_Movies):
        await message.channel.send("Hey! Litte recommendation! You should consider to watch " + random.choice(starter_recommendedMovies))     




def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = "```" + json_data [0]['q'] + "```" +  "\n -" + json_data[0]['a']
    return(quote)

def update_recommendedMovie(new_movie):
    if new_movie not in starter_recommendedMovies:
        starter_recommendedMovies.append(new_movie)

def delete_recommendedMovie(index):
    if index < len(starter_recommendedMovies):
        del starter_recommendedMovies[index]



client.run(TOKEN)





