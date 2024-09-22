import reflex as rx

from .style import APP_THEME

app = rx.App(theme=rx.theme(**APP_THEME))
app.add_page(lambda: rx.fragment(), route="/", on_load=rx.redirect("/tictactoe"))
