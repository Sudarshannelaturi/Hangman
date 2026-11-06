"""Hangman game with a Tkinter GUI.

Run with:  python hangman.py
Uses only the Python standard library.
"""

import random
import tkinter as tk
from tkinter import font as tkfont

# --- Word bank: category -> list of (word, hint) ---
WORDS = {
    "Animals": [
        ("ELEPHANT", "Largest land mammal"),
        ("GIRAFFE", "Tallest animal on Earth"),
        ("KANGAROO", "Carries its baby in a pouch"),
        ("PENGUIN", "A bird that cannot fly but swims well"),
        ("CHEETAH", "Fastest land animal"),
        ("DOLPHIN", "Intelligent sea mammal"),
        ("OCTOPUS", "Has eight arms"),
        ("PORCUPINE", "Covered in sharp quills"),
        ("LION","Has got a Maine and is also known as King of Jungle")
    ],
    "Countries": [
        ("AUSTRALIA", "Home of the kangaroo"),
        ("INDIA", "Home of the Taj Mahal"),
        ("BRAZIL", "Largest country in South America"),
        ("CANADA", "Famous for maple syrup"),
        ("JAPAN", "Land of the rising sun"),
        ("EGYPT", "Home of the pyramids of Giza"),
        ("NORWAY", "Known for its fjords"),
        ("MEXICO", "Birthplace of tacos"),
    ],
    "Fruits": [
        ("BANANA", "Long, yellow and curved"),
        ("PINEAPPLE", "Spiky outside, sweet inside"),
        ("MANGO", "King of fruits"),
        ("STRAWBERRY", "Red with seeds on the outside"),
        ("WATERMELON", "Big, green outside and red inside"),
        ("POMEGRANATE", "Full of juicy red seeds"),
        ("BLUEBERRY", "Small, round and blue"),
        ("COCONUT", "Hard shell with water inside"),
    ],
    "Programming": [
        ("PYTHON", "Language named after a comedy group"),
        ("VARIABLE", "Stores a value"),
        ("FUNCTION", "Reusable block of code"),
        ("COMPILER", "Translates source code to machine code"),
        ("RECURSION", "A function that calls itself"),
        ("DATABASE", "Organised collection of data"),
        ("ALGORITHM", "Step-by-step procedure"),
        ("DEBUGGER", "Tool for finding bugs"),
    ],
}

MAX_WRONG = 6

# --- Colours ---
BG = "#1e1e2e"
PANEL = "#2a2a3d"
FG = "#e6e6f0"
MUTED = "#8a8aa3"
ACCENT = "#7aa2f7"
GOOD = "#9ece6a"
BAD = "#f7768e"
KEY_BG = "#3b3b55"
KEY_HOVER = "#4d4d70"


class HangmanApp:
    def __init__(self, root):
        self.root = root
        root.title("Hangman")
        root.configure(bg=BG)
        root.minsize(760, 620)

        self.title_font = tkfont.Font(family="Segoe UI", size=26, weight="bold")
        self.word_font = tkfont.Font(family="Consolas", size=32, weight="bold")
        self.text_font = tkfont.Font(family="Segoe UI", size=12)
        self.key_font = tkfont.Font(family="Segoe UI", size=13, weight="bold")

        self.wins = 0
        self.losses = 0
        self.streak = 0
        self.category = tk.StringVar(value="Random")

        self._build_ui()
        root.bind("<Key>", self._on_keypress)
        self.new_game()

    # ---------- UI construction ----------
    def _build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=20, pady=(16, 6))

        tk.Label(header, text="HANGMAN", font=self.title_font,
                 bg=BG, fg=ACCENT).pack(side="left")

        self.score_label = tk.Label(header, font=self.text_font, bg=BG, fg=FG)
        self.score_label.pack(side="right")

        controls = tk.Frame(self.root, bg=BG)
        controls.pack(fill="x", padx=20, pady=4)

        tk.Label(controls, text="Category:", font=self.text_font,
                 bg=BG, fg=MUTED).pack(side="left")
        menu = tk.OptionMenu(controls, self.category,
                             "Random", *WORDS.keys(),
                             command=lambda _: self.new_game())
        menu.config(font=self.text_font, bg=KEY_BG, fg=FG, activebackground=KEY_HOVER,
                    activeforeground=FG, highlightthickness=0, relief="flat", bd=0)
        menu["menu"].config(font=self.text_font, bg=PANEL, fg=FG,
                            activebackground=ACCENT, activeforeground=BG)
        menu.pack(side="left", padx=8)

        self._button(controls, "New Game", self.new_game).pack(side="right")
        self.hint_btn = self._button(controls, "Hint (-1 life)", self.use_hint)
        self.hint_btn.pack(side="right", padx=8)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(body, width=300, height=320, bg=PANEL,
                                highlightthickness=0)
        self.canvas.pack(side="left", padx=(0, 20))

        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        self.category_label = tk.Label(right, font=self.text_font, bg=BG, fg=MUTED)
        self.category_label.pack(anchor="w")

        self.word_label = tk.Label(right, font=self.word_font, bg=BG, fg=FG)
        self.word_label.pack(anchor="w", pady=(20, 10))

        self.hint_label = tk.Label(right, font=self.text_font, bg=BG, fg=ACCENT,
                                   wraplength=380, justify="left")
        self.hint_label.pack(anchor="w")

        self.lives_label = tk.Label(right, font=self.text_font, bg=BG, fg=FG)
        self.lives_label.pack(anchor="w", pady=(20, 0))

        self.status_label = tk.Label(right, font=self.title_font, bg=BG, fg=FG)
        self.status_label.pack(anchor="w", pady=(10, 0))

        # On-screen keyboard
        kb = tk.Frame(self.root, bg=BG)
        kb.pack(pady=(4, 18))
        self.key_buttons = {}
        for row in ("QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"):
            row_frame = tk.Frame(kb, bg=BG)
            row_frame.pack(pady=3)
            for letter in row:
                b = tk.Button(row_frame, text=letter, width=3, font=self.key_font,
                              bg=KEY_BG, fg=FG, activebackground=KEY_HOVER,
                              activeforeground=FG, relief="flat", bd=0, cursor="hand2",
                              disabledforeground=MUTED,
                              command=lambda l=letter: self.guess(l))
                b.pack(side="left", padx=3, ipady=6)
                b.bind("<Enter>", lambda e, b=b: b["state"] == "normal" and b.config(bg=KEY_HOVER))
                b.bind("<Leave>", lambda e, b=b: b["state"] == "normal" and b.config(bg=KEY_BG))
                self.key_buttons[letter] = b

        tk.Label(self.root, text="Type letters on your keyboard or click them.  "
                                 "Enter = new game", font=self.text_font,
                 bg=BG, fg=MUTED).pack(pady=(0, 10))

    def _button(self, parent, text, command):
        return tk.Button(parent, text=text, command=command, font=self.text_font,
                         bg=ACCENT, fg=BG, activebackground=FG, activeforeground=BG,
                         relief="flat", bd=0, padx=14, pady=4, cursor="hand2")

    # ---------- Game logic ----------
    def new_game(self):
        cat = self.category.get()
        if cat == "Random":
            cat = random.choice(list(WORDS))
        self.current_category = cat
        self.word, self.hint = random.choice(WORDS[cat])
        self.guessed = set()
        self.wrong = 0
        self.game_over = False
        self.hint_used = False

        for b in self.key_buttons.values():
            b.config(state="normal", bg=KEY_BG, fg=FG)
        self.hint_btn.config(state="normal")
        self.category_label.config(text=f"Category: {cat}")
        self.hint_label.config(text="")
        self.status_label.config(text="")
        self._refresh()

    def guess(self, letter):
        if self.game_over or letter in self.guessed:
            return
        self.guessed.add(letter)
        btn = self.key_buttons[letter]
        if letter in self.word:
            btn.config(state="disabled", bg=GOOD, disabledforeground=BG)
        else:
            self.wrong += 1
            btn.config(state="disabled", bg=BAD, disabledforeground=BG)
        self._refresh()
        self._check_end()

    def use_hint(self):
        if self.game_over or self.hint_used:
            return
        if self.wrong >= MAX_WRONG - 1:
            self.hint_label.config(text="Not enough lives left for a hint!")
            return
        self.hint_used = True
        self.wrong += 1
        self.hint_btn.config(state="disabled")
        self.hint_label.config(text=f"Hint: {self.hint}")
        self._refresh()

    def _check_end(self):
        if all(c in self.guessed for c in self.word):
            self.game_over = True
            self.wins += 1
            self.streak += 1
            self.status_label.config(text="You win! 🎉", fg=GOOD)
        elif self.wrong >= MAX_WRONG:
            self.game_over = True
            self.losses += 1
            self.streak = 0
            self.status_label.config(text="Game over!", fg=BAD)
            self.word_label.config(text=" ".join(self.word), fg=BAD)
        else:
            return
        for b in self.key_buttons.values():
            b.config(state="disabled")
        self.hint_btn.config(state="disabled")
        self._update_score()

    def _on_keypress(self, event):
        if event.keysym == "Return":
            self.new_game()
            return
        ch = event.char.upper()
        if len(ch) == 1 and ch.isalpha() and ch in self.key_buttons:
            self.guess(ch)

    # ---------- Rendering ----------
    def _refresh(self):
        display = " ".join(c if c in self.guessed else "_" for c in self.word)
        self.word_label.config(text=display, fg=FG)
        lives = MAX_WRONG - self.wrong
        self.lives_label.config(text="Lives: " + "❤ " * lives + "♡ " * self.wrong)
        self._update_score()
        self._draw_hangman()

    def _update_score(self):
        self.score_label.config(
            text=f"Wins: {self.wins}   Losses: {self.losses}   Streak: {self.streak}")

    def _draw_hangman(self):
        c = self.canvas
        c.delete("all")
        line = dict(fill=FG, width=5, capstyle="round")

        # Gallows (always shown)
        c.create_line(40, 290, 200, 290, **line)   # base
        c.create_line(80, 290, 80, 30, **line)     # pole
        c.create_line(80, 30, 200, 30, **line)     # beam
        c.create_line(80, 70, 120, 30, **line)     # brace
        c.create_line(200, 30, 200, 70, fill=MUTED, width=3)  # rope

        body = dict(fill=BAD if self.wrong >= MAX_WRONG else ACCENT, width=5,
                    capstyle="round")
        parts = [
            lambda: c.create_oval(175, 70, 225, 120, outline=body["fill"], width=5),  # head
            lambda: c.create_line(200, 120, 200, 200, **body),  # torso
            lambda: c.create_line(200, 140, 165, 175, **body),  # left arm
            lambda: c.create_line(200, 140, 235, 175, **body),  # right arm
            lambda: c.create_line(200, 200, 170, 250, **body),  # left leg
            lambda: c.create_line(200, 200, 230, 250, **body),  # right leg
        ]
        for draw in parts[:self.wrong]:
            draw()

        if self.wrong >= MAX_WRONG:
            # X eyes
            for x in (188, 212):
                c.create_line(x - 5, 88, x + 5, 98, fill=BAD, width=2)
                c.create_line(x - 5, 98, x + 5, 88, fill=BAD, width=2)


if __name__ == "__main__":
    root = tk.Tk()
    HangmanApp(root)
    root.mainloop()
