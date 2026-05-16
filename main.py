import discord
from discord import app_commands
from discord.ext import commands, tasks
import random
import asyncio
from datetime import datetime, timedelta

TOKEN = "MTUwNTE2NzE1MTYxNzgwMjI3Mg.GTJ84f.FLCRK4AGQMRAXPEPEliQsSqVuNyDjC9erSjL7I"  # <- wklej tutaj swój token
GUILD_ID = 1495457163009851412  # <- wklej ID swojego serwera
DROP_CHANNEL_ID = 1504474153846051007 # <- wklej ID kanału drop

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="do!", intents=intents)

# Słownik cooldownów użytkowników
cooldowns = {}
COOLDOWN_HOURS = 4  # 4 godziny cooldown
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
@bot.tree.command(name="drop", description="Drop normalny", guild=discord.Object(id=GUILD_ID))
async def drop(interaction: discord.Interaction):
    if interaction.channel.id != DROP_CHANNEL_ID:
        await interaction.response.send_message(
            f"> `❌` Dropu możesz użyć tylko na <#{DROP_CHANNEL_ID}>! [Sprawdziany & Kartkówki 4U DROPIK :D]", ephemeral=True
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
                f"> `⏳` Musisz poczekać jeszcze **{hours}h {minutes}m {seconds}s** przed ponownym użyciem Dropu.",
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
        reward_text = "15%"
        is_win = True
    elif roll < 7:
        reward_text = "10%"
        is_win = True

    if is_win:
        embed = discord.Embed(
            title="🏆︲WYGRANA × Sprawdziany & Kartówki 4U Dropik :DD",
            description=f"> Gratulacje wygrałeś zniżke: `{reward_text}`",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="📛︲PRZEGRANA × Sprawdziany & Kartkówki 4U",
            description="> Niestety nic nie **wygrałeś!**",
            color=discord.Color.red()
        )

    embed.set_image(url="https://i.imgur.com/QoD8aA5.png")
    await interaction.followup.send(content=f"<@{user_id}>", embed=embed)


# ---------------- NOWY EMBED CREATOR MODAL ----------------
class EmbedCreatorModal(discord.ui.Modal, title="Tworzenie embeda"):
    def __init__(self):
        super().__init__()

        # Podstawowe
        self.add_item(discord.ui.TextInput(label="Tytuł embeda", custom_id="embedTitle", style=discord.TextStyle.short, required=True))
        self.add_item(discord.ui.TextInput(label="Opis embeda", custom_id="embedDesc", style=discord.TextStyle.paragraph, required=True))
        self.add_item(discord.ui.TextInput(label="Kolor HEX (#rrggbb)", custom_id="embedColor", style=discord.TextStyle.short, required=True))
        self.add_item(discord.ui.TextInput(label="Stopka (opcjonalnie)", custom_id="embedFooter", style=discord.TextStyle.short, required=False))

        # 4 pola opcjonalne
        for i in range(1, 5):
            self.add_item(discord.ui.TextInput(label=f"Pole {i} - Tytuł (opcjonalnie)", custom_id=f"field{i}title", style=discord.TextStyle.short, required=False))
            self.add_item(discord.ui.TextInput(label=f"Pole {i} - Opis (opcjonalnie)", custom_id=f"field{i}desc", style=discord.TextStyle.paragraph, required=False))

    async def on_submit(self, interaction: discord.Interaction):
        title = self.children[0].value
        description = self.children[1].value
        color_hex = self.children[2].value
        footer = self.children[3].value

        # Konwersja koloru
        try:
            color = int(color_hex.replace("#",""), 16)
        except:
            color = 0xFFFFFF  # domyślny biały

        embed = discord.Embed(title=title, description=description, color=color)
        if footer:
            embed.set_footer(text=footer)

        # Dodawanie pól
        for i in range(1,5):
            field_title = self.children[3 + (i-1)*2 + 1].value
            field_desc = self.children[3 + (i-1)*2 + 2].value
            if field_title or field_desc:
                embed.add_field(name=field_title if field_title else "\u200b", value=field_desc if field_desc else "\u200b", inline=False)

        # Najpierw ephemerala wiadomość dla użytkownika
        await interaction.response.send_message("✅ Pomyślnie wysłano embed", ephemeral=True)

        # Wysyłamy embed anonimowo na tym samym kanale używając followup
        await interaction.followup.send(embed=embed, ephemeral=False)


@bot.tree.command(name="embed-creator", description="Tworzenie embeda", guild=discord.Object(id=GUILD_ID))
async def embed_creator(interaction: discord.Interaction):
    await interaction.response.send_modal(EmbedCreatorModal())


bot.run(TOKEN)
