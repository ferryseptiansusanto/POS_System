import flet as ft
from views.main_view import main_view_page
from views.user_views import users_view_page

def main(page: ft.Page) -> None:
    """
    Main application router and entry point.
    """
    page.title = "Aplikasi Utama"

    def route_change(e: ft.RouteChangeEvent = None) -> None:
        page.views.clear()
        
        # 1. SELALU MASUKKAN HALAMAN UTAMA (Home) DI URUTAN PERTAMA
        # Ini wajib di Flet 1.0+ agar tidak terjadi endless reload loop
        page.views.append(
            ft.View(
                route="/",
                controls=[
                    ft.AppBar(title=ft.Text("Home"), bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
                    ft.Button(content=ft.Text("Buka Main View"), on_click=lambda _: page.navigate("/main_view")),
                    ft.Button(content=ft.Text("Buka Lainnya"), on_click=lambda _: page.navigate("/main_view")),
                ],
            )
        )
        
        # 2. TUNPUK HALAMAN LAIN DI ATASNYA JIKA RUTE BERUBAH
        # Gunakan 'if' baru, BUKAN 'elif' dari rute "/" di atas
        if page.route == "/main_view":
            page.views.append(main_view_page(page))
            
        elif page.route == "/user_views":
            page.views.append(users_view_page(page))
            
        page.update()

    def view_pop(e: ft.ViewPopEvent) -> None:
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.navigate(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    route_change() 

ft.run(main)
