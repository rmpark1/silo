import numpy as np
import hipc

import cards
import view

# The player roles (heirarchy), gained early in the game.
ROLES = "JQKA"
# The physical location of each player (south, west, north, east)
SPOTS = "SWNE"

class Policy(object):

    def __init__(self):
        self.domestic = []
        self.foreign = []

class Player(object):

    def __init__(self, spot):
        self.spot = spot
        # Role not yet assigned
        self.role = None

        # Cards in hand
        self.knowledge_base = {}
        self.hand = cards.Deck(n=0)
        self.policy = Policy()

    def make_action(self, game, options):
        """Override in base class"""
        pass

    def __repr__(self):
        s = f"({self.spot})"
        if self.role is not None: s = f"{self.role} {s}"
        return s


class RandomPlayer(Player):

    def make_action(self, game, options):
        return np.random.choice(options)

def RandomPlayer(object):
    pass

# TODO
class HumanCLI(Player):

    def make_action():
        return np.random.choice(options)

class Silo(object):
    """Encode the silo game state."""

    def __init__(self, p=hipc.Parameters()):
        # Hyperparemeters
        self.p = SiloParameters()(**p.map())
        p = self.p
        np.random.seed(p.seed)

        ### Players gather with cards

        # Players, sitting clockwise, starting with the south (dealer)
        self.players = [Player(SPOTS[j]) for j in range(4)]
        self.deck = cards.Deck()

        ### Game begins

        # Someone shuffles the deck
        self.deck.shuffle()
        # First, deal out all the cards to everyone
        self.deal_war()
        # Deterministically find the roles.
        self.determine_roles()
        self.stage = "policy"

        # for year in range(1, p.years+1):
        #     self.select_policy()

    def select_policy():
        pass

    def deal_war(self):
        size = self.deck.size
        for i in range(size):
            player = self.players[i%4]
            player.hand.add_card(self.deck.draw())

    def determine_roles(self):
        """All players show their top ranked card of each suit (ace high)."""
        remaining = [p for p in self.players]
        for role_id in range(4):
            max_ids = [(max_empty(p.hand.suit_ids(cards.SUITS[::-1][role_id])), p)
                       for p in remaining]
            winner = max(max_ids)[1]
            winner.role = ROLES[::-1][role_id]
            remaining = [p for p in remaining if p is not winner]

    def show_hands(self):

        bar = "\u2500"
        merged = ""
        desc = lambda n: f"{self.players[n]}\n{bar*7}\n{self.players[n].hand}"
        height = lambda s: len(s.split("\n"))

        north = desc(2)
        blank = (7*" "+"\n")*height(north)
        top = view.horizontal_join([blank, north, blank])

        west, east = desc(1), desc(3)
        blank = (7*" "+"\n")*max(height(west), height(east))
        middle = view.horizontal_join([west, blank, east])

        south = desc(0)
        blank = (7*" "+"\n")*height(south)
        bottom = view.horizontal_join([blank, south, blank])

        all = "\n".join([top, middle, bottom])
        print("Player hands:\n")
        print(all)

class SiloParameters(hipc.Parameters):
    seed=1
    years=5
    
def max_empty(items):
    if not len(items): return 1
    return max(items)
