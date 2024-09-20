import asyncio
from typing import Dict, List

import reflex as rx

from tictactoe_app.tictactoe import (
    BitStrategicSelector,
    RandomSelector,
    Selector,
    SquareTicTacToe,
    TicTacToe,
)

THEME_BORDER = f"1px solid {rx.color('gray', 12)}"

BOX_STYLE = {
    "border": THEME_BORDER,
    "box-shadow": f"0px 0px 10px 0px {rx.color('gray', 11)}",
    "border-radius": "5px",
    "padding": "2em",
}

SIZES = ["3", "4", "5"]
DEFAULT_SIZE = SIZES[0]


class State(rx.State):
    _game: TicTacToe
    colored_board: List[int]
    size: int = int(DEFAULT_SIZE)
    _num_cells: int = size**2
    turn: int = 0
    player_turn: int = 0
    difficulty: int = 0
    _computer_selector: Selector = RandomSelector()
    _is_game_end: bool = False
    STATE_COLOR: Dict[int, str] = {
        -1: "gray",  # 空き
        0: "red",  # 先攻
        1: "blue",  # 後攻
        2: "rgba(255,102,204)",
        3: "rgba(102,204,255)",
    }

    def initialize(self):
        self._game = SquareTicTacToe(self.size)
        self.coloring()

    def set_size(self, size: str):
        self.size = int(size)
        self._game = SquareTicTacToe(self.size)
        self.reset_selector()
        return self.reset_board(0.5)

    def coloring(self):
        colored_board = []
        for state in self._game.board:
            colored_board.append(self.STATE_COLOR[state])
        self.colored_board = colored_board

    def change_color(self, index: int, color: str):
        self.colored_board[index] = color

    def focus(self, index: int):
        if self._game.board[index] == -1:
            self.change_color(index, self.STATE_COLOR[self.turn % 2 + 2])

    def unfocus(self, index: int):
        if self._game.board[index] == -1:
            self.change_color(index, self.STATE_COLOR[-1])

    def reset_board(self, sleep_time: float):
        self.turn = 0
        self._is_game_end = False
        self._game.reset()
        self.coloring()
        if self.player_turn == 1:
            return State.computer_select(sleep_time)

    def reset_selector(self):
        if self.difficulty == 0:
            self._computer_selector = RandomSelector()
        elif self.difficulty == 1:
            self._computer_selector = BitStrategicSelector(self.size, self._num_cells, self._game.get_candidates())

    def change_turn(self):
        self.player_turn = (self.player_turn + 1) % 2
        turn = "first" if self.player_turn == 0 else "second"
        components = [rx.toast.info(f"Your turn is {turn}", position="top-center", duration=1500)]
        components.append(State.reset_board(1.7))
        return components

    def change_difficulty(self):
        self.difficulty = (self.difficulty + 1) % 2
        self.reset_selector()
        return self.reset_board(0.5)

    def apply_select(self, num: int):
        self._is_game_end = self._game.apply_select(self.turn, num)
        self.coloring()
        if len(self._game.rest) == 0:
            self._is_game_end = True
            return rx.toast.info("Draw", position="top-center", duration=5000, style={"font-size": "20px"})
        elif self._is_game_end:
            if self.turn % 2 == self.player_turn:
                return rx.toast.success(
                    "You win!!", position="top-center", duration=5000, style={"font-size": "20px"}, close_button=True
                )
            else:
                return rx.toast.error(
                    "You lose...", position="top-center", duration=5000, style={"font-size": "20px"}, close_button=True
                )
        else:
            self.turn += 1

    def select_cell(self, index: int):
        if not self._is_game_end and self.turn % 2 == self.player_turn:
            if index not in self._game.rest:
                return rx.toast.warning("Error: This cell is already selected", position="top-center", duration=1500)
            component = self.apply_select(index)
            if self._is_game_end:
                return component
            else:
                return State.computer_select(1.0)

    async def computer_select(self, sleep_time: float = 1.0):
        await asyncio.sleep(sleep_time)
        if isinstance(self._computer_selector, BitStrategicSelector):
            computer_turn = (self.player_turn + 1) % 2
            num = self._computer_selector.select(
                self._game.rest,
                self._game.players[computer_turn].candidates,
                self._game.players[self.player_turn].candidates,
            )
        else:
            num = self._computer_selector.select(self._game.rest)
        return self.apply_select(num)


def render_box(color, index: int):
    return rx.box(
        bg=color,
        width="50px",
        height="50px",
        border=THEME_BORDER,
        on_click=State.select_cell(index),
        on_mouse_enter=State.focus(index),
        on_mouse_leave=State.unfocus(index),
    )


def setting():
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.text("Board Size"),
                rx.select(
                    SIZES,
                    default_value=DEFAULT_SIZE,
                    on_change=lambda value: State.set_size(value),
                    width="100%",
                    position="popper",
                    color_scheme="green",
                ),
                align="center",
                spacing="0",
            ),
            rx.vstack(
                rx.text(f"Difficulty: Level {State.difficulty.to_string()}"),
                rx.button("Change Difficulty", on_click=State.change_difficulty, color_scheme="green"),
                align="center",
                spacing="0",
            ),
            align="end",
        ),
        rx.hstack(
            rx.button("Change Turn", on_click=State.change_turn, color_scheme="green"),
            rx.button("Reset", on_click=State.reset_board(0.5), color_scheme="green"),
        ),
        align="center",
    )


def turn_text():
    return rx.cond(
        State.turn % 2 == State.player_turn,
        rx.text("Your Turn", color=State.STATE_COLOR[State.player_turn], size="6"),
        rx.text("Computer's Turn", color=State.STATE_COLOR[(State.player_turn + 1) % 2], size="6"),
    )


def display_board():
    return rx.grid(
        rx.foreach(State.colored_board, lambda color, index: render_box(color, index)),
        columns=State.size.to_string(),
        border=THEME_BORDER,
        justify="center",
    )


@rx.page(route="/", title="Tic Tac Toe", on_load=[State.initialize()])
def index() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Welcome to Tic Tac Toe!", size="9"),
            rx.divider(),
            setting(),
            turn_text(),
            display_board(),
            align="center",
            style=BOX_STYLE,
        ),
        rx.logo(),
    )


app = rx.App()
