'''shut up pylint'''
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


class game:
    members = []
    chanelid = 0
    game_running = False
    numwolves = 0


@bot.slash_command(description="Start the werewolf game")
async def start(inter, numwolves: int):
    if game.game_running is False:
        game.numwolves = numwolves
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
async def help_listener(inter: disnake.MessageInteraction):
    if game.game_running is False:
        if inter.data.custom_id == "join":
            game.members.append(inter.author)
            await inter.send(f"You have joined, the players are {game.members}", ephemeral=True)
        
    else:
        await inter.send("Sorry game has started", ephemeral=True)

f = open("token.txt", encoding="utf8")
token = f.read()
f.close()
bot.run(token)
