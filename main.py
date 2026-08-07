import os
import random
import requests
import asyncio
from datetime import datetime
from dotenv import load_dotenv

import discord
from discord.ext import commands, tasks

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
API_ENDPOINT = "http://localhost:8000/execute"
REQUEST_TIMEOUT = 10

CHANNEL_NAMES = [
    "général",
    "test-sentinel-live",
    "discussions-techniques",
    "showcase-resultats",
    "statistiques-daily",
    "tutoriels-sentinel",
    "bugs-et-improvements",
    "defis-sentinel",
    "idees-futures",
]

ROLE_CONFIGS = [
    {"name": "🥉 Novice", "colour": discord.Colour.light_grey()},
    {"name": "🥈 Initiate", "colour": discord.Colour.blue()},
    {"name": "🥇 Sentinel Master", "colour": discord.Colour.gold()},
    {"name": "💎 Elite Commander", "colour": discord.Colour.purple()},
    {"name": "👑 Architect", "colour": discord.Colour.dark_gold()},
]

CHALLENGES = [
    "Crée un poème IA inspiré par la surveillance d'un réseau sous tension.",
    "Propose une recette robotisée pour un dîner équilibré en 5 ingrédients.",
    "Rédige une question bizarre que seul SENTINEL pourrait résoudre.",
    "Imagine un nouveau gadget pour aider les agents à gérer les micro-coupures.",
    "Décris une mission d'exploration de données dans un décor cyberpunk.",
]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


def get_channel_by_name(guild: discord.Guild, name: str) -> discord.TextChannel | None:
    return discord.utils.get(guild.text_channels, name=name)


async def setup_channels(guild: discord.Guild) -> None:
    category_name = "SENTINEL Command Center"
    category = discord.utils.get(guild.categories, name=category_name)
    if category is None:
        category = await guild.create_category(category_name)

    for channel_name in CHANNEL_NAMES:
        if get_channel_by_name(guild, channel_name) is None:
            await guild.create_text_channel(channel_name, category=category)


async def setup_roles(guild: discord.Guild) -> None:
    for role_config in ROLE_CONFIGS:
        role = discord.utils.get(guild.roles, name=role_config["name"])
        if role is None:
            await guild.create_role(
                name=role_config["name"],
                colour=role_config["colour"],
                mentionable=False,
            )


async def welcome_message(guild: discord.Guild) -> None:
    channel = get_channel_by_name(guild, "général")
    if channel is None:
        return

    embed = discord.Embed(
        title="🛡️ BIENVENUE COMMANDANT!",
        description=(
            "Vous entrez dans SENTINEL Command Center.\n"
            "Testez SENTINEL avec : `!sentinel <votre_prompt>`\n\n"
            "Discord : [lien]\n"
            "Hugging Face : [lien]\n"
            "GitHub : [lien]"
        ),
        colour=discord.Colour.green(),
        timestamp=datetime.utcnow(),
    )
    embed.set_footer(text="Sentinel · Command Center")
    await channel.send(embed=embed)


async def send_daily_challenge() -> None:
    for guild in bot.guilds:
        channel = get_channel_by_name(guild, "defis-sentinel")
        if channel is None:
            continue

        challenge = random.choice(CHALLENGES)
        embed = discord.Embed(
            title="🎯 Défi SENTINEL du jour",
            description=challenge,
            colour=discord.Colour.dark_teal(),
            timestamp=datetime.utcnow(),
        )
        embed.set_footer(text="Répondez dans le canal et faites bouger la communauté !")

        try:
            await channel.send(embed=embed)
        except Exception as exc:
            print(f"Erreur en envoyant le défi sur {guild.name}: {exc}")


@tasks.loop(hours=24)
async def daily_challenge_task() -> None:
    await bot.wait_until_ready()
    await send_daily_challenge()


@daily_challenge_task.before_loop
async def before_daily_challenge() -> None:
    await bot.wait_until_ready()


@bot.event
async def on_ready() -> None:
    print("🛡️ SENTINEL Discord Bot is ONLINE")
    for guild in bot.guilds:
        try:
            await setup_channels(guild)
            await setup_roles(guild)
            await welcome_message(guild)
        except Exception as exc:
            print(f"Erreur lors de la configuration du serveur {guild.name}: {exc}")

    if not daily_challenge_task.is_running():
        daily_challenge_task.start()


@bot.command(name="sentinel")
async def sentinel(ctx: commands.Context, *, prompt: str = None) -> None:
    if prompt is None or prompt.strip() == "":
        embed = discord.Embed(
            title="⚠️ Commande incomplète",
            description="Merci de préciser un prompt après `!sentinel`. Exemple : `!sentinel Vérifie mon code Python`.",
            colour=discord.Colour.orange(),
            timestamp=datetime.utcnow(),
        )
        await ctx.reply(embed=embed, mention_author=False)
        return

    embed = discord.Embed(
        title="🛰️ SENTINEL en cours d'exécution",
        description=f"Analyse en cours pour : **{prompt}**",
        colour=discord.Colour.blue(),
        timestamp=datetime.utcnow(),
    )
    message = await ctx.reply(embed=embed, mention_author=False)

    try:
        response = requests.post(
            API_ENDPOINT,
            json={"prompt": prompt},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        quality_score = data.get("quality_score", "N/A")
        execution_time = data.get("execution_time", "N/A")
        model_used = data.get("model_used", "N/A")
        result_text = data.get("output") or data.get("response") or "Aucune sortie disponible."

        result_embed = discord.Embed(
            title="✅ SENTINEL - Résultat obtenu",
            description=result_text,
            colour=discord.Colour.green(),
            timestamp=datetime.utcnow(),
        )
        result_embed.add_field(name="Score de qualité", value=str(quality_score), inline=True)
        result_embed.add_field(name="Temps d'exécution", value=str(execution_time), inline=True)
        result_embed.add_field(name="Modèle utilisé", value=str(model_used), inline=True)
        result_embed.set_footer(text="SENTINEL • Localhost API")

        await message.edit(embed=result_embed)
    except requests.exceptions.Timeout:
        error_embed = discord.Embed(
            title="⏱️ Délai d'attente dépassé",
            description=(
                "Le service local n'a pas répondu à temps."
                " Veuillez réessayer dans quelques instants."
            ),
            colour=discord.Colour.red(),
            timestamp=datetime.utcnow(),
        )
        await message.edit(embed=error_embed)
    except requests.exceptions.RequestException as exc:
        error_embed = discord.Embed(
            title="❌ Erreur réseau",
            description=(
                "Impossible de contacter `http://localhost:8000/execute`."
                f" Détail : {exc}"
            ),
            colour=discord.Colour.red(),
            timestamp=datetime.utcnow(),
        )
        await message.edit(embed=error_embed)
    except ValueError:
        error_embed = discord.Embed(
            title="❌ Réponse invalide",
            description="Le service local a renvoyé un format inattendu.",
            colour=discord.Colour.red(),
            timestamp=datetime.utcnow(),
        )
        await message.edit(embed=error_embed)
    except Exception as exc:
        error_embed = discord.Embed(
            title="💥 Erreur inattendue",
            description=f"Une erreur est survenue lors de l'exécution : {exc}",
            colour=discord.Colour.red(),
            timestamp=datetime.utcnow(),
        )
        await message.edit(embed=error_embed)


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("Erreur : DISCORD_TOKEN non trouvé. Veuillez créer un fichier .env avec DISCORD_TOKEN=<votre_token>.")
        raise SystemExit(1)

    try:
        bot.run(DISCORD_TOKEN)
    except Exception as exc:
        print(f"Échec du démarrage du bot Discord : {exc}")
        raise
