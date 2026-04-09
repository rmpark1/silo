import numpy as np

from cards import Card, Deck
from silo import Silo

def test_names():
    for i in range(52):
        print(Card(i))

def test_shuffle():
    d = Deck()
    print(d)
    d.shuffle()
    print(d)

def test_draw():
    d = Deck()
    print(d.draw())
    d.shuffle()
    print(d.draw())
    print(d)
    d.verify()

def test_verify():
    d = Deck()
    c = d.draw()
    d.add_card(c)
    d.add_card(c)
    assert not d.verify()

def test_deck_view():
    np.random.seed(0)
    d = Deck()
    d.shuffle()
    for i in range(3*13): d.draw()
    print(d)

def test_suit_ids():

    np.random.seed(0)
    d = Deck()
    d.shuffle()
    for i in range(40): d.draw()
    d.ids = d.suit_ids("C")
    print(d)

def test_playthrough():

    game = Silo()
    players = game.players
    south = players[0]
    game.show_hands()
    game.determine_roles()
    game.show_hands()
