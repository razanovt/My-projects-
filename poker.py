from kivy.app import App
from kivy.properties import BooleanProperty, NumericProperty
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
import random

CARD_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 11, 'Q': 12, 'K': 13, 'A': 14
}

CHIP_VALUE = 100


class Card(Image):
    face_up = BooleanProperty(False)
    card = ''

    def __init__(self, card, face_up=False, **kwargs):
        super().__init__(**kwargs)
        self.card = card
        self.face_up = face_up
        self.update_texture()

    def update_texture(self):
        self.source = f'cards/{self.card}.png' if self.face_up else 'cards/back.png'

    def flip_up(self):
        if self.face_up:
            return
        anim = Animation(opacity=0, duration=0.15)
        anim.bind(on_complete=lambda *_: self._show())
        anim += Animation(opacity=1, duration=0.15)
        anim.start(self)

    def _show(self):
        self.face_up = True
        self.update_texture()


class PokerTable(FloatLayout):
    player_balance = NumericProperty(1000)
    dealer_balance = NumericProperty(1000)
    bank = NumericProperty(0)
    round_active = False
    cards_dealt = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.deck = []
        self.player_hand = []
        self.dealer_hand = []
        self.player_cards = []
        self.dealer_cards = []
        self.chips = []

        self.init_ui()
        self.init_deck()
        self.update_labels()

    # ---------------- UI ----------------
    def init_ui(self):
        with self.canvas.before:
            Color(0, 0.4, 0, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._resize, pos=self._resize)

        # Карты
        self.card_area = FloatLayout(size_hint=(1, .7), pos_hint={'y': .3})
        self.add_widget(self.card_area)

        # Колода
        self.deck_img = Image(source='cards/back.png', size=(100, 150),
                              size_hint=(None, None), pos_hint={'x': 0.03, 'center_y': .5})
        self.add_widget(self.deck_img)

        # Балансы
        self.lbl_player = Label(size=(300, 40), size_hint=(None, None),
                                pos_hint={'x': 0.01, 'top': 0.99}, font_size=16)
        self.lbl_dealer = Label(size=(300, 40), size_hint=(None, None),
                                pos_hint={'right': 0.99, 'top': 0.99}, font_size=16)
        self.add_widget(self.lbl_player)
        self.add_widget(self.lbl_dealer)

        # Банк
        self.msg = Label(size_hint=(1, .05), pos_hint={'top': .88}, font_size=18)
        self.add_widget(self.msg)

        # Результат
        self.result_label = Label(size_hint=(1, .05), pos_hint={'top': .83},
                                  font_size=16, color=(1, 1, 0, 1))
        self.add_widget(self.result_label)

        # Зона фишек
        self.chip_area = FloatLayout(size_hint=(0.25, 0.6), pos_hint={'right': 0.98, 'center_y': 0.45})
        self.add_widget(self.chip_area)

        # Ставка
        self.bet_input = TextInput(text='100', size=(100, 30), size_hint=(None, None),
                                   pos_hint={'center_x': .5, 'y': .12})
        self.add_widget(self.bet_input)

        # Кнопки
        self.btn_bet = Button(text='Ставка')
        self.btn_deal = Button(text='Раздать', disabled=True)
        self.btn_open = Button(text='Открыть', disabled=True)
        self.btn_fold = Button(text='Пас', disabled=True)
        self.btn_next = Button(text='Следующая', disabled=True)

        box = BoxLayout(size_hint=(.7, .08), pos_hint={'center_x': .5, 'y': .03}, spacing=10)
        for b in (self.btn_bet, self.btn_deal, self.btn_open, self.btn_fold, self.btn_next):
            box.add_widget(b)
        self.add_widget(box)

        self.btn_bet.bind(on_press=self.make_bet)
        self.btn_deal.bind(on_press=self.deal)
        self.btn_open.bind(on_press=self.open_cards)
        self.btn_fold.bind(on_press=self.fold)
        self.btn_next.bind(on_press=self.next_round)

    def _resize(self, *_):
        self.bg.size = self.size
        self.bg.pos = self.pos

    # ---------------- DECK ----------------
    def init_deck(self):
        suits = ['чирв', 'бубен', 'пик', 'треф']
        self.deck = [f'{v}_{s}' for v in CARD_VALUES.keys() for s in suits]
        random.shuffle(self.deck)

    # ---------------- LABELS ----------------
    def update_labels(self):
        self.lbl_player.text = f'Игрок: {self.player_balance}'
        self.lbl_dealer.text = f'Дилер: {self.dealer_balance}'
        self.msg.text = f'Банк: {self.bank}' if self.bank else 'Введите ставку'

    # ---------------- BET ----------------
    def make_bet(self, *_):
        if self.round_active:
            return
        try:
            bet = int(self.bet_input.text)
            if bet <= 0 or bet > self.player_balance or bet > self.dealer_balance:
                return
        except ValueError:
            return

        self.player_balance -= bet
        self.dealer_balance -= bet
        self.bank = bet * 2
        self.round_active = True
        self.result_label.text = ""
        self.btn_deal.disabled = False
        self.show_chips(self.bank)
        self.update_labels()

    # ---------------- CHIPS ----------------
    def show_chips(self, amount):
        self.clear_chips()
        chip_count = max(1, amount // CHIP_VALUE)
        chips_per_stack = 5

        for i in range(chip_count):
            stack = i // chips_per_stack
            height = i % chips_per_stack
            chip = Image(source='chips/chip.png', size=(40, 40), size_hint=(None, None),
                         pos=(self.width, self.height / 2))
            self.chip_area.add_widget(chip)
            x = stack * 45
            y = height * 12
            Animation(x=x, y=y, duration=0.4, t='out_back').start(chip)
            self.chips.append(chip)

    def clear_chips(self):
        for c in self.chips:
            if c.parent:
                c.parent.remove_widget(c)
        self.chips.clear()

    # ---------------- DEAL ----------------
    def deal(self, *_):
        self.clear_cards()
        if len(self.deck) < 10:
            self.init_deck()
        self.player_hand = [self.deck.pop() for _ in range(5)]
        self.dealer_hand = [self.deck.pop() for _ in range(5)]

        for i in range(5):
            Clock.schedule_once(lambda _, x=i: self.spawn_card(self.dealer_hand[x], x, False), i * .25)
            Clock.schedule_once(lambda _, x=i: self.spawn_card(self.player_hand[x], x, True), (i + 5) * .25)

        self.cards_dealt = True
        self.btn_open.disabled = False
        self.btn_fold.disabled = False
        self.btn_deal.disabled = True

    def spawn_card(self, card, idx, player):
        c = Card(card, face_up=player, size=(100, 150), size_hint=(None, None), pos=self.deck_img.pos)
        self.card_area.add_widget(c)
        y = 220 if player else self.card_area.height - 260
        Animation(x=self.card_area.width / 2 - 250 + idx * 110, y=y, duration=.4).start(c)
        (self.player_cards if player else self.dealer_cards).append(c)

    # ---------------- OPEN / RESULT ----------------
    def open_cards(self, *_):
        for c in self.dealer_cards:
            c.flip_up()
        Clock.schedule_once(lambda *_: self.resolve(), 1)

    def evaluate_hand(self, hand):
        values = [c.split('_')[0] for c in hand]
        suits = [c.split('_')[1] for c in hand]
        sv = sorted([CARD_VALUES[v] for v in values])

        if len(set(suits)) == 1 and sv == [10, 11, 12, 13, 14]:
            return "Роял-флеш"
        if len(set(suits)) == 1 and all(sv[i]+1 == sv[i+1] for i in range(4)):
            return "Стрит-флеш"
        if any(values.count(v) == 4 for v in values):
            return "Каре"
        if any(values.count(v) == 3 for v in values) and any(values.count(v) == 2 for v in values):
            return "Фул-хаус"
        if len(set(suits)) == 1:
            return "Флеш"
        if all(sv[i]+1 == sv[i+1] for i in range(4)):
            return "Стрит"
        if any(values.count(v) == 3 for v in values):
            return "Тройка"
        if len([v for v in set(values) if values.count(v) == 2]) == 2:
            return "Две пары"
        if any(values.count(v) == 2 for v in values):
            return "Пара"
        return "Старшая карта"

    def resolve(self):
        p = self.evaluate_hand(self.player_hand)
        d = self.evaluate_hand(self.dealer_hand)
        order = ["Старшая карта", "Пара", "Две пары", "Тройка", "Стрит",
                 "Флеш", "Фул-хаус", "Каре", "Стрит-флеш", "Роял-флеш"]

        if order.index(p) > order.index(d):
            self.player_balance += self.bank
            self.result_label.text = f"Победил игрок — {p}"
        elif order.index(p) < order.index(d):
            self.dealer_balance += self.bank
            self.result_label.text = f"Победил дилер — {d}"
        else:
            self.player_balance += self.bank // 2
            self.dealer_balance += self.bank // 2
            self.result_label.text = f"Ничья — {p}"

        self.bank = 0
        self.end_round()

    def fold(self, *_):
        self.dealer_balance += self.bank
        self.result_label.text = "Игрок спасовал — победил дилер"
        self.bank = 0
        self.end_round()

    # ---------------- END ROUND / RESTART ----------------
    def end_round(self):
        self.round_active = False
        self.cards_dealt = False
        self.btn_open.disabled = True
        self.btn_fold.disabled = True
        self.btn_next.disabled = False
        self.clear_chips()
        self.update_labels()
        self.check_restart()

    def check_restart(self):
        if self.player_balance == 0 or self.dealer_balance == 0:
            Clock.schedule_once(lambda *_: self.reset_game(), 1.5)

    def reset_game(self):
        self.player_balance = 1000
        self.dealer_balance = 1000
        self.bank = 0
        self.result_label.text = "Игра начата заново"
        self.clear_cards()
        self.clear_chips()
        self.init_deck()
        self.update_labels()

    def next_round(self, *_):
        self.clear_cards()
        self.btn_next.disabled = True
        self.update_labels()

    def clear_cards(self):
        for c in self.player_cards + self.dealer_cards:
            if c.parent:
                c.parent.remove_widget(c)
        self.player_cards.clear()
        self.dealer_cards.clear()


class PokerApp(App):
    def build(self):
        return PokerTable()


if __name__ == '__main__':
    PokerApp().run()
