import reflex as rx

THEME_BORDER = f"1px solid {rx.color('gray', 12)}"

BOX_STYLE = {
    "border": THEME_BORDER,
    "box-shadow": f"0px 0px 10px 0px {rx.color('gray', 11)}",
    "border-radius": "5px",
    "padding": "2em",
}

APP_THEME = {
    "radius": "large",
    "accent_color": "green",
}

SIZES = ["3", "4", "5"]
DEFAULT_SIZE = SIZES[0]
