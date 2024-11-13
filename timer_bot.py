import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables from .env file
load_dotenv()

# Access your bot token
bot_token = os.getenv("BOT_TOKEN")

# Replace 'YOUR_BOT_TOKEN' with your actual bot token from the Discord Developer Portal
TOKEN = bot_token

# Enable necessary intents
intents = discord.Intents.default()
intents.message_content = True  # Allows the bot to read message content

# Prefix for bot commands
bot = commands.Bot(command_prefix="!", intents=intents)

# ID of the role that is allowed to set the timer (replace with your role ID)
ALLOWED_ROLE_ID = 1306268971078520922  # Replace with actual role ID

# Variable to store the timer task
timer_task = None

# Event: Bot ready notification
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Command: Set Timer
@bot.command(name="settimer")
async def set_timer(ctx, time_in_minutes: int):
    # Check if the user has the allowed role
    if ALLOWED_ROLE_ID not in [role.id for role in ctx.author.roles]:
        await ctx.send("You do not have permission to set the timer.")
        return
    
    # Cancel any existing timer
    global timer_task
    if timer_task:
        timer_task.cancel()

    # Start a new timer
    await ctx.send(f"Timer set for {time_in_minutes} minutes.")
    timer_task = bot.loop.create_task(timer_countdown(ctx, time_in_minutes))

# Function: Timer countdown with notifications
async def timer_countdown(ctx, time_in_minutes):
    try:
        # Wait for the specified time in seconds
        await asyncio.sleep(time_in_minutes * 60)
        
        # Notify in the text channel
        await ctx.send("Time's up!.")

        # Play sound in the voice channel if the user is connected
        if ctx.author.voice:  # Check if the author is in a voice channel
            voice_channel = ctx.author.voice.channel
            vc = await voice_channel.connect()

            # Ensure audio file path is correct
            audio_source = discord.FFmpegPCMAudio("darius-stimming-made-with-Voicemod.mp3")  # Ensure this file exists in the same folder
            if not audio_source.is_opus():
                vc.play(audio_source)
                await asyncio.sleep(10)  # Play for 10 seconds
                await vc.disconnect()
            else:
                await ctx.send("Error: Audio file is in an unsupported format.")
        else:
            await ctx.send("You're not in a voice channel, so the alarm can't be played")

    except asyncio.CancelledError:
        await ctx.send("Timer was canceled.")

# Run the bot
bot.run(TOKEN)
