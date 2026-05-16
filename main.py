import discord
from discord.ext import commands
from datetime import datetime, timedelta
import random

TOKEN = "MTUwNTE2NzE1MTYxNzgwMjI3Mg.GTJ84f.FLCRK4AGQMRAXPEPEliQsSqVuNyDjC9erSjL7I" 
GUILD_ID = 1495457163009851412 
DROP_CHANNEL_ID = 1504474153846051007 

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="do!", intents=intents)

# ------------------ COOLDOWN ------------------
cooldowns = {}
COOLDOWN_HOURS = 4
COOLDOWN = timedelta(hours=COOLDOWN_HOURS)

# ------------------ ZAPISANE EMBEDY ------------------
saved_embeds = {}   # {user_id: discord.Embed}

# ------------------ READY ------------------
@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}')
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f'Synced {len(synced)} komend slash.')
    except Exception as e:
        print(e)

# ------------------ DROP COMMAND ------------------
@bot.tree.command(name="drop", description="Drop normalny", guild=discord.Object(id=GUILD_ID))
async def drop(interaction: discord.Interaction):
    if interaction.channel.id != DROP_CHANNEL_ID:
        await interaction.response.send_message(
            f"> `❌` Dropu możesz użyć tylko na <#{DROP_CHANNEL_ID}>!", ephemeral=True
        )
        return

    user_id = interaction.user.id
    now = datetime.now()

    if user_id in cooldowns:
        expiration = cooldowns[user_id] + COOLDOWN
        if now >= expiration:
            del cooldowns[user_id]
        else:
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

    roll = random.random() * 30
    reward_text = None
    is_win = False

    if roll < 2:
        reward_text = "20%"
        is_win = True
    elif roll < 5:
        reward_text = "15%"
        is_win = True
    elif roll < 8:
        reward_text = "10%"
        is_win = True

    if is_win:
        embed = discord.Embed(
            title="🏆︲WYGRANA × Drop | Sprawdziany & Kartkówki 4U",
            description=f"> Gratulacje wygrałeś zniżke: `{reward_text}`",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="📛︲PRZEGRANA × Drop | Sprawdziany & Kartkówki 4U",
            description="> Niestety nic nie **wygrałeś!**",
            color=discord.Color.red()
        )

    embed.set_image(url="https://i.imgur.com/QoD8aA5.png")
    await interaction.followup.send(content=f"<@{user_id}>", embed=embed)

# ------------------ EMBED CREATOR MODAL ------------------
class EmbedCreatorModal(discord.ui.Modal, title="Tworzenie embeda"):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.TextInput(label="Tytuł embeda", style=discord.TextStyle.short, required=True))
        self.add_item(discord.ui.TextInput(label="Opis embeda", style=discord.TextStyle.paragraph, required=True))
        self.add_item(discord.ui.TextInput(label="Kolor HEX (#rrggbb)", style=discord.TextStyle.short, required=True))
        self.add_item(discord.ui.TextInput(label="Stopka (opcjonalnie)", style=discord.TextStyle.short, required=False))
        self.add_item(discord.ui.TextInput(
            label="Dodatkowe pole (Tytuł + Opis)", 
            style=discord.TextStyle.paragraph, 
            required=False,
            placeholder="Pierwsza linia = tytuł pola\nKolejne linie = opis pola"
        ))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            title = self.children[0].value
            description = self.children[1].value
            color_hex = self.children[2].value
            footer = self.children[3].value.strip() if self.children[3].value else None
            extra = self.children[4].value.strip() if self.children[4].value else None

            try:
                color = int(color_hex.replace("#", ""), 16)
            except:
                color = 0xFFFFFF

            embed = discord.Embed(title=title, description=description, color=color)
            
            if footer:
                embed.set_footer(text=footer)

            if extra:
                lines = extra.split("\n", 1)
                field_name = lines[0].strip() if lines else "\u200b"
                field_value = lines[1].strip() if len(lines) > 1 else "\u200b"
                if field_name or field_value:
                    embed.add_field(name=field_name or "\u200b", value=field_value or "\u200b", inline=False)

            saved_embeds[interaction.user.id] = embed

            await interaction.followup.send(
                "✅ **Embed został zapisany!**\nWpisz `do!send` na kanale, na którym chcesz go wysłać.", 
                ephemeral=True
            )

        except Exception as e:
            print(f"[Embed Error] {e}")
            await interaction.followup.send(f"❌ Błąd: {e}", ephemeral=True)

# ------------------ SLASH COMMAND ------------------
@bot.tree.command(name="embed", description="Tworzenie embeda", guild=discord.Object(id=GUILD_ID))
async def embed_creator(interaction: discord.Interaction):
    await interaction.response.send_modal(EmbedCreatorModal())

# ------------------ PREFIX COMMAND - SEND ------------------
@bot.command(name="send")
async def send_embed(ctx):
    user_id = ctx.author.id

    if user_id not in saved_embeds:
        await ctx.send("❌ Nie masz zapisanych embedów. Użyj `/embed` najpierw.", delete_after=15)
        return

    embed = saved_embeds[user_id]
    
    # Wysyła na kanale, na którym użyto do!send
    await ctx.send(embed=embed)
    
    # Usuwamy z bazy po wysłaniu
    del saved_embeds[user_id]

    # Opcjonalnie usuwamy wiadomość z komendą
    try:
        await ctx.message.delete()
    except:
        pass

bot.run(TOKEN)
