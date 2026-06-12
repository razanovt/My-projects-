import asyncio
import time
from collections import defaultdict

import discord
from discord.ext import commands

# ---------------- НАСТРОЙКИ ----------------

LOG_CHANNEL_ID = 1514949446260097124
MUTE_ROLE_ID = 1513305097353035816

VOICE_CHANNEL_ID = 1513305918312546374

ALLOWED_VOICE_CHANNELS = [
    1513305918312546374,
]

IMMUNE_ROLES = [
    1513840435230015558,
    1513301313558151259,
    1513301481296494762,
]

MUTE_TIME = 600       # 10 минут
SPAM_LIMIT = 5        # действий
SPAM_WINDOW = 30      # секунд

# -------------------------------------------

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

voice_activity = defaultdict(list)


# ---------------- ON READY ----------------

@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")

    channel = bot.get_channel(VOICE_CHANNEL_ID)

    if channel:
        vc = discord.utils.get(bot.voice_clients, guild=channel.guild)

        if not vc:
            try:
                await channel.connect(timeout=30, reconnect=True)
                print(f"Подключился к голосовому: {channel.name}")
            except Exception as e:
                print(f"Ошибка подключения к войсу: {e}")


# ---------------- VOICE EVENT ----------------

@bot.event
async def on_voice_state_update(member, before, after):
    try:
        if member.bot:
            return

        log_channel = bot.get_channel(LOG_CHANNEL_ID)

        # -------- ЛОГИ --------

        if log_channel:

            if before.channel is None and after.channel is not None:
                await log_channel.send(
                    f"📥 {member.display_name} зашел в {after.channel.mention}"
                )

            elif before.channel is not None and after.channel is None:
                await log_channel.send(
                    f"📤 {member.display_name} вышел из {before.channel.mention}"
                )

            elif before.channel != after.channel:
                await log_channel.send(
                    f"🔄 {member.display_name} перешел из "
                    f"{before.channel.mention} в {after.channel.mention}"
                )

        # -------- АНТИФЛУД --------

        if after.channel is None:
            return

        if after.channel.id not in ALLOWED_VOICE_CHANNELS:
            return

        if any(role.id in IMMUNE_ROLES for role in member.roles):
            return

        now = time.time()

        voice_activity[member.id].append(now)

        # чистим старые события
        voice_activity[member.id] = [
            t for t in voice_activity[member.id]
            if now - t <= SPAM_WINDOW
        ]

        # проверка спама
        if len(voice_activity[member.id]) < SPAM_LIMIT:
            return

        guild = member.guild
        mute_role = guild.get_role(MUTE_ROLE_ID)

        if not mute_role:
            print("❌ Роль мута не найдена")
            return

        if mute_role in member.roles:
            return

        # -------- МУТ --------

        await member.add_roles(mute_role, reason="Флуд в голосовых")

        try:
            await member.edit(mute=True, reason="Флуд в голосовых")
        except Exception as e:
            print(f"voice mute error: {e}")

        try:
            await member.move_to(None, reason="Флуд в голосовых")
        except Exception as e:
            print(f"disconnect error: {e}")

        if log_channel:
            await log_channel.send(
                f"🚨 {member.display_name} получил мут на {MUTE_TIME // 60} мин за флуд"
            )

        # -------- АВТОРАЗМУТ --------

        async def unmute():
            await asyncio.sleep(MUTE_TIME)

            try:
                updated = guild.get_member(member.id)

                if updated and mute_role in updated.roles:
                    await updated.remove_roles(mute_role, reason="Авторазмут")

                    if log_channel:
                        await log_channel.send(
                            f"🔊 {updated.display_name} автоматически размучен"
                        )

            except Exception as e:
                print(f"unmute error: {e}")

        asyncio.create_task(unmute())

        voice_activity[member.id].clear()

    except Exception as e:
        print(f"voice event error: {e}")


# ---------------- RUN ----------------

bot.run("Your Tokken")