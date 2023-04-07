from nicegui import ui


origin_name: str = ""
dest_name: str = ""


def set_origin_name(e):
    global origin_name
    origin_name = e.value


def set_dest_name(e):
    global dest_name
    dest_name = e.value


def submit_route(origin_name: str, dest_name: str):
    ui.notify(message=f"Finding route for {origin_name} -> {dest_name}")


ui.label("DetourAI ML Backend Demo")\
    .style(add="font-size: 2em;")
with ui.row().style(add="display: flex; flex-direction: row; align-items: end;"):
    ui.input(label="Origin", on_change=set_origin_name)
    ui.label("TO")
    ui.input(label="Destination", on_change=set_dest_name)
    ui.button("Go", on_click=lambda: submit_route(origin_name, dest_name))


ui.run()