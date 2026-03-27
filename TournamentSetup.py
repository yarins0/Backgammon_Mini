import os
import glob
from tkinter import *
from Constants import (
    RAND_AI, HEUR_AI, MIN_MAX_AI, MCTS_AI, NEURAL_AI, HUMAN,
    EVAL_DISTRIBUTION, MIN_MAX_DEPTH, MCTS_C,
)

# The six heuristic weight keys, in display order
RATIO_KEYS = [
    "prime_structure",
    "anchors",
    "blots",
    "race_advantage",
    "home_board_strength",
    "captured_pieces",
]

PLAYER_TYPE_LABELS = ["Neural AI", "MCTS AI", "MinMax AI", "Heuristic AI", "Random AI", "Human"]


def player_spec_label(spec):
    """Return a human-readable name for a player spec in parse_player() format."""
    if spec == HUMAN:
        return "Human"
    if spec == RAND_AI:
        return "Random AI"
    if spec == HEUR_AI:
        return "Heuristic AI"
    if spec == MIN_MAX_AI:
        return "MinMax AI"
    if spec == MCTS_AI:
        return "MCTS AI"
    if spec == NEURAL_AI:
        return "Neural AI"
    if isinstance(spec, list):
        type_const = spec[0]
        if type_const == HEUR_AI:
            return "Heuristic AI"
        if type_const == MIN_MAX_AI:
            return f"MinMax AI (depth={spec[2]})"
        if type_const == MCTS_AI:
            return f"MCTS AI (c={spec[2]:.2f})"
        if type_const == NEURAL_AI:
            return f"Neural AI ({os.path.basename(spec[1])})"
    return str(spec)


def _round_robin_game_count(n):
    """Number of games in a round-robin tournament with n players."""
    return n * (n - 1) // 2


class TournamentSetupWindow:
    """
    A setup screen rendered inside the main Tk window.
    Lets the user assemble a list of players and their configurations,
    then calls on_start(players) with a list in the parse_player() format.
    """

    def __init__(self, window, on_start):
        self.window = window
        self.on_start = on_start
        self.players = []        # player specs in parse_player() format
        self.player_labels = []  # display names shown in the roster
        self._param_widgets = []

        self._build_ui()

    # ------------------------------------------------------------------ layout

    def _build_ui(self):
        self.window.title("Backgammon — Tournament Setup")

        self.frame = Frame(self.window, padx=20, pady=20)
        self.frame.pack(fill=BOTH, expand=True)

        Label(self.frame, text="Tournament Setup", font=("Helvetica", 18, "bold")).pack(pady=(0, 15))

        panels = Frame(self.frame)
        panels.pack(fill=BOTH, expand=True)

        self._build_left_panel(panels)
        self._build_right_panel(panels)

    def _build_left_panel(self, parent):
        left = LabelFrame(parent, text="Configure Player", padx=10, pady=10)
        left.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

        self._build_type_selector(left)

        # Dynamic parameter section — rebuilt each time the type changes
        self.param_frame = Frame(left)
        self.param_frame.pack(fill=X, pady=(0, 8))

        self._add_btn = Button(left, text="Add Player", command=self._add_player)
        self._add_btn.pack(pady=(4, 0))

        # Populate params for the initially selected type
        self._on_type_changed(PLAYER_TYPE_LABELS[0])

    def _build_type_selector(self, parent):
        row = Frame(parent)
        row.pack(fill=X, pady=(0, 8))
        Label(row, text="Type:", width=8, anchor=W).pack(side=LEFT)

        self.type_var = StringVar(value=PLAYER_TYPE_LABELS[0])
        OptionMenu(row, self.type_var, *PLAYER_TYPE_LABELS,
                   command=self._on_type_changed).pack(side=LEFT)

    def _build_right_panel(self, parent):
        right = LabelFrame(parent, text="Players", padx=10, pady=10, width=240)
        right.pack(side=LEFT, fill=BOTH, expand=True)
        right.pack_propagate(False)

        # Game count hint — updated in _refresh_roster
        self.game_count_label = Label(right, text="", fg="grey", font=("Helvetica", 9))
        self.game_count_label.pack(anchor=W, pady=(0, 4))

        self.roster_frame = Frame(right)
        self.roster_frame.pack(fill=BOTH, expand=True)

        Label(self.roster_frame, text="No players added yet.", fg="grey").pack()

        self.start_btn = Button(
            right, text="Start Tournament",
            command=self._start_tournament, state=DISABLED,
        )
        self.start_btn.pack(pady=(10, 0))

    # -------------------------------------------------------- dynamic params

    def _on_type_changed(self, selected):
        for widget in self._param_widgets:
            widget.destroy()
        self._param_widgets = []
        # Re-enable by default; _build_model_selector disables it when no models exist
        self._add_btn.config(state=NORMAL)

        if selected in ("Heuristic AI", "MinMax AI", "MCTS AI"):
            self._build_ratio_sliders()
        if selected == "MinMax AI":
            self._build_depth_spinbox()
        if selected == "MCTS AI":
            self._build_c_entry()
        if selected == "Neural AI":
            self._build_model_selector()

    def _build_ratio_sliders(self):
        """Six labelled sliders (0.0–1.0) for the heuristic weight keys.
        Values are normalized to sum to 1 when collected; the indicator below
        shows the raw sum so the user can see how weights relate to each other.
        """
        self.ratio_vars = {}
        for key in RATIO_KEYS:
            row = Frame(self.param_frame)
            row.pack(fill=X, pady=1)
            self._param_widgets.append(row)

            Label(row, text=key.replace("_", " ").title(), width=22, anchor=W).pack(side=LEFT)

            default = EVAL_DISTRIBUTION.get(key, 0.0)
            val_var = DoubleVar(value=default)
            self.ratio_vars[key] = val_var

            val_label = Label(row, text=f"{default:.2f}", width=4)
            val_label.pack(side=RIGHT)

            def on_slider_move(v, lbl=val_label):
                lbl.config(text=f"{float(v):.2f}")
                self._update_ratio_sum()

            Scale(
                row, variable=val_var, from_=0.0, to=1.0, resolution=0.01,
                orient=HORIZONTAL, length=130, showvalue=False,
                command=on_slider_move,
            ).pack(side=RIGHT)

        # Sum indicator — updated by _update_ratio_sum on every slider move
        sum_row = Frame(self.param_frame)
        sum_row.pack(fill=X, pady=(2, 0))
        self._param_widgets.append(sum_row)
        self._ratio_sum_label = Label(sum_row, text="", font=("Helvetica", 8), anchor=E)
        self._ratio_sum_label.pack(fill=X)
        self._update_ratio_sum()

    def _build_depth_spinbox(self):
        """Depth selector for MinMax (1–5)."""
        row = Frame(self.param_frame)
        row.pack(fill=X, pady=(6, 2))
        self._param_widgets.append(row)

        Label(row, text="Search Depth:", width=22, anchor=W).pack(side=LEFT)
        self.depth_var = IntVar(value=MIN_MAX_DEPTH)
        Spinbox(row, from_=1, to=5, textvariable=self.depth_var, width=5).pack(side=LEFT)

    def _build_c_entry(self):
        """Exploration constant (c) entry for MCTS."""
        row = Frame(self.param_frame)
        row.pack(fill=X, pady=(6, 2))
        self._param_widgets.append(row)

        Label(row, text="Exploration (c):", width=22, anchor=W).pack(side=LEFT)
        # StringVar rather than DoubleVar: DoubleVar raises TclError silently
        # on non-numeric keystrokes, leaving the variable in an undefined state.
        # Parsing is done explicitly in _build_player_spec instead.
        self.c_var = StringVar(value=str(MCTS_C))
        Entry(row, textvariable=self.c_var, width=8).pack(side=LEFT)

    def _build_model_selector(self):
        """Dropdown populated with .pth files found in HeuristicNets/."""
        row = Frame(self.param_frame)
        row.pack(fill=X, pady=2)
        self._param_widgets.append(row)

        Label(row, text="Model:", width=8, anchor=W).pack(side=LEFT)

        models = self._find_model_files()
        self.model_var = StringVar()

        if models:
            self.model_var.set(models[0])
            OptionMenu(row, self.model_var, *models,
                       command=lambda _: None).pack(side=LEFT)
        else:
            self.model_var.set("")
            Label(row, text="No .pth files found in HeuristicNets/", fg="red").pack(side=LEFT)
            self._add_btn.config(state=DISABLED)

    def _find_model_files(self):
        """Return absolute paths to .pth files in HeuristicNets/.
        Absolute paths ensure Neural_Player can open them regardless of CWD.
        """
        base = os.path.dirname(os.path.abspath(__file__))
        pattern = os.path.join(base, "HeuristicNets", "*.pth")
        return [os.path.abspath(p) for p in sorted(glob.glob(pattern))]

    # --------------------------------------------------------- roster logic

    def _update_ratio_sum(self):
        """Refresh the sum indicator label below the ratio sliders."""
        total = sum(self.ratio_vars[key].get() for key in RATIO_KEYS)
        if abs(total - 1.0) < 1e-6:
            text, color = f"Sum: {total:.2f}", "#2a7a2a"
        elif total == 0:
            text, color = "Sum: 0.00 — all zero, equal weights will be used", "orange"
        else:
            text, color = f"Sum: {total:.2f} — will be normalized to 1.00", "#888"
        self._ratio_sum_label.config(text=text, fg=color)

    def _collect_ratios(self):
        """Return normalized ratios that sum to exactly 1.0.
        If all sliders are at zero, falls back to equal weights.
        """
        raw = {key: self.ratio_vars[key].get() for key in RATIO_KEYS}
        total = sum(raw.values())
        if total == 0:
            equal = 1.0 / len(RATIO_KEYS)
            return {key: round(equal, 4) for key in RATIO_KEYS}
        return {key: round(v / total, 4) for key, v in raw.items()}

    def _add_player(self):
        selected = self.type_var.get()
        spec, label = self._build_player_spec(selected)
        if spec is None:
            return
        self.players.append(spec)
        self.player_labels.append(label)
        self._refresh_roster()

    def _build_player_spec(self, selected):
        """Return (spec, label) for the current configuration, or (None, None) on error."""
        if selected == "Human":
            return HUMAN, "Human"

        if selected == "Random AI":
            return RAND_AI, "Random AI"

        if selected == "Heuristic AI":
            ratios = self._collect_ratios()
            return [HEUR_AI, ratios], "Heuristic AI"

        if selected == "MinMax AI":
            ratios = self._collect_ratios()
            depth = self.depth_var.get()
            return [MIN_MAX_AI, ratios, depth], f"MinMax AI (depth={depth})"

        if selected == "MCTS AI":
            ratios = self._collect_ratios()
            try:
                c = float(self.c_var.get())
                if c <= 0:
                    raise ValueError
            except ValueError:
                c = MCTS_C
            return [MCTS_AI, ratios, c], f"MCTS AI (c={c:.2f})"

        if selected == "Neural AI":
            model_path = self.model_var.get()
            if not model_path:
                return None, None
            return [NEURAL_AI, model_path], f"Neural AI ({os.path.basename(model_path)})"

        return None, None

    def _remove_player(self, idx):
        self.players.pop(idx)
        self.player_labels.pop(idx)
        self._refresh_roster()

    def _refresh_roster(self):
        for widget in self.roster_frame.winfo_children():
            widget.destroy()

        n = len(self.players)

        if n == 0:
            Label(self.roster_frame, text="No players added yet.", fg="grey").pack()
            self.game_count_label.config(text="")
            self.start_btn.config(state=DISABLED)
            return

        games = _round_robin_game_count(n)
        game_word = "game" if games == 1 else "games"
        self.game_count_label.config(text=f"{n} player{'s' if n != 1 else ''} → {games} {game_word}")

        for i, label in enumerate(self.player_labels):
            row = Frame(self.roster_frame)
            row.pack(fill=X, pady=2)
            Label(row, text=f"{i + 1}. {label}", anchor=W).pack(side=LEFT, fill=X, expand=True)
            # i=i captures loop variable by value at definition time
            Button(row, text="Remove", command=lambda i=i: self._remove_player(i)).pack(side=RIGHT)

        self.start_btn.config(state=NORMAL if n >= 2 else DISABLED)

    # --------------------------------------------------------------- start

    def _start_tournament(self):
        if len(self.players) >= 2:
            self.on_start(self.players)

    def destroy(self):
        self.frame.destroy()


class TournamentResultsScreen:
    """
    Results screen shown after all tournament games complete.
    Displays a ranked table of players and scores, highlights the winner,
    and offers buttons to start a new tournament or quit.
    """

    def __init__(self, window, players, scores, winner_idx, on_new_tournament):
        self.window = window
        self.on_new_tournament = on_new_tournament

        self._build_ui(players, scores, winner_idx)

    # ------------------------------------------------------------------ layout

    def _build_ui(self, players, scores, winner_idx):
        self.window.title("Backgammon — Results")

        self.frame = Frame(self.window, padx=30, pady=30)
        self.frame.pack(fill=BOTH, expand=True)

        Label(self.frame, text="Tournament Complete",
              font=("Helvetica", 18, "bold")).pack(pady=(0, 6))

        winner_name = player_spec_label(players[winner_idx])
        Label(self.frame, text=f"Winner: {winner_name}",
              font=("Helvetica", 13), fg="#2a7a2a").pack(pady=(0, 18))

        self._build_scores_table(players, scores, winner_idx)
        self._build_action_buttons()

    def _build_scores_table(self, players, scores, winner_idx):
        table = Frame(self.frame, relief=GROOVE, bd=1)
        table.pack(fill=X, pady=(0, 20))

        self._build_table_header(table)

        # Sort rows by score descending so the winner appears first
        ranked = sorted(
            enumerate(zip(players, scores)),
            key=lambda x: x[1][1],
            reverse=True,
        )
        for rank, (orig_idx, (spec, score)) in enumerate(ranked):
            self._build_table_row(table, rank, orig_idx, spec, score, winner_idx)

    def _build_table_header(self, table):
        bg = "#e0e0e0"
        for col, (text, width) in enumerate([("#", 4), ("Player", 28), ("Wins", 6)]):
            anchor = W if text == "Player" else CENTER
            Label(table, text=text, width=width, bg=bg, relief=RIDGE,
                  pady=4, anchor=anchor).grid(row=0, column=col, sticky=NSEW)

    def _build_table_row(self, table, rank, orig_idx, spec, score, winner_idx):
        is_winner = orig_idx == winner_idx
        if is_winner:
            bg = "#d4edda"
        elif rank % 2 == 0:
            bg = "white"
        else:
            bg = "#f5f5f5"

        label = player_spec_label(spec)
        for col, (text, width, anchor) in enumerate([
            (str(rank + 1), 4, CENTER),
            (label,         28, W),
            (str(score),    6,  CENTER),
        ]):
            Label(table, text=text, width=width, bg=bg,
                  pady=3, anchor=anchor).grid(row=rank + 1, column=col, sticky=NSEW)

    def _build_action_buttons(self):
        btn_frame = Frame(self.frame)
        btn_frame.pack()

        Button(btn_frame, text="New Tournament",
               command=self._new_tournament, width=16).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Quit",
               command=self.window.destroy, width=10).pack(side=LEFT, padx=5)

    # ----------------------------------------------------------------- actions

    def _new_tournament(self):
        self.frame.destroy()
        self.on_new_tournament()

    def destroy(self):
        self.frame.destroy()
