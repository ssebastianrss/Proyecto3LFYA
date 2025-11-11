import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Set, List

# Constantes y clases base
BLANK = '_'
EPSILON = 'ε'

class Direction(Enum):
    L = 'L'
    R = 'R'
    S = 'S'

@dataclass(frozen=True)
class Transition:
    write: str
    move: Direction
    next_state: str

class Tape:
    def __init__(self, blank: str = BLANK):
        self.cells: Dict[int, str] = {}
        self.head: int = 0
        self.blank: str = blank

    def reset(self, s: str):
        self.cells.clear()
        self.head = 0
        for i, ch in enumerate(s):
            self.cells[i] = ch

    def read(self) -> str:
        return self.cells.get(self.head, self.blank)

    def write(self, c: str):
        if c == self.blank:
            self.cells.pop(self.head, None)
        else:
            self.cells[self.head] = c

    def move(self, d: Direction):
        if d == Direction.L:
            self.head -= 1
        elif d == Direction.R:
            self.head += 1

    def window_bounds(self, radius: int = 12):
        if not self.cells:
            left = self.head - radius
            right = self.head + radius
        else:
            left = min(min(self.cells.keys()), self.head - radius)
            right = max(max(self.cells.keys()), self.head + radius)
        return left, right

class TuringMachine:
    def __init__(self,
                 states: Set[str],
                 start: str,
                 accept: Set[str],
                 reject: Set[str],
                 delta: Dict[str, Dict[str, Transition]],
                 tape: Tape):
        self.states = states
        self.start_state = start
        self.accept_states = accept
        self.reject_states = reject
        self.delta = delta
        self.tape = tape
        self.current_state = start

    def reset(self):
        self.current_state = self.start_state

    def load_input(self, s: str):
        self.tape.reset(s)
        self.reset()

    def is_halted(self) -> bool:
        return self.current_state in self.accept_states or self.current_state in self.reject_states

    def status(self) -> str:
        if self.current_state in self.accept_states:
            return "ACCEPT"
        if self.current_state in self.reject_states:
            return "REJECT"
        return "RUNNING"

    def step(self) -> bool:
        if self.is_halted():
            return False
        row = self.delta.get(self.current_state, {})
        t = row.get(self.tape.read())
        if t is None:
            if self.reject_states:
                self.current_state = next(iter(self.reject_states))
            return False
        self.tape.write(EPSILON)
        self.tape.move(t.move)
        self.current_state = t.next_state
        return True

def tm_one_or_more_then_any() -> TuringMachine:
    states = {"q0", "q1", "q_accept", "q_reject"}
    acc, rej = {"q_accept"}, {"q_reject"}
    tape = Tape()
    d = {s: {} for s in states}

    d["q0"]["0"] = Transition('0', Direction.R, "q0")
    d["q0"]["1"] = Transition('1', Direction.R, "q1")
    d["q0"][BLANK] = Transition(BLANK, Direction.S, "q_reject")
    d["q0"]["a"] = Transition('a', Direction.S, "q_reject")
    d["q0"]["b"] = Transition('b', Direction.S, "q_reject")

    d["q1"]["0"] = Transition('0', Direction.R, "q1")
    d["q1"]["1"] = Transition('1', Direction.R, "q1")
    d["q1"][BLANK] = Transition(BLANK, Direction.S, "q_accept")
    d["q1"]["a"] = Transition('a', Direction.S, "q_reject")
    d["q1"]["b"] = Transition('b', Direction.S, "q_reject")

    return TuringMachine(states, "q0", acc, rej, d, tape)

def tm_zeros_then_ones() -> TuringMachine:
    states = {"q0", "q1", "q_accept", "q_reject"}
    acc, rej = {"q_accept"}, {"q_reject"}
    tape = Tape()
    d = {s: {} for s in states}

    d["q0"]["0"] = Transition('0', Direction.R, "q0")
    d["q0"]["1"] = Transition('1', Direction.R, "q1")
    d["q0"][BLANK] = Transition(BLANK, Direction.S, "q_accept")
    d["q0"]["a"] = Transition('a', Direction.S, "q_reject")
    d["q0"]["b"] = Transition('b', Direction.S, "q_reject")

    d["q1"]["1"] = Transition('1', Direction.R, "q1")
    d["q1"][BLANK] = Transition(BLANK, Direction.S, "q_accept")
    d["q1"]["0"] = Transition('0', Direction.S, "q_reject")
    d["q1"]["a"] = Transition('a', Direction.S, "q_reject")
    d["q1"]["b"] = Transition('b', Direction.S, "q_reject")

    return TuringMachine(states, "q0", acc, rej, d, tape)

def tm_ab_star() -> TuringMachine:
    states = {"q0", "q1", "q_accept", "q_reject"}
    acc, rej = {"q_accept"}, {"q_reject"}
    tape = Tape()
    d = {s: {} for s in states}

    d["q0"][BLANK] = Transition(BLANK, Direction.S, "q_accept")
    d["q0"]["a"] = Transition('a', Direction.R, "q1")
    d["q0"]["b"] = Transition('b', Direction.S, "q_reject")
    d["q0"]["0"] = Transition('0', Direction.S, "q_reject")
    d["q0"]["1"] = Transition('1', Direction.S, "q_reject")

    d["q1"]["b"] = Transition('b', Direction.R, "q0")
    d["q1"]["a"] = Transition('a', Direction.S, "q_reject")
    d["q1"][BLANK] = Transition(BLANK, Direction.S, "q_reject")
    d["q1"]["0"] = Transition('0', Direction.S, "q_reject")
    d["q1"]["1"] = Transition('1', Direction.S, "q_reject")

    return TuringMachine(states, "q0", acc, rej, d, tape)

def tm_one_then_pairs_then_zero() -> TuringMachine:
    states = {"q0", "q1", "q2", "q3", "q_accept", "q_reject"}
    acc, rej = {"q_accept"}, {"q_reject"}
    tape = Tape()
    d = {s: {} for s in states}

    d["q0"]["1"] = Transition('1', Direction.R, "q1")
    d["q0"]["0"] = Transition('0', Direction.S, "q_reject")
    d["q0"][BLANK] = Transition(BLANK, Direction.S, "q_reject")
    d["q0"]["a"] = Transition('a', Direction.S, "q_reject")
    d["q0"]["b"] = Transition('b', Direction.S, "q_reject")

    d["q1"]["0"] = Transition('0', Direction.R, "q2")
    d["q1"]["1"] = Transition('1', Direction.S, "q_reject")
    d["q1"][BLANK] = Transition(BLANK, Direction.S, "q_reject")
    d["q1"]["a"] = Transition('a', Direction.S, "q_reject")
    d["q1"]["b"] = Transition('b', Direction.S, "q_reject")

    d["q2"]["1"] = Transition('1', Direction.R, "q3")
    d["q2"]["0"] = Transition('0', Direction.S, "q_accept")
    d["q2"][BLANK] = Transition(BLANK, Direction.S, "q_reject")
    d["q2"]["a"] = Transition('a', Direction.S, "q_reject")
    d["q2"]["b"] = Transition('b', Direction.S, "q_reject")

    d["q3"]["0"] = Transition('0', Direction.R, "q2")
    d["q3"]["1"] = Transition('1', Direction.S, "q_reject")
    d["q3"][BLANK] = Transition(BLANK, Direction.S, "q_reject")
    d["q3"]["a"] = Transition('a', Direction.S, "q_reject")
    d["q3"]["b"] = Transition('b', Direction.S, "q_reject")

    return TuringMachine(states, "q0", acc, rej, d, tape)

def tm_contains_at_least_one_a() -> TuringMachine:
    states = {"q0", "q1", "q_accept", "q_reject"}
    acc, rej = {"q_accept"}, {"q_reject"}
    tape = Tape()
    d = {s: {} for s in states}

    d["q0"]["a"] = Transition('a', Direction.R, "q1")
    d["q0"]["b"] = Transition('b', Direction.R, "q0")
    d["q0"][BLANK] = Transition(BLANK, Direction.S, "q_reject")
    d["q0"]["0"] = Transition('0', Direction.S, "q_reject")
    d["q0"]["1"] = Transition('1', Direction.S, "q_reject")

    d["q1"]["a"] = Transition('a', Direction.R, "q1")
    d["q1"]["b"] = Transition('b', Direction.R, "q1")
    d["q1"][BLANK] = Transition(BLANK, Direction.S, "q_accept")
    d["q1"]["0"] = Transition('0', Direction.S, "q_reject")
    d["q1"]["1"] = Transition('1', Direction.S, "q_reject")

    return TuringMachine(states, "q0", acc, rej, d, tape)

def tm_a_star() -> TuringMachine:
    states = {"q0", "q_accept", "q_reject"}
    acc, rej = {"q_accept"}, {"q_reject"}
    tape = Tape()
    d = {s: {} for s in states}

    d["q0"]["a"] = Transition('a', Direction.R, "q0")
    d["q0"][BLANK] = Transition(BLANK, Direction.S, "q_accept")
    d["q0"]["b"] = Transition('b', Direction.S, "q_reject")
    d["q0"]["0"] = Transition('0', Direction.S, "q_reject")
    d["q0"]["1"] = Transition('1', Direction.S, "q_reject")

    return TuringMachine(states, "q0", acc, rej, d, tape)

def tm_b_star() -> TuringMachine:
    states = {"q0", "q_accept", "q_reject"}
    acc, rej = {"q_accept"}, {"q_reject"}
    tape = Tape()
    d = {s: {} for s in states}

    d["q0"]["b"] = Transition('b', Direction.R, "q0")
    d["q0"][BLANK] = Transition(BLANK, Direction.S, "q_accept")
    d["q0"]["a"] = Transition('a', Direction.S, "q_reject")
    d["q0"]["0"] = Transition('0', Direction.S, "q_reject")
    d["q0"]["1"] = Transition('1', Direction.S, "q_reject")

    return TuringMachine(states, "q0", acc, rej, d, tape)

def tm_any_ab_star() -> TuringMachine:
    states = {"q0", "q_accept", "q_reject"}
    acc, rej = {"q_accept"}, {"q_reject"}
    tape = Tape()
    d = {s: {} for s in states}

    d["q0"]["a"] = Transition('a', Direction.R, "q0")
    d["q0"]["b"] = Transition('b', Direction.R, "q0")
    d["q0"][BLANK] = Transition(BLANK, Direction.S, "q_accept")
    d["q0"]["0"] = Transition('0', Direction.S, "q_reject")
    d["q0"]["1"] = Transition('1', Direction.S, "q_reject")

    return TuringMachine(states, "q0", acc, rej, d, tape)

def tm_even_a() -> TuringMachine:
    states = {"q0", "q1", "q_accept", "q_reject"}
    acc, rej = {"q_accept"}, {"q_reject"}
    tape = Tape()
    d = {s: {} for s in states}

    d["q0"]["a"] = Transition('a', Direction.R, "q1")
    d["q0"][BLANK] = Transition(BLANK, Direction.S, "q_accept")
    d["q0"]["b"] = Transition('b', Direction.S, "q_reject")
    d["q0"]["0"] = Transition('0', Direction.S, "q_reject")
    d["q0"]["1"] = Transition('1', Direction.S, "q_reject")

    d["q1"]["a"] = Transition('a', Direction.R, "q0")
    d["q1"][BLANK] = Transition(BLANK, Direction.S, "q_reject")
    d["q1"]["b"] = Transition('b', Direction.S, "q_reject")
    d["q1"]["0"] = Transition('0', Direction.S, "q_reject")
    d["q1"]["1"] = Transition('1', Direction.S, "q_reject")

    return TuringMachine(states, "q0", acc, rej, d, tape)

def tm_ab_plus() -> TuringMachine:
    states = {"q0", "q1", "q_accept", "q_reject"}
    acc, rej = {"q_accept"}, {"q_reject"}
    tape = Tape()
    d = {s: {} for s in states}

    d["q0"]["a"] = Transition('a', Direction.R, "q1")
    d["q0"][BLANK] = Transition(BLANK, Direction.S, "q_reject")
    d["q0"]["b"] = Transition('b', Direction.S, "q_reject")
    d["q0"]["0"] = Transition('0', Direction.S, "q_reject")
    d["q0"]["1"] = Transition('1', Direction.S, "q_reject")

    d["q1"]["b"] = Transition('b', Direction.R, "q0")
    d["q1"][BLANK] = Transition(BLANK, Direction.S, "q_accept")
    d["q1"]["a"] = Transition('a', Direction.S, "q_reject")
    d["q1"]["0"] = Transition('0', Direction.S, "q_reject")
    d["q1"]["1"] = Transition('1', Direction.S, "q_reject")

    return TuringMachine(states, "q0", acc, rej, d, tape)

REGEX_TABLE = [
    {
        "name": "(0|1)+1(0|1)*",
        "pattern": r"^(?:0|1)+1(?:0|1)*$",
        "alphabet": "{0,1}",
        "factory": tm_one_or_more_then_any,
        "examples": ["1", "01", "10", "1010", "00101"]
    },
    {
        "name": "0*1*",
        "pattern": r"^0*1*$",
        "alphabet": "{0,1}",
        "factory": tm_zeros_then_ones,
        "examples": ["", "0", "000", "1", "111", "0111"]
    },
    {
        "name": "(ab)*",
        "pattern": r"^(?:ab)*$",
        "alphabet": "{a,b}",
        "factory": tm_ab_star,
        "examples": ["", "ab", "abab"]
    },
    {
        "name": "1(01)*0",
        "pattern": r"^1(?:01)*0$",
        "alphabet": "{0,1}",
        "factory": tm_one_then_pairs_then_zero,
        "examples": ["10", "1010", "101010"]
    },
    {
        "name": "(a|b)*a(a|b)*",
        "pattern": r"^(?:a|b)*a(?:a|b)*$",
        "alphabet": "{a,b}",
        "factory": tm_contains_at_least_one_a,
        "examples": ["a", "ab", "ba", "aba", "bba"]
    },
    {
        "name": "a*",
        "pattern": r"^a*$",
        "alphabet": "{a}",
        "factory": tm_a_star,
        "examples": ["", "a", "aa", "aaa"]
    },
    {
        "name": "b*",
        "pattern": r"^b*$",
        "alphabet": "{b}",
        "factory": tm_b_star,
        "examples": ["", "b", "bb", "bbb"]
    },
    {
        "name": "(a|b)*",
        "pattern": r"^(?:a|b)*$",
        "alphabet": "{a,b}",
        "factory": tm_any_ab_star,
        "examples": ["", "a", "b", "ab", "ba", "aba"]
    },
    {
        "name": "(aa)*",
        "pattern": r"^(?:aa)*$",
        "alphabet": "{a}",
        "factory": tm_even_a,
        "examples": ["", "aa", "aaaa"]
    },
    {
        "name": "(ab)+",
        "pattern": r"^(?:ab)+$",
        "alphabet": "{a,b}",
        "factory": tm_ab_plus,
        "examples": ["ab", "abab", "ababab"]
    }
]

CELL_W = 26
CELL_H = 36
CELL_PAD = 4
HEAD_H = 12

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Máquina de Turing")
        self.geometry("920x520")
        self.resizable(False, False)
        self.tm: TuringMachine | None = None
        self.running = False
        self.after_id = None
        self.speed_ms = 300
        self.returning = False
        self._build_ui()
        self._load_selected_machine()

    def _build_ui(self):
        top = ttk.Frame(self, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(top, text="Expresión/MT:").grid(row=0, column=0, sticky="w")
        self.combo = ttk.Combobox(top, width=42,
                                  values=[item["name"] for item in REGEX_TABLE], state="readonly")
        self.combo.current(0)
        self.combo.grid(row=0, column=1, padx=6, sticky="w")
        top.grid_columnconfigure(2, weight=1)
        ttk.Label(top, text="Cadena:").grid(row=0, column=3, padx=(12, 0), sticky="e")
        self.entry = ttk.Entry(top, width=28)
        self.entry.grid(row=0, column=4, padx=6, sticky="e")
        self.entry.insert(0, REGEX_TABLE[0]["examples"][0])
        self.btn_insert = ttk.Button(top, text="Insertar", command=self.on_insert)
        self.btn_insert.grid(row=0, column=5, padx=6, sticky="e")

        info = ttk.Frame(self, padding=8)
        info.pack(side=tk.TOP, fill=tk.X)
        self.lbl_state = ttk.Label(info, text="Estado: -")
        self.lbl_state.pack(side=tk.LEFT, padx=6)
        self.lbl_status = ttk.Label(info, text="Ejecución: -")
        self.lbl_status.pack(side=tk.LEFT, padx=12)
        self.lbl_regex = ttk.Label(info, text="Regex: -")
        self.lbl_regex.pack(side=tk.LEFT, padx=12)
        self.lbl_alphabet = ttk.Label(info, text="Σ: -")
        self.lbl_alphabet.pack(side=tk.LEFT, padx=12)

        self.canvas = tk.Canvas(self, width=900, height=320, bg="#101418", highlightthickness=0)
        self.canvas.pack(side=tk.TOP, pady=8)

        bottom = ttk.Frame(self, padding=(8, 6))
        bottom.pack(side=tk.BOTTOM, fill=tk.X)
        ctrl = ttk.Frame(bottom)
        ctrl.pack(side=tk.TOP, pady=2)
        ctrl.pack_configure(anchor="center")
        self.btn_play = ttk.Button(ctrl, text="Play ▶", command=self.on_play)
        self.btn_play.grid(row=0, column=0, padx=4)
        self.btn_pause = ttk.Button(ctrl, text="Pause ⏸", command=self.on_pause)
        self.btn_pause.grid(row=0, column=1, padx=4)
        self.btn_step = ttk.Button(ctrl, text="Paso ➤", command=self.on_step)
        self.btn_step.grid(row=0, column=2, padx=4)
        self.btn_reset = ttk.Button(ctrl, text="Reset ↺", command=self.on_reset)
        self.btn_reset.grid(row=0, column=3, padx=4)

        speed_fr = ttk.Frame(bottom)
        speed_fr.pack(side=tk.RIGHT)
        ttk.Label(speed_fr, text="Velocidad:").pack(side=tk.LEFT, padx=(0, 6))
        self.speed = ttk.Scale(speed_fr, from_=600, to=30, value=self.speed_ms,
                               command=self.on_speed_change, orient=tk.HORIZONTAL, length=220)
        self.speed.pack(side=tk.LEFT)

        self.combo.bind("<<ComboboxSelected>>", lambda e: self.on_change_regex())

    def on_insert(self):
        if self.tm is None:
            return
        s = self.entry.get().strip()
        self.tm.load_input(s)
        self._update_info_labels()
        self._redraw_tape()

    def on_change_regex(self):
        self._load_selected_machine()

    def on_speed_change(self, val):
        self.speed_ms = int(float(val))

    def _load_selected_machine(self):
        item = REGEX_TABLE[self.combo.current()]
        self.tm = item["factory"]()
        example = item["examples"][0]
        self.entry.delete(0, tk.END)
        self.entry.insert(0, example)
        self.tm.load_input(example)
        self._update_info_labels()
        self._redraw_tape()

    def on_play(self):
        if self.running:
            return
        self.running = True
        self.returning = False
        self._tick()

    def on_pause(self):
        self.running = False
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

    def on_step(self):
        self.running = False
        if self.tm is None:
            return
        self.tm.step()
        self._update_info_labels()
        self._redraw_tape()

    def on_reset(self):
        self.on_pause()
        if self.tm is None:
            return
        s = self.entry.get().strip()
        self.tm.load_input(s)
        self._update_info_labels()
        self._redraw_tape()

    def _tick(self):
        if not self.running:
            return
        if self.tm and not self.tm.is_halted():
            self.tm.step()
            self._update_info_labels()
            self._redraw_tape()
            self.after_id = self.after(self.speed_ms, self._tick)
        else:
            if not self.returning and self.tm:
                self.returning = True
                self._return_head_to_start()
            else:
                self.running = False
                self.returning = False
                self._update_info_labels()

    def _return_head_to_start(self):
        if self.tm.tape.head > 0:
            self.tm.tape.move(Direction.L)
            self._redraw_tape()
            self.after_id = self.after(self.speed_ms, self._return_head_to_start)
        else:
            self.running = False
            self.returning = False
            self._update_info_labels()

    def _update_info_labels(self):
        item = REGEX_TABLE[self.combo.current()]
        st = self.tm.current_state if self.tm else "-"
        self.lbl_state.config(text=f"Estado: {st}")
        self.lbl_status.config(text=f"Ejecución: {self.tm.status() if self.tm else '-'}")
        self.lbl_regex.config(text=f"Regex: {item['pattern']}")
        self.lbl_alphabet.config(text=f"Σ: {item['alphabet']}")

    def _redraw_tape(self):
        self.canvas.delete("all")
        if not self.tm:
            return
        left, right = self.tm.tape.window_bounds(radius=12)
        x0 = 10
        y0 = 60
        for i in range(left, right + 1):
            x = x0 + (i - left) * (CELL_W + CELL_PAD)
            self.canvas.create_rectangle(x, y0, x + CELL_W, y0 + CELL_H,
                                         outline="#3A4250",
                                         fill="#18202A")
            ch = self.tm.tape.cells.get(i, BLANK)
            color = "#E5E7EB" if ch != BLANK else "#6B7280"
            self.canvas.create_text(x + CELL_W / 2, y0 + CELL_H / 2, text=ch, fill=color, font=("Consolas", 14, "bold"))
            if i == self.tm.tape.head:
                self.canvas.create_polygon(
                    x + CELL_W * 0.2, y0 - HEAD_H,
                    x + CELL_W * 0.8, y0 - HEAD_H,
                    x + CELL_W / 2, y0 - 2,
                    fill="#10B981", outline=""
                )
                self.canvas.create_rectangle(x, y0, x + CELL_W, y0 + CELL_H, outline="#10B981", width=2)

        self.canvas.create_text(450, 20, text="Cinta ( '_' = blanco, 'ε' = leído )", fill="#93C5FD", font=("Segoe UI", 10, "bold"))
        self.canvas.create_text(450, 38, text=f"Cabezal en índice {self.tm.tape.head}", fill="#60A5FA", font=("Segoe UI", 9))

if __name__ == "__main__":
    app = App()
    app.mainloop()
