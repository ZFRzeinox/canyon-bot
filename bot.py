import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Chargement du token Discord
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Requis pour détecter la venue des nouveaux membres

class CanyonBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Synchronisation des commandes slash avec Discord
        await self.tree.sync()
        print("✅ Commandes Slash synchronisées avec succès !")

bot = CanyonBot()

@bot.event
async def on_ready():
    print(f"🚀 Canyon Bot est en ligne ! Connecté en tant que {bot.user.name}")
    # Statut personnalisable
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name="Canyon Interactive Games | /studio"
        )
    )

# ---------------------------------------------------------
# 👥 ACCUEIL AUTOMATIQUE
# ---------------------------------------------------------

@bot.event
async def on_member_join(member):
    # Recherche du salon d'accueil par nom
    welcome_channel = discord.utils.get(member.guild.text_channels, name="📌-│-welcome") or \
                      discord.utils.get(member.guild.text_channels, name="welcome")
    
    if welcome_channel:
        embed = discord.Embed(
            title=f"👋 Bienvenue chez Canyon Interactive, {member.display_name} !",
            description=(
                f"Ravi de te compter parmi nous {member.mention} !\n\n"
                "• Prends connaissance des règles dans <#📜-│-rules>\n"
                "• N'hésite pas à te présenter dans <#👋-│-introduce-yourself>\n"
                "• Suis les coulisses du développement dans <#🛠️-│-dev-previews>"
            ),
            color=discord.Color.dark_orange()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="Canyon Interactive Community", icon_url=member.guild.icon.url if member.guild.icon else None)
        await welcome_channel.send(embed=embed)

# ---------------------------------------------------------
# 📣 COMMANDES ADMINISTRATEUR / STAFF
# ---------------------------------------------------------

# 1. Commande d'Annonce Officielle
@bot.tree.command(name="announcement", description="[STAFF] Publie une annonce officielle du studio.")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    title="Titre de l'annonce",
    message="Contenu de l'annonce",
    ping_everyone="Mentoinner @everyone ? (True/False)"
)
async def announcement(interaction: discord.Interaction, title: str, message: str, ping_everyone: bool = False):
    embed = discord.Embed(
        title=f"📢 {title}",
        description=message,
        color=discord.Color.gold()
    )
    embed.set_author(name="Canyon Interactive — Annonce Officielle", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
    embed.set_footer(text=f"Publié par {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

    # Trouve le salon studio-announcements
    target_channel = discord.utils.get(interaction.guild.text_channels, name="📢-│-studio-announcements") or interaction.channel

    content = "@everyone" if ping_everyone else None
    await target_channel.send(content=content, embed=embed)
    await interaction.response.send_message(f"✅ Annonce publiée dans {target_channel.mention} !", ephemeral=True)


# 2. Commande de Patch Notes
@bot.tree.command(name="patch", description="[STAFF] Publie une note de mise à jour (Patch Notes).")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(platform=[
    app_commands.Choice(name="🧱 Roblox", value="Roblox"),
    app_commands.Choice(name="💻 Steam / PC", value="Steam / PC"),
    app_commands.Choice(name="🎮 Console (PS5 / Xbox)", value="Console"),
    app_commands.Choice(name="📱 Mobile", value="Mobile"),
    app_commands.Choice(name="🌐 Global / Studio", value="Global")
])
@app_commands.describe(
    version="Ex: v1.0.2",
    platform="Plateforme concernée",
    changes="Détails des changements / correctifs"
)
async def patch(interaction: discord.Interaction, version: str, platform: app_commands.Choice[str], changes: str):
    embed = discord.Embed(
        title=f"📝 Patch Notes — {version} ({platform.name})",
        description=changes,
        color=discord.Color.green()
    )
    embed.set_author(name="Canyon Interactive — Dev Team", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
    embed.set_footer(text=f"Déployé par {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

    # Trouve le salon patch-notes
    target_channel = discord.utils.get(interaction.guild.text_channels, name="📝-│-patch-notes") or interaction.channel

    await target_channel.send(embed=embed)
    await interaction.response.send_message(f"✅ Patch notes publiés dans {target_channel.mention} !", ephemeral=True)


# 3. Commande Dev Preview / Sneak Peek
@bot.tree.command(name="preview", description="[STAFF] Partage un aperçu exclusif de dev.")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    title="Titre du Dev Preview",
    description="Explications / Contexte",
    image_url="Lien direct vers une image/GIF (Optionnel)"
)
async def preview(interaction: discord.Interaction, title: str, description: str, image_url: str = None):
    embed = discord.Embed(
        title=f"🛠️ Dev Preview : {title}",
        description=description,
        color=discord.Color.purple()
    )
    if image_url:
        embed.set_image(url=image_url)
    embed.set_footer(text="Canyon Labs • Work in Progress")

    # Trouve le salon dev-previews
    target_channel = discord.utils.get(interaction.guild.text_channels, name="🛠️-│-dev-previews") or interaction.channel

    await target_channel.send(embed=embed)
    await interaction.response.send_message(f"✅ Preview partagée dans {target_channel.mention} !", ephemeral=True)


# Gestion des erreurs de permission pour le staff
@announcement.error
@patch.error
@preview.error
async def admin_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Réservé aux administrateurs de Canyon Interactive.", ephemeral=True)

# ---------------------------------------------------------
# 🌐 COMMANDES PUBLIQUES (Tout le monde)
# ---------------------------------------------------------

@bot.tree.command(name="studio", description="Découvre l'histoire et la vision de Canyon Interactive.")
async def studio(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🏔️ Canyon Interactive",
        description=(
            "**Bienvenue chez Canyon Interactive !**\n\n"
            "**Notre Histoire :**\n"
            "Fondé par une équipe de passionnés, Canyon Interactive est un studio indépendant dédié à la création d'expériences de jeu innovantes, immersives et multiplateformes (PC, Console, Roblox & Mobile).\n\n"
            "**Notre Philosophie :**\n"
            "Proposer un gamedev transparent, proche de sa communauté, avec des mises à jour régulières et à l'écoute des retours joueurs !"
        ),
        color=discord.Color.dark_orange()
    )
    embed.add_field(name="🔗 Rejoindre la communauté", value="https://discord.gg/9HzQWdYy5c", inline=False)
    embed.set_footer(text="Canyon Interactive Games", icon_url=bot.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="socials", description="Affiche les réseaux sociaux officiels du studio.")
async def socials(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🌐 Réseaux Sociaux & Liens Officiels",
        description="Retrouvez Canyon Interactive partout sur le web :",
        color=discord.Color.blue()
    )
    embed.add_field(name="💬 Discord Officiel", value="https://discord.gg/9HzQWdYy5c", inline=False)
    # Tu pourras ajouter ici d'autres liens (Twitter/X, Roblox Group, YouTube, etc.)
    embed.set_footer(text="Canyon Interactive")
    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)