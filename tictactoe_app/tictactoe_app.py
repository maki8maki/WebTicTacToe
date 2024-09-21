import reflex as rx

import tictactoe_app.pages  # noqa: F401
from tictactoe_app.style import BOX_STYLE


@rx.page(route="/tictactoe", title="Tic Tac Toe")
def index() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Welcome to Tic Tac Toe!", size="9"),
            rx.hstack(
                rx.button("2D", on_click=rx.redirect("/tictactoe/2d")),
                rx.button("3D"),
            ),
            align="center",
            style=BOX_STYLE,
        ),
        rx.logo(),
    )


app = rx.App()
app.add_page(lambda: rx.fragment(), route="/", on_load=rx.redirect("/tictactoe"))
