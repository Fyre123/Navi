# main.py
"""Contains error handling and the help and about commands"""

from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands import errors

from database import errors, guilds
from resources import emojis, exceptions, logs, settings, tasks


class MainCog(commands.Cog):
    """Cog with events and help and about commands"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Commands
    @commands.command(name='help', aliases=('h',))
    @commands.bot_has_permissions(send_messages=True, embed_links=True, read_message_history=True)
    async def main_help(self, ctx: commands.Context) -> None:
        """Main help command"""
        if ctx.prefix.lower() == 'rpg ':
            return
        embed = await embed_main_help(ctx)
        await ctx.respond(embed=embed)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, external_emojis=True, add_reactions=True, read_message_history=True)
    async def ascended(self, ctx: commands.Context, *args) -> None:
        """Ascended command detection"""
        if ctx.prefix.lower() == 'rpg ' and len(args) >= 1:
            arg1 = args[0].lower()
            args = list(args)
            command = None
            if arg1 == 'hunt':
                command = self.bot.get_command(name='hunt')
            elif arg1 in ('adventure','adv',):
                command = self.bot.get_command(name='adventure')
            elif arg1 in ('tr','training','ultr','ultraining'):
                command = self.bot.get_command(name='training')
            elif arg1 in ('chop','axe','bowsaw','chainsaw','fish','net','boat','bigboat','pickup','ladder','tractor',
                          'greenhouse','mine','pickaxe','drill','dynamite',):
                command = self.bot.get_command(name='chop')
            elif arg1 in ('big','not',):
                command = self.bot.get_command(name='big')
            elif arg1 in ('farm',):
                command = self.bot.get_command(name='farm')

            if command is not None:
                await command.callback(command.cog, ctx, args)

    @commands.command(aliases=('ping','info'))
    async def about(self, ctx: commands.Context) -> None:
        """Shows some info about Tatl"""
        if ctx.prefix.lower() == 'rpg ':
            return
        start_time = datetime.utcnow()
        message = await ctx.send('Testing API latency...')
        end_time = datetime.utcnow()
        api_latency = end_time - start_time
        embed = await embed_about(self.bot, api_latency)
        await message.edit(content=None, embed=embed)


     # Events
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """Runs when an error occurs and handles them accordingly.
        Interesting errors get written to the database for further review.
        """
        async def send_error() -> None:
            """Sends error message as embed"""
            embed = discord.Embed(title='An error occured')
            embed.add_field(name='Command', value=f'`{ctx.command.qualified_name}`', inline=False)
            embed.add_field(name='Error', value=f'```py\n{error}\n```', inline=False)
            await ctx.reply(embed=embed)

        if isinstance(error, (commands.CommandNotFound, commands.NotOwner)):
            return
        elif isinstance(error, commands.DisabledCommand):
            await ctx.reply(f'Command `{ctx.command.qualified_name}` is temporarily disabled.')
        elif isinstance(error, (commands.MissingPermissions, commands.MissingRequiredArgument,
                                commands.TooManyArguments, commands.BadArgument)):
            await send_error()
        elif isinstance(error, commands.BotMissingPermissions):
            if 'send_messages' in error.missing_permissions:
                return
            if 'embed_links' in error.missing_perms:
                await ctx.replay(error)
            else:
                await send_error()
        elif isinstance(error, exceptions.FirstTimeUserError):
            await ctx.reply(
                f'**{ctx.author.name}**, looks like I don\'t know you yet.\n'
                f'Use `{ctx.prefix}on` to activate me first.',
                mention_author=False
            )
        else:
            await errors.log_error(error, ctx)
            await send_error()

    # Events
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Fires when bot has finished starting"""
        startup_info = f'{self.bot.user.name} has connected to Discord!'
        print(startup_info)
        logs.logger.info(startup_info)
        tasks.schedule_reminders.start()
        tasks.delete_old_reminders.start()
        tasks.reset_clans.start()
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                                 name='your commands'))
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Fires when bot joins a guild. Sends a welcome message to the system channel."""
        try:
            guild_settings: guilds.Guild = guilds.get_guild(guild.id)
            welcome_message = (
                f'Hey! **{guild.name}**! I\'m here to remind you to do your Epic RPG commands!\n\n'
                f'Note that reminders are off by default. If you want to get reminded, please use '
                f'`{guild_settings.prefix}on` to activate me.\n'
                f'If you don\'t like this prefix, use `{guild_settings.prefix}setprefix` to change it.\n\n'
                f'Tip: If you ever forget the prefix, simply ping me with a command.'
            )
            await guild.system_channel.send(welcome_message)
        except:
            return


# Initialization
def setup(bot):
    bot.add_cog(MainCog(bot))


# --- Embeds ---
async def embed_main_help(ctx: commands.Context) -> discord.Embed:
    """Main menu embed"""
    guild = await guilds.get_guild(ctx.guild.id)
    prefix = guild.prefix

    reminder_management = (
        f'{emojis.BP} `{prefix}list` : List all your active reminders\n'
        f'{emojis.BP} `{prefix}rm` : Manage custom reminders'
    )

    user_settings = (
        f'{emojis.BP} `{prefix}on` / `off` : Turn the bot on/off\n'
        f'{emojis.BP} `{prefix}settings` : Check your settings\n'
        f'{emojis.BP} `{prefix}donator` : Set your EPIC RPG donator tier\n'
        f'{emojis.BP} `{prefix}enable` / `disable` : Enable/disable specific reminders\n'
        f'{emojis.BP} `{prefix}dnd on` / `off` : Turn DND mode on/off (disables pings)\n'
        f'{emojis.BP} `{prefix}hardmode on` / `off` : Turn hardmode mode on/off (tells your partner to hunt solo)\n'
        f'{emojis.BP} `{prefix}ruby on` / `off` : Turn the ruby counter on/off\n'
        f'{emojis.BP} `{prefix}tr-helper on` / `off` : Turn the training helper on/off\n'
        f'{emojis.BP} `{prefix}ruby` : Check your current ruby count'
    )

    partner_settings = (
        f'{emojis.BP} `{prefix}partner` : Set your marriage partner\n'
        f'{emojis.BP} `{prefix}partner donator` : Set your partner\'s EPIC RPG donator tier\n'
        f'{emojis.BP} `{prefix}partner channel` : Set the channel for incoming lootbox alerts'
    )

    guild_settings = (
        f'{emojis.BP} `rpg guild list` : Add/update your guild\n'
        f'{emojis.BP} `{prefix}guild leaderboard` : Check the weekly raid leaderboard\n'
        f'{emojis.BP} `{prefix}guild channel` : Set the channel for guild reminders\n'
        f'{emojis.BP} `{prefix}guild on` / `off` : Turn guild reminders on or off\n'
        f'{emojis.BP} `{prefix}guild stealth` : Set your stealth threshold'
    )

    server_settings = (
        f'{emojis.BP} `{prefix}prefix` : Check the bot prefix\n'
        f'{emojis.BP} `{prefix}setprefix` / `{prefix}sp` : Set the bot prefix'
    )

    embed = discord.Embed(
        color = settings.EMBED_COLOR,
        title = 'NAVI',
        description =   f'Hey! **{ctx.author.name}**! Hello!'
    )
    embed.add_field(name='REMINDERS', value=reminder_management, inline=False)
    embed.add_field(name='USER SETTINGS', value=user_settings, inline=False)
    embed.add_field(name='PARTNER SETTINGS', value=partner_settings, inline=False)
    embed.add_field(name='GUILD SETTINGS', value=guild_settings, inline=False)
    embed.add_field(name='SERVER SETTINGS', value=server_settings, inline=False)

    await ctx.reply(embed=embed, mention_author=False)


async def embed_about(bot: commands.Bot, api_latency: datetime) -> discord.Embed:
    """Bot info embed"""
    general = (
        f'{emojis.BP} {len(bot.guilds):,} servers\n'
        f'{emojis.BP} {round(bot.latency * 1000):,} ms bot latency\n'
        f'{emojis.BP} {round(api_latency.total_seconds() * 1000):,} ms API latency'
    )
    creator = f'{emojis.BP} Miriel#0001'
    embed = discord.Embed(color = settings.EMBED_COLOR, title = 'ABOUT NAVI')
    embed.add_field(name='BOT STATS', value=general, inline=False)
    embed.add_field(name='CREATOR', value=creator, inline=False)

    return embed