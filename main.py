'''shut up pylint'''
import random
import disnake
from disnake.ext import commands

intents = disnake.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True  # Required for managing roles


command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True

bot = commands.InteractionBot(
    test_guilds=[1012004094564646992],
    command_sync_flags=command_sync_flags,
)


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.author = None
        self.members = []
        self.nicks = []
        self.channel = None
        self.game_running = False
        self.numwolves = 0
        self.roles = {}  # Store player roles for easy access

    def add_member(self, member):
        if member not in self.members:
            self.members.append(member)
            self.nicks.append(member.name)

game = Game()
@bot.slash_command(name="force_stop", description="Force stops the warewolf game")
async def force_stop(inter):
    game.reset()
    await inter.send("Game stopped", ephemeral=True)


@bot.slash_command(description="Start the werewolf game")
async def start(inter, numwolves: int):
    if game.game_running is False:
        game.numwolves = numwolves
        game.author = inter.author
        game.channel = inter.channel
        game.members = []
        # reply's to original message to allow people to enter
        await inter.response.send_message("Press button to enter",
            components=[
                disnake.ui.Button(
                    label="Join", style=disnake.ButtonStyle.success, custom_id="join")
            ],)
        # dms user with button to   
        await inter.author.send("Press button to start",
            components=[
                disnake.ui.Button(
                    label="Start", style=disnake.ButtonStyle.success, custom_id="start")
            ],)
    else:
        await inter.send("Sorry game has started", ephemeral=True)


@bot.listen("on_button_click")
async def handle_button_click(inter: disnake.MessageInteraction):
    if inter.data.custom_id == "join":
        if game.game_running:
            await inter.send("The game has already started.", ephemeral=True)
            return

        if inter.author in game.members:
            await inter.send("You are already in the game.", ephemeral=True)
            return
        # Add the player to the game
        game.add_member(inter.author)
        await inter.send(f"You have joined! Current players: {game.nicks}", ephemeral=True)

    elif inter.data.custom_id == "start" and inter.author == game.author:
        if game.game_running:
            await inter.send("The game is already running.", ephemeral=True)
            return
        if len(game.members) < game.numwolves + 1:
            await inter.send("Not enough players for the selected number of werewolves.", ephemeral=True)
            return
        game.game_running = True
        await inter.send("The game has started!", ephemeral=True)
        await start_game()


async def dmplayers(members, message):
    for player in members:
        await player.send(message)

async def start_game():
    await dmplayers(game.members, f"Game started with {game.numwolves} werewolves!")
    await assign_roles(game.members, game.numwolves)
    await night_phase()

async def assign_roles(members, numwolves):
    werewolves = random.sample(members, numwolves)
    for player in members:
        if player in werewolves:
            game.roles[player] = "Werewolf"
            await player.send(f"You are a werewolf. Your fellow werewolves are: {', '.join([w.name for w in werewolves if w != player])}")
        else:
            game.roles[player] = "Villager"
            await player.send("You are a villager")



async def night_phase():

    await day_phase()

async def day_phase():

    await check_game_status()

async def collect_votes(voters, choices, phase):

    return target



async def eliminate_player(player):
    return player

async def check_game_status():
    werewolf_count = len([player for player in game.members if game.roles.get(player) == "Werewolf"])
    villager_count = len(game.members) - werewolf_count

    if werewolf_count == 0:
        await dmplayers(game.members, "Villagers win! All werewolves have been eliminated.")
        game.reset()
    else:
        # Continue to the next night phase if the game is not yet over
        await night_phase()



f = open("token.txt", encoding="utf8")
token = f.read()
f.close()
bot.run(token)
