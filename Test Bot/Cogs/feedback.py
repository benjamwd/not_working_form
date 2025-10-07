import os
import discord
from discord import app_commands
from discord.ext import commands
from utils.bot import DClient  # your existing bot subclass

GUILD_ID = 1424690290148511848  # <-- replace with your server ID

class FeedbackModal(discord.ui.Modal, title="Submit Feedback"):
    def __init__(self, target_channel: discord.abc.Messageable | None):
        super().__init__()
        self.target_channel = target_channel
        self.feedback = discord.ui.TextInput(
            label="Your feedback",
            style=discord.TextStyle.paragraph,
            max_length=1000,
            required=True,
        )
        self.add_item(self.feedback)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        content = str(self.feedback.value).strip()
        if not content:
            return await interaction.response.send_message("Feedback cannot be empty.", ephemeral=True)
        if self.target_channel is not None:
            await self.target_channel.send(embed=discord.Embed(
                title="New Feedback",
                description=content,
                color=discord.Color.blurple(),
                ).set_author(name=f"{interaction.user}")
            )
        await interaction.response.send_message("Thank you for your feedback!", ephemeral=True)


class SuggestionModal(discord.ui.Modal, title="Submit Suggestion"):
    def __init__(self, target_channel: discord.abc.Messageable | None):
        super().__init__()
        self.target_channel = target_channel
        self.title_input = discord.ui.TextInput(label="Title", style=discord.TextStyle.short, max_length=80, required=True)
        self.desc_input = discord.ui.TextInput(label="Description", style=discord.TextStyle.paragraph, max_length=1000, required=False)
        self.add_item(self.title_input)
        self.add_item(self.desc_input)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        title = str(self.title_input.value).strip()
        desc = str(self.desc_input.value or "").strip()
        if not title:
            return await interaction.response.send_message("Title is required.", ephemeral=True)
        if self.target_channel is not None:
            msg = await self.target_channel.send(embed=discord.Embed(
                title=title,
                description=desc or " ",
                color=discord.Color.green(),
            ).set_author(name=f"{interaction.user}"))
            try:
                await msg.add_reaction("👍")
                await msg.add_reaction("👎")
            except Exception:
                pass
        await interaction.response.send_message("Suggestion submitted!", ephemeral=True)


class Feedback(commands.Cog):
    def __init__(self, client: DClient) -> None:
        super().__init__()
        self.client = client

    @app_commands.command(name="feedback", description="Open a modal to submit feedback")
    async def feedback(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(FeedbackModal(interaction.channel))

    @app_commands.command(name="suggest", description="Open a modal to submit a feature suggestion")
    async def suggest(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(SuggestionModal(interaction.channel))


async def setup(client: DClient):
    await client.add_cog(Feedback(client))


# --- Bot setup for testing ---
intents = discord.Intents.default()
intents.message_content = True
bot = DClient(intents=intents)

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)  # sync commands to this guild only
    print(f"Logged in as {bot.user}. Commands synced for testing guild.")
    print(bot.tree.get_commands(guild=discord.Object(id=GUILD_ID)))

bot.run(os.getenv("DISCORD_TOKEN"))



