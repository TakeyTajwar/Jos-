### Import Packages ###
import os
import discord
from discord.ext import commands
import requests
from replit import db
from keep_alive import keep_alive



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


# on reaction add
@client.event
async def on_raw_reaction_add(reaction):
	print(reaction)
	reaction_emoji = reaction.emoji
	reaction_msg_id = reaction.message_id
	reaction_msg_chn_id = reaction.channel_id

	print(reaction_emoji)

	if(str(reaction.emoji) == "<:bookmarkmsg:912040565720350731>"):
		bookmark_msg_chn = client.get_channel(912039171718250586)
		await bookmark_msg_chn.send(f"https://discord.com/channels/911794251703144508/{reaction_msg_chn_id}/{reaction_msg_id}") # server_id/channel_id/message_id



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