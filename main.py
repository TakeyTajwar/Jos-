### Import Packages ###
# os, discord and replit
import os
import discord
from discord.ext import commands
from replit import db
from keep_alive import keep_alive

# useful libraries
import re # regular expression

# web
import requests
from bs4 import BeautifulSoup



### Run the Bot ###
intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.reactions = True
client = commands.Bot(command_prefix='/', intents=intents)



### DB Variables ###
db['stats_msg_id'] = 911834720487235648



### Variables ###
emojis = {
	'bookmark': "<:bookmarkmsg:912040565720350731>"
}



### Client Functions ###
# on ready
@client.event
async def on_ready():
	print("José is ready!")
	await update_stats()



# on message
@client.event
async def on_message(message):
	if(message.author.bot): # if the sender is a bot
		return
	
	msg = message.content

	print(msg)

	await check_for_stats(msg)
	
	# delete messages sent in channels only for bots
	bots_only_channels = [
		911828737270616164, # stats
		912039171718250586, # messages
	]
	if(message.channel.id in bots_only_channels):
		await message.delete()
		return
	
	# functions for different channels
	if(message.channel.id == 911794506570035260): # films
		if(msg.startswith(r"https://www.imdb.com/title/")):
			await send_embed(imdb_film_embed(msg), 911794506570035260)
			await message.delete()
			return



# on reaction add
@client.event
async def on_raw_reaction_add(reaction):
	print(reaction)
	reaction_emoji = reaction.emoji
	reaction_msg_id = reaction.message_id
	reaction_msg_chn_id = reaction.channel_id
	reaction_msg_sender_id = reaction.user_id

	print(reaction_emoji)

	if(str(reaction.emoji) == "<:bookmarkmsg:912040565720350731>"):
		message = await client.get_channel(reaction_msg_chn_id).fetch_message(reaction_msg_id)
		sender = client.get_user(reaction_msg_sender_id)

		await message.remove_reaction(reaction_emoji, sender)

		bookmark_msg_chn = client.get_channel(912039171718250586)
		msg = message.content
		if(len(msg)>64):
			msg = msg[0:60] + '...'
		elif(len(msg)<1):
			msg = "<press here to jump to the message>"
		
		embed=discord.Embed(color=0x3b874a)
		embed.add_field(name=message.author, value=f"[{msg}](<https://discord.com/channels/911794251703144508/{reaction_msg_chn_id}/{reaction_msg_id}>)", inline=False)
		await bookmark_msg_chn.send(embed=embed)



### Embed Functions ###
# send embed to channel
async def send_embed(embed, chn_id):
	chn = client.get_channel(chn_id)
	await chn.send(embed=embed)

# IMDB film embed
def imdb_film_embed(link):
	# bs4
	soup = BeautifulSoup(requests.get(link).content, "html.parser")

	# embed
	film_title = soup.find("h1", {'data-testid': "hero-title-block__title"}).get_text()
	film_description = soup.find("span", {'data-testid': "plot-l"}).get_text()
	# film_icon = ""
	film_year = soup.find("a", {'class': r"ipc-link ipc-link--baseAlt ipc-link--inherit-color TitleBlockMetaData__StyledTextLink-sc-12ein40-1 rgaOW"}).get_text()
	# film_duration = soup.find("a", {'class': r"ipc-inline-list__item", 'role': "presentation"})
	film_genres = soup.find("div", {'class': r"ipc-chip-list GenresAndPlot__GenresChipList-cum89p-4 gtBDBL"}).get_text()
	film_director = soup.find("a", {'class': r"ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"}).get_text()
	film_writers = soup.find("div", {'class': r"ipc-metadata-list-item__content-container"}).get_text()
	film_stars = soup.find("ul", {'class': r"ipc-inline-list ipc-inline-list--show-dividers ipc-inline-list--inline ipc-metadata-list-item__list-content baseAlt"}).get_text()

	embed=discord.Embed(title=film_title, url=link, description=film_description, color=0xdeb522)
	embed.set_author(name="IMDB", url=link, icon_url=r"https://static-s.aa-cdn.net/img/ios/342792525/42b815c1b75b4bcb107806c6eb3f0fb3?v=1")
	# embed.set_thumbnail(url=film_icon)
	embed.add_field(name="Year", value=film_year, inline=False)
	# embed.add_field(name="Duration", value=film_duration, inline=False)
	embed.add_field(name="Genres", value=film_genres, inline=False)
	embed.add_field(name="Director", value=film_director, inline=False)
	embed.add_field(name="Writers", value=film_writers, inline=False)
	embed.add_field(name="Stars", value=film_stars, inline=False)
	return(embed)



### Stats Functions ###
async def check_for_stats(msg):
	msg = msg.lower().replace(' ', '')

	if('iloveyou' in msg):
		db["stats_ily"] = db['stats_ily'] + 1
		await update_stats()

async def update_stats():
	stats_msg = "```py\n" + f"'I love you' messages: {db['stats_ily']}" + "\n```"
	# await client.get_channel(911828737270616164).send(stats_msg)
	stats_message = await client.get_channel(911828737270616164).fetch_message(db['stats_msg_id'])
	await stats_message.edit(content=stats_msg)



### Run The Bot ###
keep_alive()
client.run(os.getenv('TOKEN'))