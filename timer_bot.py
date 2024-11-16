import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import asyncio
from pynput import keyboard

# Load environment variables from .env file
load_dotenv()

# Access your bot token
bot_token = os.getenv("BOT_TOKEN")

# Replace 'YOUR_BOT_TOKEN' with your actual bot token from the Discord Developer Portal
TOKEN = bot_token

USER_ID = 756620918952034314  # Replace with your Discord user ID

# Enable necessary intents
intents = discord.Intents.default()
intents.message_content = True  # Allows the bot to read message content
intents.voice_states = True  # Enable voice state intents to check user presence in voice channels

# Prefix for bot commands
bot = commands.Bot(command_prefix="!", intents=intents)

# ID of the role that is allowed to set the timer (replace with your role ID)
ALLOWED_ROLE_ID = 1306244777825534022  # Replace with actual role ID

# Variable to store the timer task
timer_task = None

# Event: Bot ready notification
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

    # Start listening for the key sequence
    asyncio.create_task(listen_for_key_sequence())

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

# Function to join the user's current voice channel and play a sound
async def play_sound_in_user_channel():
    for guild in bot.guilds:
        # Get the member object for the user in this guild
        member = guild.get_member(USER_ID)
        if member and member.voice:  # Check if the user is connected to a voice channel
            voice_channel = member.voice.channel
            vc = await voice_channel.connect()
            vc.play(discord.FFmpegPCMAudio("lere-lund-ke (mp3cut.net).mp3"))  # Replace with your sound file
            await asyncio.sleep(5)  # Duration to play sound (adjust as needed)
            await vc.disconnect()
            return
    print("User is not in any voice channel.")

# Function to listen for key sequences asynchronously
async def listen_for_key_sequence():
    def on_press(key):
        try:
            # Listen for a specific key or key combination
            if key == keyboard.Key.f12:  # Replace with your desired key
                asyncio.run_coroutine_threadsafe(play_sound_in_user_channel(), bot.loop)
        except Exception as e:
            print(e)

    # Start the listener in a separate thread
    listener = keyboard.Listener(on_press=on_press)
    listener.start()


# Run the bot
bot.run(TOKEN)
