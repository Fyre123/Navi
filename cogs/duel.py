# duel.py

from datetime import datetime
import re

import discord
from discord.ext import commands

from database import errors, reminders, users
from resources import emojis, exceptions, functions, settings


class DuelCog(commands.Cog):
    """Cog that contains the duel detection commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Runs when a message is sent in a channel."""
        if message.author.id != settings.EPIC_RPG_ID: return

        if message.embeds:
            embed: discord.Embed = message.embeds[0]
            message_author = message_title = icon_url = ''
            if embed.author:
                message_author = str(embed.author.name)
                icon_url = embed.author.icon_url
            if embed.title: message_title = str(embed.title)

            # Daily cooldown
            if 'you have been in a duel recently' in message_title.lower():
                user_id = user_name = None
                user = await functions.get_interaction_user(message)
                if user is None:
                    try:
                        user_id = int(re.search("avatars\/(.+?)\/", icon_url).group(1))
                    except:
                        try:
                            user_name = re.search("^(.+?)'s cooldown", message_author).group(1)
                            user_name = await functions.encode_text(user_name)
                        except Exception as error:
                            await message.add_reaction(emojis.WARNING)
                            await errors.log_error(f'User not found in duel cooldown message: {message.embeds[0].fields}')
                            return
                    if user_id is not None:
                        user = await message.guild.fetch_member(user_id)
                    else:
                        for member in message.guild.members:
                            member_name = await functions.encode_text(member.name)
                            if member_name == user_name:
                                user = member
                                break
                if user is None:
                    await message.add_reaction(emojis.WARNING)
                    await errors.log_error(f'User not found in duel cooldown message: {message.embeds[0].fields}')
                    return
                try:
                    user_settings: users.User = await users.get_user(user.id)
                except exceptions.FirstTimeUserError:
                    return
                if not user_settings.bot_enabled or not user_settings.alert_duel: return
                timestring = re.search("wait at least \*\*(.+?)\*\*...", message_title).group(1)
                time_left = await functions.parse_timestring_to_timedelta(timestring.lower())
                bot_answer_time = message.created_at.replace(microsecond=0, tzinfo=None)
                current_time = datetime.utcnow().replace(microsecond=0)
                time_elapsed = current_time - bot_answer_time
                time_left = time_left - time_elapsed
                reminder_message = user_settings.alert_duel.message.replace('{command}', 'rpg duel')
                reminder: reminders.Reminder = (
                    await reminders.insert_user_reminder(user.id, 'duel', time_left,
                                                         message.channel.id, reminder_message)
                )
                if reminder.record_exists:
                    await message.add_reaction(emojis.NAVI)
                else:
                    if settings.DEBUG_MODE: await message.add_reaction(emojis.CROSS)


# Initialization
def setup(bot):
    bot.add_cog(DuelCog(bot))