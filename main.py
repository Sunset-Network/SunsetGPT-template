import discord
import requests
import os
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv('TOKEN') # DO NOT PUT YOUR TOKEN IN HERE
GROQ_API_KEY = os.getenv('GROQ_API_KEY') # DO NOT PUT THE API KEY IN HERE

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

chat_channels = {}
current_model = "llama3-8b-8192"  # if this model didn't work change it to mistral-8x7b-32768 and rerun your bot and do everything and it should work!
current_mode = "normal" 
admin_ids = [ 132213, 1212] # Replace with role id or user id

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
activity=discord.Activity(type=discord.ActivityType.playing, name='Chatting with people') # Put any activity you like idfc

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.guild and message.channel.id == chat_channels.get(message.guild.id):
        await handle_chat(message)

    await bot.process_commands(message)

@bot.hybrid_command(name='channel') # set a specifi channel for the bot to response just do /channel and send the command it should set it to the channel you want it to change
async def channel(ctx):
    chat_channels[ctx.guild.id] = ctx.channel.id
    await ctx.send(f'Chat channel set to: {ctx.channel.mention}')

@bot.hybrid_command(name='mode') # Modes might not work i might fix it and reupdate everything so make sure to check this github repo if updated or you can js join sunset server i will let ppl know if i updated the code or no
async def mode(ctx, mode: str):
    if ctx.author.id not in admin_ids:
        await ctx.send("You do not have permission to use this command.")
        return

    global current_mode
    valid_modes = ["normal", "developer", "funny"]

    if mode in valid_modes:
        current_mode = mode
        await ctx.send(f'Mode changed to: {current_mode}')
    else:
        await ctx.send("Invalid mode. Please choose from: normal, developer, or funny.")

async def handle_chat(message): # This line is important so don't remove it or else the bot won't work
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        messages = [
            {"role": "user", "content": message.content}
        ]

        data = {
            "model": current_model,
            "messages": messages
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            data = response.json()
            response_text = data['choices'][0]['message']['content']
            if len(response_text) > 2000:
                response_text = response_text[:1997] + '...'  
            await message.channel.send(response_text)
        else:
            await message.channel.send(f"Error fetching data: {response.status_code}")

    except Exception as e:
        await message.channel.send(f"An error occurred: {str(e)}")

@bot.hybrid_command(name='models') # Ai bot models, some models are not work idfk why so yea don't blame me for it if all didn't work js use mistral-8x7b-32768
async def models(ctx):
    if ctx.author.id not in allowed_users:
        await ctx.send("You do not have permission to use this command.")
        return

    models = [
        "llama-3.1-70b-versatile",
        "whisper-large-v3",
        "distil-whisper-large-v3-en",
        "llama3-groq-8b-8192-tool-use-preview",
        "llava-v1.5-7b-4096-preview",
        "gemma2-9b-it",
        "llama-3.2-90b-text-preview",
        "mistral-8x7b-32768",
        "llama-guard-3-8b", # This model will response with safe. 💀
        "whisper-large-v3-turbo"
    ]

    models_list = "\n".join(models)
    await ctx.send(f"Available Models:\n{models_list}")

@bot.command()
async def sync(ctx):
    synced = await bot.tree.sync()
    await ctx.send(f"Synced {len(synced)} command(s)")


# You can add more commands any command you like

bot.run(TOKEN) # DO NOT PUT YOUR TOKEN HERE
