import asyncio
from typing import Dict, List

import reflex as rx

from tictactoe_app.tictactoe import RandomSelector, Selector, SquareTicTacToe, TicTacToe

THEME_BORDER = f"1px solid {rx.color('gray', 12)}"

BOX_STYLE = {
    "border": THEME_BORDER,
    "box-shadow": f"0px 0px 10px 0px {rx.color('gray', 11)}",
    "border-radius": "5px",
    "padding": "2em",
}

STATE_COLOR = {
    -1: "gray",  # 空き
    0: "red",  # 先攻
    1: "blue",  # 後攻
}


class State(rx.State):
    colored_board: List[int]
    size: int = 3
    turn: int = 0
    player_turn: int = 0
    _game: TicTacToe = SquareTicTacToe(size)
    _computer_selector: Selector = RandomSelector()
    _is_game_end: bool = False
    STATE_COLOR: Dict[int, str] = {
        -1: "gray",  # 空き
        0: "red",  # 先攻
        1: "blue",  # 後攻
    }

    def initialize(self):
        self.coloring()

    def coloring(self):
        colored_board = []
        for state in self._game.board:
            colored_board.append(self.STATE_COLOR[state])
        self.colored_board = colored_board

    def reset_board(self, sleep_time: float):
        self.turn = 0
        self._is_game_end = False
        self._game.reset()
        self.coloring()
        if self.player_turn == 1:
            return State.computer_select(sleep_time)

    def change_turn(self):
        self.player_turn = (self.player_turn + 1) % 2
        turn = "first" if self.player_turn == 0 else "second"
        components = [rx.toast.info(f"Your turn is {turn}", position="top-center", duration=1500)]
        components.append(State.reset_board(1.7))
        return components

    def apply_select(self, num: int):
        self._is_game_end = self._game.apply_select(self.turn, num)
        self.coloring()
        if len(self._game.rest) == 0:
            self._is_game_end = True
            return rx.toast.info("Draw", position="top-center", duration=5000, style={"font-size": "20px"})
        elif self._is_game_end:
            if self.turn % 2 == self.player_turn:
                return rx.toast.success("You win!!", position="top-center", duration=5000, style={"font-size": "20px"})
            else:
                return rx.toast.error("You lose...", position="top-center", duration=5000, style={"font-size": "20px"})
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
        num = self._computer_selector.select(self._game.rest)
        return self.apply_select(num)


def render_box(color, index: int):
    return rx.box(
        bg=color,
        width="50px",
        height="50px",
        border=THEME_BORDER,
        on_click=State.select_cell(index),
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
            turn_text(),
            display_board(),
            rx.hstack(
                rx.button("Change Turn", on_click=State.change_turn, width="130px"),
                rx.button("Reset", on_click=State.reset_board(0.5), width="130px"),
            ),
            align="center",
            style=BOX_STYLE,
        ),
        rx.logo(),
    )


app = rx.App()
