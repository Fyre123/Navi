# nsmb-bigarena.py

from datetime import datetime
import re

import discord
from discord.ext import commands

from database import errors, reminders, users
from resources import emojis, exceptions, functions, settings


class NotSoMiniBossBigArenaCog(commands.Cog):
    """Cog that contains the not so mini boss and big arena detection commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Runs when a message is sent in a channel."""
        if message.author.id != settings.EPIC_RPG_ID: return
        if message.embeds: return
        message_content = message.content
        if ('successfully registered for the next **big arena** event!' in message_content.lower()
            or 'successfully registered for the next **minin\'tboss** event!' in message_content.lower()
            or 'you are already registered!' in message_content.lower()):
            user_name = None
            user = await functions.get_interaction_user(message)
            slash_command = True if user is not None else False
            if user is None:
                if message.mentions:
                    user = message.mentions[0]
                else:
                    try:
                        user_name = re.search("^\*\*(.+?)\*\*,", message_content).group(1)
                        user_name = await functions.encode_text(user_name)
                    except Exception as error:
                        await message.add_reaction(emojis.WARNING)
                        await errors.log_error(f'User not found in big-arena or not-so-mini-boss message: {message_content}')
                        return
                    for member in message.guild.members:
                        member_name = await functions.encode_text(member.name)
                        if member_name == user_name:
                            user = member
                            break
            if user is None:
                await message.add_reaction(emojis.WARNING)
                await errors.log_error(f'User not found in big-arena or not-so-mini-boss message: {message_content}')
                return
            try:
                user_settings: users.User = await users.get_user(user.id)
            except exceptions.FirstTimeUserError:
                return
            if not user_settings.bot_enabled: return
            if slash_command:
                interaction = await functions.get_interaction(message)
                user_command = '/big arena' if interaction.name == 'big' else '/minint'
                user_command = f'{user_command} join: true'
            else:
                message_history = await message.channel.history(limit=50).flatten()
                user_command_message = None
                for msg in message_history:
                    if msg.content is not None:
                        if ((msg.content.lower().startswith('rpg ')
                            and 'big arena join' in msg.content.lower() or 'minintboss join' in msg.content.lower())
                            and msg.author == user):
                            user_command_message = msg
                            break
                if user_command_message is None:
                    await message.add_reaction(emojis.WARNING)
                    await errors.log_error('Couldn\'t find a command for the big-arena or not-so-mini-boss message.')
                    return
                user_command = user_command_message.content.lower()
            if 'minint' in user_command:
                if not user_settings.alert_not_so_mini_boss.enabled: return
                event = 'minin\'tboss'
                reminder_message = user_settings.alert_not_so_mini_boss.message.replace('{event}', event)
            else:
                if not user_settings.alert_big_arena.enabled: return
                event = 'big-arena'
                reminder_message = user_settings.alert_big_arena.message.replace('{event}', event.replace('-',' '))
            timestring = re.search("next event is in \*\*(.+?)\*\*", message_content).group(1)
            time_left = await functions.parse_timestring_to_timedelta(timestring.lower())
            bot_answer_time = message.created_at.replace(microsecond=0, tzinfo=None)
            current_time = datetime.utcnow().replace(microsecond=0)
            time_elapsed = current_time - bot_answer_time
            time_left = time_left - time_elapsed
            reminder: reminders.Reminder = (
                await reminders.insert_user_reminder(user.id, event, time_left,
                                                     message.channel.id, reminder_message)
            )
            if reminder.record_exists:
                await message.add_reaction(emojis.NAVI)
            else:
                if settings.DEBUG_MODE: await message.add_reaction(emojis.CROSS)


# Initialization
def setup(bot):
    bot.add_cog(NotSoMiniBossBigArenaCog(bot))