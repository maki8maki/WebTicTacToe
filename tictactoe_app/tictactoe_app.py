import reflex as rx

app = rx.App()
app.add_page(lambda: rx.fragment(), route="/", on_load=rx.redirect("/tictactoe"))
