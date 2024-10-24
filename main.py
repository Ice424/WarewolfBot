'''shut up pylint'''
import random
import asyncio
from collections import defaultdict
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
    test_guilds=[1012004094564646992, 873251935602499654],
    command_sync_flags=command_sync_flags,
)


class Game:
    '''Game class for storing global variables'''

    def __init__(self):
        self.reset()
        self.author = None
        self.members = []
        self.alive = []
        self.names = []
        self.channel = None
        self.game_running = False
        self.numwolves = 0
        self.roles = defaultdict(list)  # Store player roles for easy access
        self.votes = {}  # Store votes from players
        self.voters = []  # List of players eligible to vote
        self.voting_messages = []  # Store the voting messages sent to players
        self.phase = "night"

    def reset(self):
        '''Resets all variables'''
        self.author = None
        self.members = []
        self.alive = []
        self.names = []
        self.channel = None
        self.game_running = False
        self.numwolves = 0
        self.roles = defaultdict(list)  # Store player roles for easy access
        self.votes = {}  # Store votes from players
        self.voters = []  # List of players eligible to vote
        self.voting_messages = []  # Store the voting messages sent to players
        self.phase = "night"

    def add_member(self, member):
        '''Adds a member to the game'''
        if member not in self.members:
            self.members.append(member)
            self.names.append(member.name)
            self.alive.append(member)

    def reset_votes(self):
        '''Resets the votes and voting messages'''
        self.votes = {}
        self.voting_messages = []

    def remove_member(self, member):
        '''Adds a member to the game'''
        self.alive.remove(member)
        self.names.remove(member.name)
        if member in self.roles["werewolf"]:
            self.roles["werewolf"].remove(member)
        else:
            self.roles["villager"].remove(member)


game = Game()


@bot.slash_command(name="reset", description="Reset's the werewolf game DOES NOT STOP IT")
async def reset(inter):
    game.reset()
    await inter.send("Game variable reset", ephemeral=True)


@bot.slash_command(description="Start the werewolf game")
async def start(inter, numwolves: int):
    if game.game_running is False:
        game.numwolves = numwolves
        game.author = inter.author
        game.channel = inter.channel
        # reply's to original message to allow people to enter
        await inter.response.send_message("Press button to enter",
                                components=[
                                    disnake.ui.Button(
                                        label="Join",
                                        style=disnake.ButtonStyle.success,
                                        custom_id="join")
                                ],)
        # dms user with button to
        await inter.author.send("Press button to start",
                                components=[
                                    disnake.ui.Button(
                                        label="Start",
                                        style=disnake.ButtonStyle.success,
                                        custom_id="start")
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
        await inter.send(f"You have joined! Current players: {game.names}", ephemeral=True)
        print(f"{inter.author} Joined")
        
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


@bot.listen("on_dropdown")
async def handle_dropdown_click(inter: disnake.MessageInteraction):
    if inter.data.custom_id == "voting":
        if inter.author in game.voters:
            game.votes[inter.author] = inter.values[0]  # Record the vote
            await inter.send(f"You voted for {inter.values[0]}", ephemeral=True)


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
            game.roles["werewolf"].append(player)
            await player.send(f"You are a werewolf. Your fellow werewolves are: {', '.join([w.name for w in werewolves if w != player])}")
        else:
            game.roles["villager"].append(player)
            await player.send("You are a villager")
    print(f"members {game.members}")
    print(f"names {game.names}")
    print(f"roles {game.roles}")


async def night_phase():
    game.phase = "night"
    await initiate_votes(game.roles["werewolf"], game.roles["villager"], 30)
    if await check_game_status():
        await day_phase()


async def day_phase():
    game.phase = "day"
    await initiate_votes(game.alive, game.alive, 100)
    if await check_game_status():
        await night_phase()


async def initiate_votes(voters, choices, time):
    game.reset_votes()
    voting_messages = []  # To store messages so we can delete them later
    game.voters = voters
    # Set voting message based on phase
    msg = f"Vote for a player to eliminate you have {time}s" if game.phase == "day" else f"Vote for a player to kill you have {time}s"

    # Send the vote message to each player and store the message object
    for player in voters:
        voting_msg = await player.send(
            msg,
            components=[
                disnake.ui.StringSelect(custom_id="voting",
                                        options=[disnake.SelectOption(label=str(choice.name),
                                        value=str(choice.name)) for choice in choices])
            ]
        )
        voting_messages.append(voting_msg)  # Store the message object

    def has_everyone_voted():
        return len(game.votes) == len(voters)

    # Check every second if either all votes are in or 30 seconds passed
    for i in range(time):
        if has_everyone_voted():
            break
        if i % 5 == 0:
            for voting_msg in voting_messages:
                try:
                    await voting_msg.edit(content=msg)
                except Exception as e:
                    print(f"Failed to edit message: {e}")
        await asyncio.sleep(1)
        
    if not has_everyone_voted():
        print("Timeout: Not all players voted within 30 seconds.")

    # Delete all voting messages after the vote has closed
    for voting_msg in voting_messages:
        try:
            await voting_msg.delete()
        except Exception as e:
            print(f"Failed to delete message: {e}")

    # Process votes after the voting period ends
    await process_votes(game.votes)


async def process_votes(votes):
    vote_counts = {}

    for voter, choice in votes.items():
        if choice not in vote_counts:
            vote_counts[choice] = 0
        vote_counts[choice] += 1

    if not vote_counts:
        await dmplayers(game.voters, "No votes were cast. Skipping elimination.")
        return

    max_votes = max(vote_counts.values())

    tied_players = [player for player,
                    count in vote_counts.items() if count == max_votes]

    if len(tied_players) > 1:
        await dmplayers(game.voters, "There was a tie, you may now chose between the tied contestants")
        await initiate_votes(tied_players, game.voters, 30)
    else:

        eliminated = tied_players[0]

        if game.phase == "night":
            await dmplayers(game.voters, f"You have slain {eliminated}")
            await game.members[game.names.index(eliminated)].send("The werewolf's have killed you")
        else:
            await dmplayers(game.voters, f"{eliminated} has been voted out")
            await game.members[game.names.index(eliminated)].send("The villager's voted you out")

        game.remove_member(game.members[game.names.index(eliminated)])


async def check_game_status():
    werewolf_count = len(game.roles["werewolf"])
    villager_count = len(game.roles["villager"])

    if werewolf_count == 0:
        await dmplayers(game.members, "Villagers win! All werewolves have been eliminated.")
        return False
    if villager_count == 0:
        await dmplayers(game.members, "Werewolf's win! All villagers have been killed.")
        return False

    return True


f = open("token.txt", encoding="utf8")
token = f.read()
f.close()
bot.run(token)