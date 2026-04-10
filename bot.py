import discord
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

teams = {}
solos = {"tank": [], "heal": [], "dps": []}
event_locked = False


class MainView(discord.ui.View):

    @discord.ui.button(label="Créer équipe", style=discord.ButtonStyle.green)
    async def create_team(self, interaction: discord.Interaction, button: discord.ui.Button):

        if event_locked:
            await interaction.response.send_message("Inscriptions fermées", ephemeral=True)
            return

        await interaction.response.send_modal(CreateTeamModal())


    @discord.ui.button(label="Rejoindre équipe", style=discord.ButtonStyle.blurple)
    async def join_team(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_modal(JoinTeamModal())


    @discord.ui.button(label="Inscription Solo", style=discord.ButtonStyle.gray)
    async def solo(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_modal(SoloModal())


    @discord.ui.button(label="Voir équipes", style=discord.ButtonStyle.secondary)
    async def view(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(title="Mythic+ Teams", color=discord.Color.blue())

        for name, team in teams.items():

            tank = team["tank"] or "—"
            heal = team["heal"] or "—"
            dps = ", ".join(team["dps"]) or "—"

            embed.add_field(
                name=name,
                value=f"Tank: {tank}\nHeal: {heal}\nDPS: {dps}",
                inline=False
            )

        embed.add_field(
            name="Solos",
            value=f"Tank: {', '.join(solos['tank'])}\n"
                  f"Heal: {', '.join(solos['heal'])}\n"
                  f"DPS: {', '.join(solos['dps'])}",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


class CreateTeamModal(discord.ui.Modal, title="Créer équipe"):

    team_name = discord.ui.TextInput(label="Nom équipe")

    async def on_submit(self, interaction: discord.Interaction):

        if self.team_name.value in teams:
            await interaction.response.send_message("Equipe existe déjà", ephemeral=True)
            return

        teams[self.team_name.value] = {"tank": None, "heal": None, "dps": []}

        await interaction.response.send_message(
            f"Equipe {self.team_name.value} créée",
            ephemeral=True
        )


class JoinTeamModal(discord.ui.Modal, title="Rejoindre équipe"):

    team_name = discord.ui.TextInput(label="Nom équipe")
    role = discord.ui.TextInput(label="Role (tank/heal/dps)")

    async def on_submit(self, interaction: discord.Interaction):

        if self.team_name.value not in teams:
            await interaction.response.send_message("Equipe inexistante", ephemeral=True)
            return

        team = teams[self.team_name.value]

        role = self.role.value.lower()

        if role == "tank":
            if team["tank"]:
                await interaction.response.send_message("Tank déjà pris", ephemeral=True)
                return
            team["tank"] = interaction.user.name

        elif role == "heal":
            if team["heal"]:
                await interaction.response.send_message("Heal déjà pris", ephemeral=True)
                return
            team["heal"] = interaction.user.name

        elif role == "dps":
            if len(team["dps"]) >= 3:
                await interaction.response.send_message("DPS complet", ephemeral=True)
                return
            team["dps"].append(interaction.user.name)

        await interaction.response.send_message("Inscription réussie", ephemeral=True)


class SoloModal(discord.ui.Modal, title="Inscription Solo"):

    role = discord.ui.TextInput(label="Role (tank/heal/dps)")

    async def on_submit(self, interaction: discord.Interaction):

        solos[self.role.value].append(interaction.user.name)

        await interaction.response.send_message(
            "Inscription solo réussie",
            ephemeral=True
        )


@bot.tree.command(name="event", description="Créer message inscription")
@app_commands.describe(note="Description de l'événement")
async def event(interaction: discord.Interaction, note: str = None):

    description = "Cliquez sur les boutons pour vous inscrire"

    if note:
        description += f"\n\n📌 **Note :**\n{note}"

    embed = discord.Embed(
        title="Mythic+ League Inscription",
        description=description,
        color=discord.Color.green()
    )

    await interaction.response.send_message(
        embed=embed,
        view=MainView()
    )


@bot.tree.command(name="reset", description="Reset event")
async def reset(interaction: discord.Interaction):

    teams.clear()
    solos["tank"].clear()
    solos["heal"].clear()
    solos["dps"].clear()

    await interaction.response.send_message("Event reset")


@bot.event
async def on_ready():
    print(f"{bot.user} est connecté")
    await bot.tree.sync()


import os

bot.run(os.getenv("DISCORD_TOKEN"))