# 🃏 Poker Game (Kivy)

A desktop poker game built with Kivy that features animated card dealing, chip betting, hand evaluation, and automatic winner determination.

The game simulates a classic five-card poker showdown between the player and a dealer, including betting mechanics, card animations, chip stacks, and bankroll management.

---

# ✨ Features

* 🃏 Five-card poker gameplay
* 🎲 Randomized deck generation and shuffling
* 💰 Betting system with player and dealer balances
* 🪙 Animated chip stacks
* 🎴 Animated card dealing and card flipping
* 🏆 Automatic hand evaluation
* 🤖 Dealer opponent
* 🔄 Multiple rounds support
* 🎨 Custom card and chip graphics
* ♻️ Automatic game reset when a player runs out of chips

---

# 🛠 Built With

* Python 3.10+
* Kivy

---

# 📦 Installation

## Clone the Repository

```bash
git clone https://github.com/yourusername/kivy-poker-game.git

cd kivy-poker-game
```

## Create a Virtual Environment

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

## Install Dependencies

```bash
pip install kivy
```

---

# 📂 Project Structure

```text
project/
│
├── main.py
│
├── cards/
│   ├── back.png
│   ├── A_spades.png
│   ├── K_hearts.png
│   └── ...
│
├── chips/
│   └── chip.png
│
└── README.md
```

---

# ▶️ Running the Game

```bash
python main.py
```

The game window will open automatically.

---

# 🎮 Gameplay

## Place a Bet

Enter your desired bet amount and click:

```text
Bet
```

The bet amount is deducted from both player and dealer balances and added to the pot.

---

## Deal Cards

Click:

```text
Deal
```

Both players receive five cards.

* Player cards are shown face-up.
* Dealer cards remain hidden.

---

## Reveal Cards

Click:

```text
Open
```

Dealer cards are revealed and the game automatically determines the winner.

---

## Fold

Click:

```text
Fold
```

The dealer instantly wins the round and receives the pot.

---

## Next Round

Click:

```text
Next Round
```

The table is cleared and a new round can begin.

---

# 🏆 Supported Poker Hands

The game evaluates the following hands:

| Rank | Hand            |
| ---- | --------------- |
| 1    | High Card       |
| 2    | One Pair        |
| 3    | Two Pair        |
| 4    | Three of a Kind |
| 5    | Straight        |
| 6    | Flush           |
| 7    | Full House      |
| 8    | Four of a Kind  |
| 9    | Straight Flush  |
| 10   | Royal Flush     |

---

# 💰 Banking System

Initial balances:

```text
Player: 1000
Dealer: 1000
```

The pot contains both players' bets.

Winner receives the entire pot.

In case of a tie:

```text
Pot is split equally.
```

---

# 🎨 Assets Required

The game expects the following resources:

## Cards

Located in:

```text
cards/
```

Required:

```text
back.png

2_hearts.png
2_diamonds.png
...
A_spades.png
```

One image for every card in the deck.

---

## Chips

Located in:

```text
chips/
```

Required:

```text
chip.png
```

Used for pot visualization and chip animations.

---

# 🔄 Automatic Restart

The game automatically resets when:

```text
Player balance = 0
or
Dealer balance = 0
```

Both balances are restored to:

```text
1000 chips
```

and a new deck is generated.

---

# 🎴 Card Animations

The game includes:

* Animated card dealing
* Smooth card movement from the deck
* Card flip animations
* Animated chip stacking

---

# 📄 License

MIT License

---

# 👨‍💻 Author

Poker Game built with Kivy.

A simple poker simulation demonstrating Kivy animations, game logic, and interactive UI development.
