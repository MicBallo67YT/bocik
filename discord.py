import discord
from discord import app_commands
from discord.ext import commands, tasks
import random
import asyncio
from datetime import datetime, timedelta

TOKEN = "TWÓJ_TOKEN"  # <- wklej tutaj swój token
GUILD_ID = 123456789012345678  # <- wklej ID swojego serwera
DROP_CHANNEL_ID = 123456789012345678  # <- wklej ID kanału drop

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Słownik cooldownów użytkowników
cooldowns = {}
COOLDOWN_HOURS = 5  # 5 godzin cooldown
COOLDOWN = timedelta(hours=COOLDOWN_HOURS)


@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}')
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f'Synced {len(synced)} komend slash.')
    except Exception as e:
        print(e)


# ---------------- DROP COMMAND ----------------
@bot.tree.command(name="drop", description="Drop zwykły", guild=discord.Object(id=GUILD_ID))
async def drop(interaction: discord.Interaction):
    if interaction.channel.id != DROP_CHANNEL_ID:
        await interaction.response.send_message(
            f"> `❌` Dropu możesz użyć tylko na <#{DROP_CHANNEL_ID}>!", ephemeral=True
        )
        return

    user_id = interaction.user.id
    now = datetime.now()

    # Sprawdzenie cooldownu
    if user_id in cooldowns:
        expiration = cooldowns[user_id] + COOLDOWN
        if now < expiration:
            remaining = expiration - now
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            await interaction.response.send_message(
                f"> `⏳` Musisz poczekać jeszcze **{hours}h {minutes}m {seconds}s** przed ponownym użyciem komendy!",
                ephemeral=True
            )
            return

    cooldowns[user_id] = now
    await interaction.response.defer()

    # Losowanie nagrody
    roll = random.random() * 100
    reward_text = None
    is_win = False

    if roll < 1:
        reward_text = "20%"
        is_win = True
    elif roll < 5:
        reward_text = "10%"
        is_win = True
    elif roll < 7:
        reward_text = "5%"
        is_win = True

    if is_win:
        embed = discord.Embed(
            title="🏆︲WYGRANA × PRIMECODE",
            description=f"> Gratulacje wygrałeś zniżke: `{reward_text}`",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="📛︲PRZEGRANA × PRIMECODE",
            description="> Niestety nic nie **wygrałeś!**",
            color=discord.Color.red()
        )

    embed.set_image(url="https://i.imgur.com/Fl5oGsE.png")
    await interaction.followup.send(content=f"<@{user_id}>", embed=embed)


# ---------------- EMBED CREATOR MODAL ----------------
class EmbedCreatorModal(discord.ui.Modal, title="Ostatni krok »"):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.TextInput(label="Tytuł", custom_id="embedTitle", style=discord.TextStyle.short, required=True))
        self.add_item(discord.ui.TextInput(label="Opis", custom_id="embedDescription", style=discord.TextStyle.paragraph, required=True))
        self.add_item(discord.ui.TextInput(label="Kolor HEX (np. #ff0000)", custom_id="embedColor", style=discord.TextStyle.short, required=True))

    async def on_submit(self, interaction: discord.Interaction):
        title = self.children[0].value
        description = self.children[1].value
        color_hex = self.children[2].value

        try:
            color = int(color_hex.replace("#", ""), 16)
        except ValueError:
            color = 0xFFFFFF

        embed = discord.Embed(title=title, description=description, color=color)
        await interaction.response.send_message(embed=embed)


@bot.tree.command(name="embed-creator", description="Otwiera modal do stworzenia embeda", guild=discord.Object(id=GUILD_ID))
async def embed_creator(interaction: discord.Interaction):
    await interaction.response.send_modal(EmbedCreatorModal())


bot.run(TOKEN)
