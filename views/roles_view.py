"""Role management view."""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from main_window import MainWindow

# Ensure the Model directory is importable before importing `models`
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_DIR = os.path.join(_PROJECT_ROOT, "Model")
if _MODEL_DIR not in sys.path:
    sys.path.insert(0, _MODEL_DIR)

from models import Role  # noqa: E402

# Flet version compatibility
Colors = getattr(ft, "Colors", None) or ft.colors
Icons = getattr(ft, "Icons", None) or ft.icons


class RolesView:
    def __init__(self, page: ft.Page, app: "MainWindow"):
        self.page = page
        self.app = app
        self.roles_cache: list = []
        self._load_roles()

    def _load_roles(self):
        try:
            self.roles_cache = list(Role.order_by("name").get())
        except Exception:
            try:
                self.roles_cache = list(Role.all())
            except Exception as exc:
                self.roles_cache = []
                print(f"[WARN] load roles: {exc}")

    def build(self) -> ft.Control:
        self._load_roles()
        rows = []
        for role in self.roles_cache:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(role.name or "-")),
                        ft.DataCell(ft.Text(role.description or "-")),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        Icons.EDIT,
                                        icon_size=18,
                                        on_click=lambda e, r=role: self._role_dialog(r),
                                    ),
                                    ft.IconButton(
                                        Icons.DELETE_OUTLINE,
                                        icon_size=18,
                                        icon_color=Colors.RED_400,
                                        on_click=lambda e, r=role: self._delete_role(r),
                                    ),
                                ],
                                spacing=0,
                            )
                        ),
                    ]
                )
            )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(h))
                for h in ("Nama", "Deskripsi", "Aksi")
            ],
            rows=rows,
            heading_row_color=Colors.GREY_100,
        )

        return self.app._card(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Master Peran (Role)", size=18, weight="bold", expand=True),
                            ft.ElevatedButton(
                                "Tambah Role",
                                icon=Icons.ADD,
                                on_click=lambda e: self._role_dialog(None),
                            ),
                        ]
                    ),
                    ft.Divider(),
                    ft.Column([table], scroll="auto", expand=True),
                ],
                expand=True,
            ),
            expand=True,
        )

    def _role_dialog(self, role=None):
        fields = {
            "name": ft.TextField(
                label="Nama Role",
                value=getattr(role, "name", "") or "",
            ),
            "description": ft.TextField(
                label="Deskripsi",
                multiline=True,
                min_lines=2,
                value=getattr(role, "description", "") or "",
            ),
        }

        def save(e):
            name = fields["name"].value.strip()
            description = fields["description"].value.strip()

            if not name:
                self.app._toast("Nama role wajib diisi", error=True)
                return

            payload = {
                "name": name,
                "description": description,
            }

            try:
                if role is None:
                    Role.create(**payload)
                else:
                    role.update(**payload)
            except Exception as exc:
                self.app._toast(f"Gagal menyimpan role: {exc}", error=True)
                return

            self.app._close_dialog(dialog)
            self._load_roles()
            self.app.show_page(4)
            self.app._toast("Role tersimpan")

        dialog = ft.AlertDialog(
            title=ft.Text("Tambah Role" if role is None else "Edit Role"),
            content=ft.Container(
                ft.Column(list(fields.values()), spacing=8, tight=True),
                width=360,
            ),
            actions=[
                ft.TextButton("Batal", on_click=lambda e: self.app._close_dialog(dialog)),
                ft.ElevatedButton("Simpan", on_click=save),
            ],
        )
        self.app._open_dialog(dialog)

    def _delete_role(self, role):
        try:
            role.delete()
        except Exception as exc:
            self.app._toast(f"Gagal menghapus role: {exc}", error=True)
            return
        self._load_roles()
        self.app.show_page(4)
        self.app._toast("Role dihapus")
