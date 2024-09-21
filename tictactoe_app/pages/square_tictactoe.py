import asyncio
from typing import Dict, List

import reflex as rx

from ..style import BOX_STYLE, DEFAULT_SIZE, SIZES, THEME_BORDER
from ..tictactoe import BitStrategicSelector, RandomSelector, Selector, SquareTicTacToe


class SquareTicTacToeState(rx.State):
    _num_cells: int
    _game: SquareTicTacToe
    _computer_selector: Selector
    colored_board: List[int]
    size: int = int(DEFAULT_SIZE)
    turn: int = 0
    player_turn: int = 0
    difficulty: int = 0
    _is_game_end: bool = False
    STATE_COLOR: Dict[int, str] = {
        -1: "gray",  # 空き
        0: "red",  # 先攻
        1: "blue",  # 後攻
        2: "rgba(255,102,204)",
        3: "rgba(102,204,255)",
    }

    # *** 初期化やリセットに関する関数 ***
    def initialize(self):
        self._num_cells = self.size**2
        self.make_tictactoe()
        self.reset_selector()
        self.coloring()

    def make_tictactoe(self):
        self._game = SquareTicTacToe(self.size)

    def reset_board(self, sleep_time: float):
        self.turn = 0
        self._is_game_end = False
        self._game.reset()
        self.coloring()
        if self.player_turn == 1:
            return SquareTicTacToeState.computer_select(sleep_time)

    def reset_selector(self):
        if self.difficulty == 0:
            self._computer_selector = RandomSelector()
        elif self.difficulty == 1:
            self._computer_selector = BitStrategicSelector(self.size, self._num_cells, self._game.get_candidates())

    # *** 便利関数 ***
    def coloring(self):
        colored_board = []
        for state in self._game.board:
            colored_board.append(self.STATE_COLOR[state])
        self.colored_board = colored_board

    def change_cell_color(self, index: int, color: str):
        self.colored_board[index] = color

    # *** 選択に関する関数 ***
    def apply_select(self, num: int):
        self._is_game_end = self._game.apply_select(self.turn, num)
        self.coloring()
        if len(self._game.rest) == 0:
            self._is_game_end = True
            return rx.toast.info("Draw", position="top-center", duration=5000, style={"font-size": "20px"})
        elif self._is_game_end:
            if self.turn % 2 == self.player_turn:
                return rx.toast.success(
                    "You win!!",
                    position="top-center",
                    duration=5000,
                    style={"font-size": "20px"},
                    close_button=True,
                )
            else:
                return rx.toast.error(
                    "You lose...",
                    position="top-center",
                    duration=5000,
                    style={"font-size": "20px"},
                    close_button=True,
                )
        else:
            self.turn += 1

    def select_cell(self, index: int):
        if not self._is_game_end and self.turn % 2 == self.player_turn:
            if index not in self._game.rest:
                return rx.toast.warning("This cell is already selected", position="top-center", duration=1500)
            component = self.apply_select(index)
            if self._is_game_end:
                return component
            else:
                return SquareTicTacToeState.computer_select(1.0)

    async def computer_select(self, sleep_time: float):
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

    # *** インタラクションの関数 ***
    def change_size(self, size: str):
        self.size = int(size)
        self.make_tictactoe()
        self.reset_selector()
        return self.reset_board(0.5)

    def focus_cell(self, index: int):
        if self._game.board[index] == -1:
            self.change_cell_color(index, self.STATE_COLOR[self.turn % 2 + 2])

    def unfocus_cell(self, index: int):
        if self._game.board[index] == -1:
            self.change_cell_color(index, self.STATE_COLOR[-1])

    def change_turn(self):
        self.player_turn = (self.player_turn + 1) % 2
        turn = "first" if self.player_turn == 0 else "second"
        components = [rx.toast.info(f"Your turn is {turn}", position="top-center", duration=1500)]
        components.append(SquareTicTacToeState.reset_board(1.7))
        return components

    def change_difficulty(self):
        self.difficulty = (self.difficulty + 1) % 2
        self.reset_selector()
        return self.reset_board(0.5)


def render_box(color, index: int):
    return rx.box(
        bg=color,
        width="50px",
        height="50px",
        border=THEME_BORDER,
        on_click=SquareTicTacToeState.select_cell(index),
        on_mouse_enter=SquareTicTacToeState.focus_cell(index),
        on_mouse_leave=SquareTicTacToeState.unfocus_cell(index),
    )


def setting():
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.text("Board Size"),
                rx.select(
                    SIZES,
                    default_value=DEFAULT_SIZE,
                    on_change=lambda value: SquareTicTacToeState.change_size(value),
                    width="100%",
                    position="popper",
                    color_scheme="green",
                ),
                align="center",
                spacing="0",
            ),
            rx.vstack(
                rx.text(f"Difficulty: Level {SquareTicTacToeState.difficulty.to_string()}"),
                rx.button(
                    "Change Difficulty", on_click=SquareTicTacToeState.change_difficulty(), color_scheme="green"
                ),
                align="center",
                spacing="0",
            ),
            align="end",
        ),
        rx.hstack(
            rx.button("Change Turn", on_click=SquareTicTacToeState.change_turn(), color_scheme="green"),
            rx.button("Reset", on_click=SquareTicTacToeState.reset_board(0.5), color_scheme="green"),
        ),
        align="center",
    )


def turn_text():
    return rx.cond(
        SquareTicTacToeState.turn % 2 == SquareTicTacToeState.player_turn,
        rx.text("Your Turn", color=SquareTicTacToeState.STATE_COLOR[SquareTicTacToeState.player_turn], size="6"),
        rx.text(
            "Computer's Turn",
            color=SquareTicTacToeState.STATE_COLOR[(SquareTicTacToeState.player_turn + 1) % 2],
            size="6",
        ),
    )


def display_board():
    return rx.grid(
        rx.foreach(SquareTicTacToeState.colored_board, lambda color, index: render_box(color, index)),
        columns=SquareTicTacToeState.size.to_string(),
        border=THEME_BORDER,
        justify="center",
    )


@rx.page(route="/tictactoe/2d", title="Square Tic Tac Toe", on_load=[SquareTicTacToeState.initialize()])
def square_t3_page() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Square Tic Tac Toe", size="8"),
            rx.divider(),
            setting(),
            turn_text(),
            display_board(),
            align="center",
            style=BOX_STYLE,
        ),
        rx.logo(),
        rx.vstack(
            rx.button("Back to Tic Tac Toe", on_click=rx.redirect("/tictactoe"), color_scheme="green"),
            rx.button("Back to Top", on_click=rx.redirect("/"), color_scheme="green"),
            class_name="fixed bottom-4 right-4",
            spacing="1",
            align="end",
        ),
    )
