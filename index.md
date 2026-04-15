You play as the leader of a nation state granted the power to make unthinkable
decisions on behalf of your constituents. Is it worth the win?

It is playable with a standard 52-card deck, but custom art
is available.

- Four players, each starting with their own unique advantages.
- Each player represents the leader of a nation-state
- Everyone can lose if player behavior becomes too aggressive

## Sequence of play

1. [Role Determination](#role-determination)
2. Year 1
    - 3.1 [Policy Selection](#policy-selection)
    - 3.2 [Trade](#trade)
    - 3.3 [Event Play](#event-play)
    - 3.4 [Resolution](#resolution)
    - 3.5 [Victory Check](#victory-check)
3. Repeat for 5 years or until a player achieves [Victory](#victory-check)
or until [Complete and Total Destruction](#complete-and-total-destruction)


## Role Determination

- Choose one dealer to deal the entire deck (exclude Jokers) to each player.
Everyone should have 13 cards.

- Each player shall find the highest rank card (Aces are high) in each suit
and place it face up in front of them.

- if they have any remaining cards with ranks 8, 9, 10, or Jack, place those
forward face up in a seperate pile

- Determine who has the highest Spade, they are now called ``The Spade``.

- Of the remaning unnamed players, determine who has the highest Heart,
they are now called ``The Heart``.

- Repeat to determine who is ``The Diamond`` and who is ``The Club``.

- Return all cards to a central discard pile except for those with rank 8, 9, 10, or Jack.

- ``The Spade`` shall recieve   ``JS``, ``TH``, ``9D``, and ``8C``.
- ``The Heart`` shall recieve   ``JH``, ``TD``, ``9C``, and ``8S``.
- ``The Diamond`` shall recieve ``JD``, ``TC``, ``9S``, and ``8H``.
- ``The Club`` shall recieve    ``JC``, ``TS``, ``9H``, and ``8D``.

- Shuffle the discard pile and re-deal it evenly to the remaining players.

## Policy Selection

The cards in your hand can be placed into one of four places:
1. Your [Domestic Policy](#domestic-policy)
2. Your [Foreign Policy](#foreign-policy)
3. Your [Event Deck](#event-play)
the event pile
4. The central discard pile

### Domestic Policy

There are four card slots in front of you that form your domestic policy—
one for each suit. When you place high value cards in your domestic policy slots,
that suit becomes endowed with [Special Abilities](#special-abilities) during
Event Play. Once a card is placed in its respective suit slot, it let's
your Suit Progress: the highest card you've placed in that slot throughtout the
game. all players start with a Suit Progress of ``Jack`` in every suit. You may
not place a card in your domestic policy that is higher than your Suit Progress
for that suit unless you've earned enough Suit Points during the previous [Event Play](#event-play)
round.

### Foreign Policy

There are two card slots, to be placed right and left of your domestic policy cards with
their tips turned inwards. These will be matched up with your adjacent opponents
and their combination will determine effects directly between you and your
neighbors like [Allyship](#allies-and-enemies) and [Declarations of War](#declaration-of-war).

### Event Deck

You may select a number of card to set aside in your Event Deck up to the year
number being played. The rest of your cards shall be discarded

## Trade

While choosing policies you are free to engage in Trade. You can trade with
neighbors by exchanging a diamond for another card. It is up to you both
to agree if the trade is worth it. You need not be truthful about what you are trading.

## Event Play

First, each neighboring player may inspect your foreign policy card, and you theirs.

Starting with ``The Spade`` and moving clockwise, each player will play a card
from their hand to the center. Each new card must be placed adjacent to one of
the cards previously played. Each time a card of the same rank is placed adjacent to another,
a [Major Event](#major-events) occurs instantly. 

After all the cards are played, check for [explosions](#dropping-the-bomb).

Then, do [Economic Resolution](#economic-resolution).

### Major Events

The player who first played their card during event play is the ``Receiver`` and the player
who places a card of the same rank adjacent to the ``Receiver``'s card is the ``Instigator``.
A Major event ensures based on &rarr


| Combo                | Event                                            | Receiver Gets | Instigator Gets | Condition               |
| :---:                | :---:                                            | :---:         | :---:           |                         |
| S &rarr H            | Declaration of War                               | -H +S         | +S -D           | once per opponent       |
| S &rarr D            | Embargo                                          | -D -H         |                 |                         |
| S &rarr C            | Regime Change                                    | -C            |                 |                         |
| H &rarr S            | Abolitionist Movement (prevent nuclear progress) | -S            |                 |                         |
| H &rarr D            | Tried at the Hague (Global sanctions)            | -D            |                 |                         |
| H &rarr C            | Election Year                                    | +/-C          | +/-C            | + if H > J, - if H <= J |
| D &rarr S            | War Monger                                       | +D +S         | +S              |                         |
| D &rarr H (at War)   | Annexation                                       | +D            | -H              | if 1 & 2 at War         |
| D &rarr H (at Peace) | Immigration                                      | +D            | +C              | if 1 & 2 at Peace       |
| D &rarr C            | Corruption of public official (other)            | +D -H         |                 |                         |
| C &rarr S            | Spy Ring                                         | -C            | +C              |                         |
| C &rarr H            | PSYOP                                            | -H            | +C              |                         |
| C &rarr D            | Corruption of public official (self)             |               | +D -H           |                         |

Some events have additional effects:

* Abolitionist Movement: The ``Receiver`` cannot upgrade their Spade progress next round.
* Declaration of War: For the next 3 years, the ``Instigator`` and ``Receiver`` are at War. You cannot become allies.
* Regime Change: You cannot form allies next year.
* Election Year: The elections apply to everyone!
* Spy Ring: The instigator may inspect up to two of the ``Receiver``'s domestic policy.

### Special Abilities

Special abilities are unlocked only when you have a card Loaded into your domestic policy slot for that suit.
You may only have cards in this slot up to and including your [Suit Progess](#domestic-policy) for that suit.

``The Nuke``: You can [Drop the Bomb](#dropping-the-bomb) during event play with any face card lower than your
Loaded Spade.

``Second Thoughts``: You can prevent any bomb from going off by have a heart which
is both lower or equal to your Loaded Heart Suit Progress and higher or equal to the rank
of the bomb.

``Buy Out``: In lieu of trade, you can force an adjacent opponent to give you any card at or below
your Diamond Suit Progress if they have it. Once per round.

``Friends Again?``: You can break a declaration of war if you both play a face club lower than
your loaded club.

### Dropping the Bomb

After Major Events and before Economic Resolution, Bombs will detonate.

Starting with the highest ranked nuke, determine if there are other spades.
follow the chain reaction.

nukes with 3, 2, 1 rings have an explosion patterns like:

Three ring explosion (K)
| | | | | |
|:---:|:---:|:---:|:---:|:---:|
| |x|x|x| |
|x|x|x|x|x|
|x|x|x|x|x|
|x|x|x|x|x|
| |x|x|x| |

Two ring explosion (Q)
| | | |
|:---:|:---:|:---:|
|x|x|x|
|x|x|x|
|x|x|x|

One ring explosion (J)
| | | |
|:---:|:---:|:---:|
| |x| |
|x|x|x|
| |x| |

### Complete and Total Destruction

Count the number of hearts captured by Bombs this round. Shuffle the discard pile
and draw the first card. If its rank is lower than the number of hearts captured time two,
then, the game *ends* in Complete and Total Destruction.

### Allies and Enemies

You and your neighbor are deemed Allies if you both put forward a club.
You can only become Allies with your direct neighbors. The ``Ally Strength``
score between you is the average rank (rounded up) of the clubs allocated to your
foreign policies.

Allies share the [Special Ability](#special-abilities) benefits of the max
level of each suit between them, up to and including the . Neighboring enemies must continuously supply
resources to their borders to resist an ongoing dispute. They are also automatically

Opponents at War cannot become allies.

## Victory Check

If someone has obtained a level 4 Suit Progress in one of C, H, D, then they win.

If someone has obtained a level 4 Suit Progress in Spades *AND* a level 3 Suit
Progress in C, H, or D, they win.

Tie break I, compare total Heart progress points)
Tie break II, compare total Diamond progress points)
Tie break III, compare total Club progress points)

If after 5 years, no one has won,
then determine the winner from the tie breakers above.

## General Rules

### Table Talk

Table talk is allowed! You can whisper to your adjacent neighbors,
but *NOT* to the opponent sitting opposite you. You may not arbitrarily
display your cards to opponents as a means to gain additional trust.
