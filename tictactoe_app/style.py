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

STATE_COLOR = {
    -1: "gray",  # 空き
    0: "red",  # 先攻
    1: "blue",  # 後攻
    2: "rgba(255,102,204)",
    3: "rgba(102,204,255)",
}

RESULT_TOAST = {
    "position": "top-center",
    "duration": 5000,
    "style": {"font-size": "20px"},
    "close_button": True,
}

CHANGE_TURN_TOAST = {
    "position": "top-center",
    "duration": 1500,
    "style": {
        "background-color": "white",
        "color": "black",
        "border": "1px solid black",
        "border-radius": "0.53m",
    },
}

STYLESHEETS = ["tictactoe.css"]
