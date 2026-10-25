import flet as ft
import hashlib
from typing import Optional, List, Any
from Model.models import User

# Attempt to import User model from possible locations
try:
    from orm import User
except ImportError:
    try:
        from Model.models import User
    except ImportError:
        User = None  # user must adjust import

class UserManagementPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.users: List[Any] = []
        self.load_users()

    def load_users(self):
        if User is None:
            self.users = []
            return
        try:
            # Assume User.all() returns list of instances
            self.users = User.all()
        except Exception:
            self.users = []

    def get_fillable_fields(self, user=None) -> List[str]:
        if User is None:
            return []
        fillable = getattr(User, 'fillable', [])
        # Exclude fields not meant for direct editing/display
        return [f for f in fillable if f not in ['id', 'created_at', 'updated_at']]

    def build_field_control(self, field_name: str, value: str) -> ft.Control:
        if field_name == 'password_hash':
            return ft.TextField(
                label='Password',
                password=True,
                can_reveal_password=True,
                value='',  # never reveal hash
                hint_text='Kosongkan jika tidak diubah' if value else 'Password'
            )
        else:
            return ft.TextField(
                label=field_name.replace('_', ' ').title(),
                value=str(value) if value is not None else ''
            )

    def open_user_dialog(self, user=None):
        if User is None:
            self.page.show_snack_bar(ft.SnackBar(ft.Text('User model not found')))
            return

        fields = {}
        controls = []
        fillable = self.get_fillable_fields(user)

        for field in fillable:
            current_value = getattr(user, field, None) if user else None
            ctrl = self.build_field_control(field, current_value)
            fields[field] = ctrl
            controls.append(ctrl)

        def save(e):
            values = {}
            for field, ctrl in fields.items():
                val = ctrl.value
                if field == 'password_hash':
                    if val:
                        values['password_hash'] = hashlib.sha256(val.encode()).hexdigest()
                    elif user and hasattr(user, 'password_hash'):
                        # Keep existing hash when editing without new password
                        values['password_hash'] = user.password_hash
                    else:
                        self.page.show_snack_bar(ft.SnackBar(ft.Text('Password required')))
                        return
                else:
                    values[field] = val

            try:
                if user:  # update existing
                    for k, v in values.items():
                        setattr(user, k, v)
                    user.save()
                    self.page.show_snack_bar(ft.SnackBar(ft.Text('User updated')))
                else:  # create new
                    new_user = User()
                    for k, v in values.items():
                        setattr(new_user, k, v)
                    new_user.save()
                    self.page.show_snack_bar(ft.SnackBar(ft.Text('User created')))
                self.load_users()
                self.update_view()
                dlg.open = False
                self.page.update()
            except Exception as ex:
                self.page.show_snack_bar(ft.SnackBar(ft.Text(f'Error: {ex}')))

        def cancel(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text('Edit User' if user else 'New User'),
            content=ft.Column(controls, spacing=10, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton('Cancel', on_click=cancel),
                ft.FilledButton('Save', on_click=save)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def delete_user(self, user):
        def confirm(e):
            try:
                user.delete()
                self.load_users()
                self.update_view()
                dlg.open = False
                self.page.update()
                self.page.show_snack_bar(ft.SnackBar(ft.Text('User deleted')))
            except Exception as ex:
                self.page.show_snack_bar(ft.SnackBar(ft.Text(f'Error: {ex}')))

        def cancel(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text('Confirm Delete'),
            content=ft.Text(f'Delete user "{getattr(user, "username", "")}"?'),
            actions=[
                ft.TextButton('Cancel', on_click=cancel),
                ft.FilledButton('Delete', on_click=confirm, bgcolor=ft.colors.RED)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def build(self):
        if User is None:
            return ft.Column([
                ft.Text('User model not found. Please adjust import in user_views.py'),
            ], expand=True)

        columns = [
            ft.DataColumn(ft.Text('ID')),
            ft.DataColumn(ft.Text('Username')),
            ft.DataColumn(ft.Text('Full Name')),
            ft.DataColumn(ft.Text('Status')),
            ft.DataColumn(ft.Text('Actions')),
        ]

        rows = []
        for user in self.users:
            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(getattr(user, 'id', '')))),
                    ft.DataCell(ft.Text(getattr(user, 'username', ''))),
                    ft.DataCell(ft.Text(getattr(user, 'full_name', ''))),
                    ft.DataCell(ft.Text(getattr(user, 'status', ''))),
                    ft.DataCell(ft.Row([
                        ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, u=user: self.open_user_dialog(u)),
                        ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, u=user: self.delete_user(u)),
                    ])),
                ]
            ))

        table = ft.DataTable(
            columns=columns,
            rows=rows,
            width=float('inf'),
            bgcolor=ft.Colors.WHITE,
            border=ft.Border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
        )

        add_button = ft.FilledButton(
            'Add User',
            icon=ft.Icons.ADD,
            on_click=lambda e: self.open_user_dialog(None),
        )

        return ft.Column([
            ft.Row([add_button], alignment=ft.MainAxisAlignment.END),
            ft.Container(content=table, padding=10),
        ], expand=True, scroll=ft.ScrollMode.AUTO)

    def update_view(self):
        # Placeholder to refresh parent view if needed
        pass


def users_view_page(page: ft.Page) -> ft.View:
    """Return the Users Management view."""
    user_page = UserManagementPage(page)
    return ft.View(
        route="/user_views",
        controls=[
            ft.AppBar(title=ft.Text("User Management"), bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
            user_page.build()
        ],
    )
