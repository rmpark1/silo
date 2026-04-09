import copy

import numpy as np
import pandas as pd

# Club Diamond Heart Spade
SUITS = "CDHS"
RANK = "23456789TJKQA"

class Card(object):

    def __init__(self, id=0):
        self.id = id
        self.rank = id%len(RANK)
        self.string = RANK[id%len(RANK)] + SUITS[id//len(RANK)]

    def __lt__(self, other):
        return self.rank < other.rank

    def __repr__(self):
        return self.string

class Deck(object):

    def __init__(self, n=len(RANK)*len(SUITS)):
        self.ids = np.arange(n)
        self.size = n

    def shuffle(self):
        np.random.shuffle(self.ids)

    def sort(self):
        self.ids = np.sort(self.ids)

    def get_sorted(self, rev=False):
        d = copy.deepcopy(self)
        d.sort()
        if rev: d.ids = d.ids[::-1]
        return d

    def suit_ids(self, suit):
        suit_id = SUITS.index(suit)
        start = len(RANK)*suit_id
        stop = len(RANK)*(1+suit_id)
        return self.ids[np.logical_and(
            self.ids>=start, self.ids<stop)]

    def draw(self):
        x = Card(self.ids[0])
        self.ids = self.ids[1:]
        self.size -= 1
        return x

    def add_card(self, card):
        self.ids = np.concatenate((self.ids, np.array([card.id])))
        self.shuffle()

    def verify(self):
        """Ensure there are no duplicates."""
        self.sort()
        return np.all(np.unique(self.ids) == self.ids)

    def __repr__(self):
        sorted = self.get_sorted(rev=True)
        suits = {i: [] for i in SUITS[::-1]}
        size = 0
        for i in sorted.ids:
            c = Card(i)
            l = suits[c.string[1]]
            l.append(c.string[0])
            size = max(size, len(l))
        for suit in SUITS:
            suits[suit] += ["X" for i in range(size-len(suits[suit]))]
        df = pd.DataFrame(suits)
        if not len(df.index): return "Empty"
        lines = df.to_string().split("\n")
        s = f"{' '.join(lines[0].split())}\n"+"\n".join(
            [" ".join(l.split()[1:]) for l in lines[1:]])
        s = s.replace("X", " ")
        return s
