from typing import Callable, List

import reflex as rx

from ..style import BOX_STYLE


def template(head_text: str, head_kwargs: dict = {"size": "8"}, need_back_t3: bool = True) -> rx.Component:
    if need_back_t3:
        back_component = rx.vstack(
            rx.button("Back to Tic Tac Toe", on_click=rx.redirect("/tictactoe")),
            rx.button("Back to Top", on_click=rx.redirect("/")),
            class_name="fixed bottom-4 right-4",
            spacing="1",
            align="end",
        )
    else:
        back_component = rx.button("Back to Top", on_click=rx.redirect("/"), class_name="fixed bottom-4 right-4")

    def wrapper(page: Callable[[], List[rx.Component]]) -> rx.Component:
        return rx.container(
            rx.color_mode.button(position="top-right"),
            rx.vstack(
                rx.heading(head_text, **head_kwargs),
                rx.divider(),
                *(page()),
                align="center",
                style=BOX_STYLE,
            ),
            rx.logo(),
            back_component,
        )

    return wrapper
