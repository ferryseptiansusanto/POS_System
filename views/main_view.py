import flet as ft
from views.user_views import users_view_page

def main_view_page(page: ft.Page):
    return ft.View(
        route="/main_view",
        controls=[
            ft.AppBar(title=ft.Text("Main View"), bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
            ft.Text("Ini adalah tampilan dari main_view.py", size=20),
            ft.Button(content=ft.Text("Users"), on_click=lambda _: page.navigate("/user_views")),
            ft.Button(content=ft.Text("Kembali"), on_click=lambda _: page.navigate("/")),
        ],
    )
