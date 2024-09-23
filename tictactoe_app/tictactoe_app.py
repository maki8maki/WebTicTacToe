import reflex as rx

from .style import APP_THEME, STYLESHEETS

app = rx.App(stylesheets=STYLESHEETS, theme=rx.theme(**APP_THEME))
app.add_page(lambda: rx.fragment(), route="/", on_load=rx.redirect("/tictactoe"))
