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

	chn_id = message.channel.id

	print(msg)

	await check_for_stats(msg)
	
	# delete messages sent in channels only for bots
	bots_only_channels = [
		911828737270616164, # stats
		912039171718250586, # messages
	]
	if(chn_id in bots_only_channels):
		await message.delete()
		return
	
	# functions for different channels
	if(chn_id == 911794506570035260): # films
		if(msg.startswith(r"https://www.imdb.com/title/")):
			await send_embed(await imdb_film_embed(msg), 911794506570035260)
			await message.delete()
			return
	
	elif(chn_id == 911794548001349663):
		if(msg.startswith(r"https://www.imdb.com/title/")):
			await send_embed(await imdb_series_embed(msg), 911794548001349663)
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
async def imdb_film_embed(link):
	# bs4
	soup = BeautifulSoup(requests.get(link).content, "html.parser")
	
	soup_credits = soup.find("div", {'class': r"PrincipalCredits__PrincipalCreditsPanelWideScreen-hdn81t-0 iGxbgr"}).findAll("div", {'class': r"ipc-metadata-list-item__content-container"})
	
	soup_poster = soup.find("div", {'class': "ipc-poster ipc-poster--baseAlt ipc-poster--dynamic-width Poster__CelPoster-sc-6zpm25-0 kPdBKI celwidget ipc-sub-grid-item ipc-sub-grid-item--span-2"}).find("img")
	if(soup_poster == None):
		soup.find("div", {'class': "Hero__MediaContainer__NoVideo-kvkd64-7 ytFvJ"}).find("img")
	
	soup_genres = soup.find("div", {'class': r"ipc-chip-list GenresAndPlot__GenresChipList-cum89p-4 gtBDBL"})
	if(soup_genres == None):
		soup_genres = soup.find("div", {'class': r"ipc-chip-list GenresAndPlot__OffsetChipList-cum89p-5 dMcpOf"})

	# embed
	film_title = soup.find("h1", {'data-testid': "hero-title-block__title"}).get_text()
	film_description = soup.find("span", {'data-testid': "plot-l"}).get_text()
	film_icon = soup_poster['src']
	film_year = soup.find("a", {'class': r"ipc-link ipc-link--baseAlt ipc-link--inherit-color TitleBlockMetaData__StyledTextLink-sc-12ein40-1 rgaOW"}).get_text()
	film_duration = soup.find("div", {'class': r"TitleBlock__TitleMetaDataContainer-sc-1nlhx7j-2 hWHMKr"}).findChildren("li", recursive=True)[-1].get_text()
	try:
		film_genres = [item.get_text() for item in soup_genres.findAll('a')]
	except:
		film_genres = [item.get_text() for item in soup_genres.findAll('a')]
	film_director = str([item.get_text() for item in soup_credits[0].findAll('a')]).replace('[', '').replace(']', '').replace('\'', '')
	film_writers = str([item.get_text() for item in soup_credits[1].findAll('a')]).replace('[', '').replace(']', '').replace('\'', '')
	film_stars = str([item.get_text() for item in soup_credits[2].findAll('a')]).replace('[', '').replace(']', '').replace('\'', '')
	film_keywords = soup.find("div", {'data-testid': "storyline-plot-keywords"})
	film_tl = soup.find("section", {'data-testid': "Storyline"}).find("span", {'class': "ipc-metadata-list-item__list-content-item"}).get_text()

	embed=discord.Embed(title=film_title, url=link, description=film_description, color=0xdeb522)
	embed.set_author(name="IMDB", url=link, icon_url=r"https://static-s.aa-cdn.net/img/ios/342792525/42b815c1b75b4bcb107806c6eb3f0fb3?v=1")
	embed.set_thumbnail(url=film_icon)
	embed.add_field(name="Year", value=film_year, inline=False)
	embed.add_field(name="Duration", value=film_duration, inline=False)
	embed.add_field(name="Genres", value=film_genres, inline=False)
	embed.add_field(name="Director", value=film_director, inline=False)
	embed.add_field(name="Writers", value=film_writers, inline=False)
	embed.add_field(name="Stars", value=film_stars, inline=False)
	if(film_keywords):
		film_keywords = film_keywords.findAll("a", {'class': "ipc-chip ipc-chip--on-base"})
		film_keywords = [item.get_text() for item in film_keywords]
		embed.add_field(name="Keywords", value=film_keywords)
	if(film_tl):
		embed.add_field(name="Tagline", value=film_tl, inline=False)
	return(embed)

# IMDB series embed
async def imdb_series_embed(link):
	# bs4
	soup = BeautifulSoup(requests.get(link).content, "html.parser")
	
	soup_credits = soup.find("div", {'class': r"PrincipalCredits__PrincipalCreditsPanelWideScreen-hdn81t-0 iGxbgr"}).findAll("div", {'class': r"ipc-metadata-list-item__content-container"})
	
	soup_poster = soup.find("div", {'class': "ipc-poster ipc-poster--baseAlt ipc-poster--dynamic-width Poster__CelPoster-sc-6zpm25-0 kPdBKI celwidget ipc-sub-grid-item ipc-sub-grid-item--span-2"}).find("img")
	if(soup_poster == None):
		soup.find("div", {'class': "Hero__MediaContainer__NoVideo-kvkd64-7 ytFvJ"}).find("img")
	
	soup_genres = soup.find("div", {'class': r"ipc-chip-list GenresAndPlot__GenresChipList-cum89p-4 gtBDBL"})
	if(soup_genres == None):
		soup_genres = soup.find("div", {'class': r"ipc-chip-list GenresAndPlot__OffsetChipList-cum89p-5 dMcpOf"})
	
	soup_orignal_title = soup.find("div", {'data-testid': "hero-title-block__original-title"})

	# embed
	series_title = soup.find("h1", {'data-testid': "hero-title-block__title"}).get_text()
	series_description = soup.find("span", {'data-testid': "plot-l"}).get_text()
	series_icon = soup_poster['src']
	series_year = soup.find("a", {'class': r"ipc-link ipc-link--baseAlt ipc-link--inherit-color TitleBlockMetaData__StyledTextLink-sc-12ein40-1 rgaOW"}).get_text()
	series_seasons = soup.find("select", {'id': "browse-episodes-season"})
	series_duration = soup.find("div", {'class': r"TitleBlock__TitleMetaDataContainer-sc-1nlhx7j-2 hWHMKr"}).findChildren("li", recursive=True)[-1].get_text()
	series_language = soup.find("li", {'data-testid': "title-details-languages"}).find("a").get_text()
	series_genres = [item.get_text() for item in soup_genres.findAll('a')]
	if(len(soup_credits)>1):
		series_creators = str([item.get_text() for item in soup_credits[0].findAll('a')]).replace('[', '').replace(']', '').replace('\'', '')
		series_stars = str([item.get_text() for item in soup_credits[1].findAll('a')]).replace('[', '').replace(']', '').replace('\'', '')
	else:
		series_creators = None
		series_stars = str([item.get_text() for item in soup_credits[0].findAll('a')]).replace('[', '').replace(']', '').replace('\'', '')
	series_keywords = soup.find("div", {'data-testid': "storyline-plot-keywords"})
	series_tl = soup.find("section", {'data-testid': "Storyline"}).find("span", {'class': "ipc-metadata-list-item__list-content-item"})

	embed=discord.Embed(title=series_title, url=link, description=series_description, color=0xdeb522)
	embed.set_author(name="IMDB", url=link, icon_url=r"https://static-s.aa-cdn.net/img/ios/342792525/42b815c1b75b4bcb107806c6eb3f0fb3?v=1")
	embed.set_thumbnail(url=series_icon)
	embed.add_field(name="Year", value=series_year, inline=False)
	if(series_seasons):
		embed.add_field(name="Seasons", value=series_seasons['aria-label'], inline=False)
	embed.add_field(name="Duration", value=series_duration, inline=False)
	embed.add_field(name="Language", value=series_language, inline=False)
	embed.add_field(name="Genres", value=series_genres, inline=False)
	if(series_creators):
		embed.add_field(name="Creators", value=series_creators, inline=False)
	embed.add_field(name="Stars", value=series_stars, inline=False)
	if(series_keywords):
		series_keywords = series_keywords.findAll("a", {'class': "ipc-chip ipc-chip--on-base"})
		series_keywords = [item.get_text() for item in series_keywords]
		embed.add_field(name="Keywords", value=series_keywords)
	if(soup_orignal_title):
		embed.set_footer(text=soup_orignal_title.get_text())
	if(series_tl):
		embed.add_field(name="Tagline", value=series_tl.to_text(), inline=False)
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