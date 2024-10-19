import random

# Define the roles


class Role:
    def __init__(self, name):
        self.name = name


class Werewolf(Role):
    def __init__(self):
        super().__init__("Werewolf")


class Villager(Role):
    def __init__(self):
        super().__init__("Villager")

# Define the player


class Player:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.alive = True

    def __str__(self):
        return f"{self.name} ({'alive' if self.alive else 'dead'}) - {self.role.name}"

# Define the game


class WerewolfGame:
    def __init__(self, players):
        self.players = players
        self.day = True  # Start with day phase

    def get_alive_players(self):
        return [p for p in self.players if p.alive]

    def get_alive_werewolves(self):
        return [p for p in self.get_alive_players() if isinstance(p.role, Werewolf)]

    def get_alive_villagers(self):
        return [p for p in self.get_alive_players() if isinstance(p.role, Villager)]

    def night_phase(self):
        print("Night falls. Werewolves, choose someone to eliminate.")
        werewolves = self.get_alive_werewolves()
        victims = self.get_alive_villagers()

        if victims:
            victim_name = input(f"Werewolves, choose a victim from: {[p.name for p in victims]}: ")
            victim = next((p for p in victims if p.name == victim_name), None)
            if victim:
                victim.alive = False
                print(f"{victim.name} was killed by the werewolves.")
            else:
                print("Invalid victim chosen. No one was killed.")
        else:
            print("No victims available. The werewolves did not kill anyone.")

    def day_phase(self):
        print("Day breaks. Villagers, choose someone to eliminate.")
        suspects = self.get_alive_players()

        if suspects:
            suspect_name = input(f"Villagers, choose a suspect from: {
                                [p.name for p in suspects]}: ")
            suspect = next(
                (p for p in suspects if p.name == suspect_name), None)
            if suspect:
                suspect.alive = False
                print(f"{suspect.name} was voted out by the villagers.")
            else:
                print("Invalid suspect chosen. No one was voted out.")
        else:
            print("No suspects available. No one was voted out.")

    def check_game_over(self):
        werewolves = self.get_alive_werewolves()
        villagers = self.get_alive_villagers()

        if not werewolves:
            print("All werewolves are dead. Villagers win!")
            return True
        elif len(werewolves) >= len(villagers):
            print("Werewolves have taken over. Werewolves win!")
            return True
        return False

    def play(self):
        while not self.check_game_over():
            if self.day:
                self.day_phase()
            else:
                self.night_phase()
            self.day = not self.day  # Switch between day and night phases
            self.show_status()

    def show_status(self):
        print("\nCurrent status:")
        for player in self.players:
            print(player)
        print()


# Initialize players
player_names = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
roles = [Werewolf(), Villager(), Villager(), Villager(), Villager()]
random.shuffle(roles)

players = [Player(name, role) for name, role in zip(player_names, roles)]

# Start the game
game = WerewolfGame(players)
game.play()


