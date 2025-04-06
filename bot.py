# Fix for Windows event loop issue
import sys
import asyncio

if sys.platform.startswith("win") and sys.version_info >= (3, 8):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import os
import discord
import subprocess
import re
import logging
from dotenv import load_dotenv
from collections import defaultdict
import time
from discord.ext import commands
from email_validator import validate_email, EmailNotValidError  # Add email-validator library

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

# Initialize bot with default help command disabled
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Cooldown mechanism
cooldowns = defaultdict(int)

# List of disposable email domains (you can expand this list)
DISPOSABLE_DOMAINS = [
    "tempmail.com",
    "10minutemail.com",
    "guerrillamail.com",
    "mailinator.com"
]

def is_valid_email(email):
    """
    Validate email using email-validator library.
    This ensures stricter validation and checks for common issues.
    """
    try:
        # Validate the email format and domain
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def has_valid_mx_records(domain):
    """
    Check if the domain has valid MX records (mail servers).
    """
    try:
        import dns.resolver
        dns.resolver.resolve(domain, 'MX')
        return True
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
        return False

def is_on_cooldown(user_id, cooldown_seconds=10):
    """Prevent spamming by enforcing a cooldown."""
    current_time = time.time()
    last_used = cooldowns[user_id]
    if current_time - last_used < cooldown_seconds:
        return True
    cooldowns[user_id] = current_time
    return False

def parse_output(output):
    """
    Parse the output to extract found websites and categorize them.
    Example output:
        [+] Facebook: Found
        [+] Twitter: Found
        [-] Website2: Not Found
    """
    social_media = []
    other_websites = []

    # List of known social media platforms
    SOCIAL_MEDIA_PLATFORMS = [
        "facebook", "twitter", "instagram", "linkedin", "pinterest", "tiktok", "reddit"
    ]

    for line in output.splitlines():
        if "[+]" in line:  # Only include lines marked as found
            website = line.split("[+]")[1].strip().split(":")[0].strip().lower()
            if any(platform in website for platform in SOCIAL_MEDIA_PLATFORMS):
                social_media.append(website)
            else:
                other_websites.append(website)

    return social_media, other_websites

async def send_results(channel, author, email):
    try:
        # Step 1: Validate email format
        if not is_valid_email(email):
            await channel.send("❌ Invalid email address. Please enter a valid email.")
            return

        # Step 2: Extract domain and check for disposable domains
        domain = email.split("@")[-1].lower()
        if domain in DISPOSABLE_DOMAINS:
            await channel.send("❌ Disposable email domains are not allowed.")
            return

        # Step 3: Check for valid MX records
        if not has_valid_mx_records(domain):
            await channel.send("❌ The domain does not have valid mail servers.")
            return

        # Step 4: Check cooldown
        if is_on_cooldown(author.id):
            await channel.send("⏳ Please wait before running another query.")
            return

        # Send a combined loading message
        loading_message = await channel.send("🚀 Initiating reconnaissance protocol... Stand by.")

        # Run subprocess
        result = subprocess.run(
            ["holehe", email],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            raise Exception(result.stderr.strip())

        # Parse the output to extract found websites
        social_media, other_websites = parse_output(result.stdout)

        # Delete the loading message
        await loading_message.delete()

        # Create an embed for the results
        embed = discord.Embed(
            title=f"📧 Results for {email}",
            description="Websites where the email was found are listed below.",
            color=discord.Color.green()
        )

        if social_media:
            embed.add_field(
                name="📱 Social Media",
                value="\n".join([f"- {site.capitalize()}" for site in social_media]),
                inline=False
            )

        if other_websites:
            embed.add_field(
                name="🌐 Other Websites",
                value="\n".join([f"- {site.capitalize()}" for site in other_websites]),
                inline=False
            )

        if not social_media and not other_websites:
            await channel.send("❌ No websites found associated with this email.")
            return

        # Send the embed as a DM
        await author.send(embed=embed)
        await channel.send("✅ Results sent to your DMs.")

    except Exception as e:
        logging.error(f"Error: {e}")
        await channel.send("❌ An error occurred while processing your request.")

@bot.event
async def on_ready():
    print(f"[+] Logged in as {bot.user}")

    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

@bot.tree.command(name="recon", description="Check which websites an email is registered on.")
async def recon(interaction: discord.Interaction, email: str):
    await interaction.response.defer()  # Defer the response to avoid timeout
    await send_results(interaction.channel, interaction.user, email)

@bot.tree.command(name="help", description="Get help with the bot.")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📝 Email Recon Bot Help",
        description="This bot helps you find websites where an email is registered.",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="How It Works",
        value=(
            "Use `/recon <email>` to check which websites an email is registered on.\n"
            "The bot will analyze the provided email and send the results to your DMs."
        ),
        inline=False
    )
    embed.add_field(
        name="Cooldown",
        value="You can only run one query every 10 seconds to prevent abuse.",
        inline=False
    )
    embed.add_field(
        name="Example",
        value="`/recon example@example.com`",
        inline=False
    )
    embed.add_field(
        name="Important Notes",
        value=(
            "- Disposable email domains are not allowed.\n"
            "- Ensure the email is valid and associated with real websites.\n"
            "- Use responsibly!"
        ),
        inline=False
    )
    embed.set_footer(text="Email Recon Bot | Use responsibly")
    await interaction.response.send_message(embed=embed)

# Run the bot
bot.run(TOKEN)
