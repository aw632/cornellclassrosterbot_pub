import discord
from discord_slash import SlashCommand # Importing the newly installed library.
from discord_slash.utils import manage_commands

client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the client.

guild_ids = [800022005856075796] # Put your server ID in this array.

@client.event
async def on_ready():
    print("Ready!")

@slash.slash(
  name="get",
  description="gets information about a class",
  options=[manage_commands.create_option(
    name = "subject_name",
    description = "the subject acronym, i.e. 'CS' for Computer Science",
    option_type = 3,
    required = True
  ), manage_commands.create_option(
    name = "class_number",
    description = "4 digit class number",
    option_type = 4,
    required = True
  ), manage_commands.create_option(
    name = "semester",
    description = "look up a specific semester (i.e. FA20 for Fall 2020)",
    option_type = 3,
    required = False
  )],
  guild_ids=guild_ids
)

async def _test(ctx, subject_name: str, class_number: int, semester = None):
    await ctx.respond()
    await ctx.send(f"You responded with {subject_name} and {class_number} and the semester was {semester}.")

client.run("ODE2MDcwNDk0NTM2MzM1Mzkw.YD1m3w.zFoTu6gPoqQfxpxuNoXBB5Ug0TE")
