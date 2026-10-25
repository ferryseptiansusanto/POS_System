"""views/main_window.py

GUI utama aplikasi POS berbasis Flet.

Fitur:
    - Kasir (POS)  : cari produk, keranjang, diskon, metode bayar, kembalian
    - Produk       : CRUD barang
    - Pelanggan    : CRUD pelanggan
    - Riwayat      : daftar transaksi + detail struk
    - Roles        : CRUD role pengguna

Didesain agar tetap kompatibel dengan Flet 0.2x maupun 0.3x.
"""

from __future__ import annotations

import contextlib
import datetime
import os
import sys

import flet as ft

# ---------------------------------------------------------------------------
# Bootstrap path: pastikan folder `orm/`, `Model/`, dan `views/` bisa di-import
# (models.py memakai `from eloquent_base import Model`)
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _path in (
    PROJECT_ROOT,
    os.path.join(PROJECT_ROOT, "orm"),
    os.path.join(PROJECT_ROOT, "Model"),
    os.path.join(PROJECT_ROOT, "views"),
):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from models import Customer, Item, Role, Sale, SaleDetail, User  # noqa: E402
from roles_view import RolesView  # noqa: E402

try:  # transaksi database (opsional)
    from database_manager import DB, DatabaseManager
except Exception:  # pragma: no cover
    DB = None
    DatabaseManager = None


# ---------------------------------------------------------------------------
# Kompatibilitas konstanta antar versi Flet
# ---------------------------------------------------------------------------
Colors = getattr(ft, "Colors", None) or ft.colors
Icons = getattr(ft, "Icons", None) or ft.icons

try:  # Flet >= 0.28
    DdOption = ft.DropdownOption
except AttributeError:  # Flet 0.2x
    DdOption = ft.dropdown.Option


# ---------------------------------------------------------------------------
# Util
# ---------------------------------------------------------------------------
def rupiah(value) -> str:
    """Format angka menjadi 'Rp 12.500'."""
    try:
        value = float(value or 0)
    except (TypeError, ValueError):
        value = 0.0
    return "Rp " + format(int(round(value)), ",").replace(",", ".")


def to_number(value, default=0.0) -> float:
    """Parse input angka dari TextField (toleran terhadap 'Rp', '.', ',')."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace("Rp", "").replace(" ", "")
    if not text:
        return default
    # buang pemisah ribuan, ubah koma desimal menjadi titik
    if text.count(".") and text.count(",") == 0:
        text = text.replace(".", "")
    text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return default


def ensure_database() -> None:
    """Buat tabel awal dari Database/database.sql jika database masih kosong."""
    if DatabaseManager is None:
        return
    sql_path = os.path.join(PROJECT_ROOT, "Database", "database.sql")
    try:
        conn = DatabaseManager.get_connection("default")
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='items'"
        ).fetchone()
        if row:
            return
        if os.path.isfile(sql_path):
            with open(sql_path, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
            conn.commit()
            print("[OK] Skema database berhasil dibuat dari database.sql")
    except Exception as exc:  # driver non-sqlite / error izin
        print(f"[WARN] ensure_database: {exc}")


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------
class MainWindow:
    """Controller + View utama aplikasi POS."""

    def __init__(self, page: ft.Page):
        self.page = page

        # state kasir
        self.cart: dict[int, int] = {}          # item_id -> qty
        self.items_cache: list = []            # cache Item
        self.discount_value = 0.0
        self.selected_customer_id = None

        self._setup_page()
        self._build_controls()
        self.roles_view = RolesView(self.page, self)
        self._load_items()
        self._load_customers()
        self.show_page(0)

    # -- setup -------------------------------------------------------------
    def _setup_page(self) -> None:
        self.page.title = "POS Toko - Flet"
        try:
            self.page.theme_mode = ft.ThemeMode.LIGHT
        except Exception:
            pass
        try:
            self.page.window_width = 1280
            self.page.window_height = 800
        except Exception:
            try:
                self.page.window.width = 1280
                self.page.window.height = 800
            except Exception:
                pass
        self.page.padding = 0
        self.page.bgcolor = Colors.GREY_100

    def _build_controls(self) -> None:
        self.rail = ft.NavigationRail(
            selected_index=0,
            label_type="all",
            min_width=90,
            bgcolor=Colors.WHITE,
            extended=True,
            destinations=[
                ft.NavigationRailDestination(icon=Icons.POINT_OF_SALE, label="Kasir"),
                ft.NavigationRailDestination(icon=Icons.INVENTORY_2, label="Produk"),
                ft.NavigationRailDestination(icon=Icons.PEOPLE, label="Pelanggan"),
                ft.NavigationRailDestination(icon=Icons.RECEIPT_LONG, label="Riwayat"),
                ft.NavigationRailDestination(icon=Icons.GROUPS, label="Roles"),
            ],
            on_change=lambda e: self.show_page(e.control.selected_index),
        )
        self.body = ft.Container(expand=True, padding=16)

    # -- helper UI ---------------------------------------------------------
    def _toast(self, message: str, error: bool = False) -> None:
        snack = ft.SnackBar(
            content=ft.Text(message, color=Colors.WHITE),
            bgcolor=Colors.RED_400 if error else Colors.GREEN_600,
        )
        try:
            self.page.open(snack)
        except Exception:
            self.page.snack_bar = snack
            snack.open = True
            self.page.update()

    def _open_dialog(self, dialog) -> None:
        try:
            self.page.open(dialog)
        except Exception:
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

    def _close_dialog(self, dialog) -> None:
        try:
            self.page.close(dialog)
        except Exception:
            dialog.open = False
            self.page.dialog = None
            self.page.update()

    def _card(self, content, **kwargs) -> ft.Container:
        return ft.Container(
            content=content,
            bgcolor=Colors.WHITE,
            border_radius=12,
            padding=16,
            **kwargs,
        )

    # -- navigasi ----------------------------------------------------------
    def show_page(self, index: int) -> None:
        self.rail.selected_index = index
        if index == 0:
            self.body.content = self.view_pos()
        elif index == 1:
            self.body.content = self.view_products()
        elif index == 2:
            self.body.content = self.view_customers()
        elif index == 3:
            self.body.content = self.view_history()
        elif index == 4:
            self.body.content = self.roles_view.build()
        else:
            self.body.content = self.view_pos()
        self.page.update()

    def build(self) -> ft.Control:
        return ft.Row([self.rail, ft.VerticalDivider(width=1), self.body], expand=True)

    # =====================================================================
    # DATA LOADER
    # =====================================================================
    def _load_items(self) -> None:
        try:
            self.items_cache = list(Item.order_by("name").get())
        except Exception as exc:
            self.items_cache = []
            print(f"[WARN] load items: {exc}")

    def _load_customers(self) -> None:
        try:
            self.customers_cache = list(Customer.order_by("full_name").get())
        except Exception as exc:
            self.customers_cache = []
            print(f"[WARN] load customers: {exc}")

    def _cashier_id(self):
        try:
            users = User.all()
            return users[0].id if users else None
        except Exception:
            return None

    def _item_by_id(self, item_id: int):
        for item in self.items_cache:
            if item.id == item_id:
                return item
        return None

    # =====================================================================
    # VIEW: KASIR / POS
    # =====================================================================
    def view_pos(self) -> ft.Control:
        self.search_field = ft.TextField(
            hint_text="Cari nama produk / SKU ...",
            prefix_icon=Icons.SEARCH,
            border_radius=10,
            filled=True,
            bgcolor=Colors.GREY_50,
            on_change=lambda e: self._render_product_list(e.control.value),
        )
        self.product_list = ft.ListView(expand=True, spacing=6, padding=0)
        self._render_product_list("")

        product_panel = self._card(
            ft.Column(
                [
                    ft.Text("Katalog Produk", size=16, weight="bold"),
                    self.search_field,
                    ft.Container(content=self.product_list, expand=True),
                ],
                expand=True,
                spacing=10,
            ),
            expand=3,
        )

        cart_panel = self._card(self._build_cart_panel(), expand=2)

        return ft.Row([product_panel, cart_panel], expand=True, spacing=16)

    def _render_product_list(self, keyword: str) -> None:
        keyword = (keyword or "").lower().strip()
        self.product_list.controls.clear()
        for item in self.items_cache:
            haystack = f"{item.name or ''} {item.sku or ''} {item.category or ''}".lower()
            if keyword and keyword not in haystack:
                continue
            stock = int(item.stock or 0)
            self.product_list.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(item.name or "-", weight="bold", size=14),
                                    ft.Text(
                                        f"{item.sku or '-'} • stok {stock} {item.unit or ''}",
                                        size=11,
                                        color=Colors.GREY_600,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.Text(rupiah(item.sell_price), weight="bold", color=Colors.BLUE_700),
                        ],
                        alignment="spaceBetween",
                    ),
                    padding=10,
                    border_radius=10,
                    bgcolor=Colors.GREY_50 if stock > 0 else Colors.GREY_200,
                    on_click=(lambda e, i=item: self._add_to_cart(i)) if stock > 0 else None,
                    ink=stock > 0,
                )
            )
        if not self.product_list.controls:
            self.product_list.controls.append(
                ft.Text("Tidak ada produk. Tambahkan dulu di menu Produk.",
                        color=Colors.GREY_600, size=12)
            )
        try:
            self.page.update()
        except Exception:
            pass

    def _build_cart_panel(self) -> ft.Control:
        self.cart_list = ft.ListView(expand=True, spacing=6, padding=0)
        self.discount_field = ft.TextField(
            label="Diskon (Rp)",
            value="0",
            width=150,
            dense=True,
            on_change=self._on_discount_change,
        )
        self.payment_method = ft.Dropdown(
            label="Metode",
            value="cash",
            width=150,
            dense=True,
            options=[DdOption("cash", "Cash"), DdOption("qris", "QRIS"),
                     DdOption("debit", "Debit"), DdOption("transfer", "Transfer")],
            on_change=lambda e: self._refresh_cart(),
        )
        self.customer_dropdown = ft.Dropdown(
            label="Pelanggan (opsional)",
            value="",
            dense=True,
            options=[DdOption("", "Umum / non-member")],
            on_change=self._on_customer_change,
        )
        self._refresh_customer_dropdown()

        self.paid_field = ft.TextField(
            label="Uang diterima",
            value="",
            dense=True,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=lambda e: self._refresh_summary(),
        )
        self.summary_text = ft.Text("", size=12, color=Colors.GREY_700)
        self.change_text = ft.Text("", size=16, weight="bold", color=Colors.GREEN_700)

        return ft.Column(
            [
                ft.Text("Keranjang", size=16, weight="bold"),
                self.customer_dropdown,
                ft.Container(content=self.cart_list, expand=True),
                ft.Divider(height=1),
                ft.Row([self.discount_field, self.payment_method],
                       alignment="spaceBetween"),
                self.summary_text,
                self.paid_field,
                self.change_text,
                ft.ElevatedButton(
                    "Bayar",
                    icon=Icons.PAYMENTS,
                    height=46,
                    style=ft.ButtonStyle(bgcolor=Colors.GREEN_600, color=Colors.WHITE),
                    on_click=self._on_pay,
                    width=10000,
                ),
                ft.OutlinedButton(
                    "Kosongkan",
                    icon=Icons.DELETE_SWEEP,
                    on_click=lambda e: self._clear_cart(),
                    width=10000,
                ),
            ],
            expand=True,
            spacing=10,
        )

    def _refresh_customer_dropdown(self) -> None:
        try:
            options = [DdOption("", "Umum / non-member")]
            for cust in getattr(self, "customers_cache", []):
                options.append(DdOption(str(cust.id), cust.full_name or f"#{cust.id}"))
            self.customer_dropdown.options = options
        except Exception:
            pass

    def _add_to_cart(self, item) -> None:
        stock = int(item.stock or 0)
        current = self.cart.get(item.id, 0)
        if current + 1 > stock:
            self._toast(f"Stok {item.name} tidak cukup (sisa {stock})", error=True)
            return
        self.cart[item.id] = current + 1
        self._refresh_cart()

    def _change_qty(self, item_id: int, delta: int) -> None:
        qty = self.cart.get(item_id, 0) + delta
        if qty <= 0:
            self.cart.pop(item_id, None)
        else:
            item = self._item_by_id(item_id)
            if item and qty > int(item.stock or 0):
                self._toast("Melebihi stok tersedia", error=True)
                return
            self.cart[item_id] = qty
        self._refresh_cart()

    def _clear_cart(self) -> None:
        self.cart.clear()
        self.discount_value = 0.0
        try:
            self.discount_field.value = "0"
            self.paid_field.value = ""
        except Exception:
            pass
        self._refresh_cart()

    def _on_discount_change(self, e) -> None:
        self.discount_value = to_number(e.control.value)
        self._refresh_summary()

    def _on_customer_change(self, e) -> None:
        value = (e.control.value or "").strip()
        self.selected_customer_id = int(value) if value.isdigit() else None

    def _subtotal(self) -> float:
        subtotal = 0.0
        for item_id, qty in self.cart.items():
            item = self._item_by_id(item_id)
            if item:
                subtotal += float(item.sell_price or 0) * qty
        return subtotal

    def _grand_total(self) -> float:
        return max(self._subtotal() - self.discount_value, 0.0)

    def _refresh_cart(self) -> None:
        self.cart_list.controls.clear()
        for item_id, qty in list(self.cart.items()):
            item = self._item_by_id(item_id)
            if not item:
                continue
            price = float(item.sell_price or 0)
            self.cart_list.controls.append(
                ft.Container(
                    padding=8,
                    border_radius=8,
                    bgcolor=Colors.GREY_50,
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(item.name or "-", size=13, weight="bold"),
                                    ft.Text(rupiah(price) + f" x {qty}", size=11,
                                            color=Colors.GREY_600),
                                ],
                                spacing=1,
                                expand=True,
                            ),
                            ft.IconButton(
                                Icons.REMOVE_CIRCLE_OUTLINE,
                                icon_size=18,
                                on_click=lambda e, i=item_id: self._change_qty(i, -1),
                            ),
                            ft.Text(str(qty), width=20, text_align="center"),
                            ft.IconButton(
                                Icons.ADD_CIRCLE_OUTLINE,
                                icon_size=18,
                                on_click=lambda e, i=item_id: self._change_qty(i, 1),
                            ),
                            ft.Text(rupiah(price * qty), weight="bold", size=13),
                        ],
                        alignment="spaceBetween",
                    ),
                )
            )
        if not self.cart_list.controls:
            self.cart_list.controls.append(
                ft.Text("Keranjang kosong. Klik produk di kiri.",
                        color=Colors.GREY_600, size=12)
            )
        self._refresh_summary()

    def _refresh_summary(self) -> None:
        subtotal = self._subtotal()
        total = self._grand_total()
        method = getattr(self.payment_method, "value", "cash")
        try:
            self.summary_text.value = (
                f"Subtotal: {rupiah(subtotal)}\nDiskon: {rupiah(self.discount_value)}\n"
                f"Total: {rupiah(total)}"
            )
        except Exception:
            pass

        paid = to_number(self.paid_field.value)
        try:
            if method == "cash" and paid > 0:
                change = paid - total
                if change >= 0:
                    self.change_text.value = f"Kembalian: {rupiah(change)}"
                    self.change_text.color = Colors.GREEN_700
                else:
                    self.change_text.value = f"Kurang: {rupiah(abs(change))}"
                    self.change_text.color = Colors.RED_600
            else:
                self.change_text.value = ""
        except Exception:
            pass
        try:
            self.page.update()
        except Exception:
            pass

    # -- transaksi ---------------------------------------------------------
    def _next_invoice_no(self) -> str:
        prefix = "INV-" + datetime.date.today().strftime("%Y%m%d") + "-"
        try:
            count = Sale.where("invoice_no", "LIKE", prefix + "%").count()
        except Exception:
            count = 0
        return f"{prefix}{int(count) + 1:04d}"

    def _on_pay(self, e) -> None:
        if not self.cart:
            self._toast("Keranjang masih kosong", error=True)
            return

        subtotal = self._subtotal()
        total = self._grand_total()
        method = getattr(self.payment_method, "value", "cash") or "cash"
        paid = to_number(self.paid_field.value)

        if method == "cash":
            if paid <= 0:
                self._toast("Masukkan uang yang diterima", error=True)
                return
            if paid < total:
                self._toast("Uang yang diterima kurang dari total", error=True)
                return
        else:
            paid = total

        invoice_no = self._next_invoice_no()
        user_id = self._cashier_id()

        try:
            context = DB.transaction() if DB is not None else contextlib.nullcontext()
            with context:
                sale = Sale.create(
                    invoice_no=invoice_no,
                    customer_id=self.selected_customer_id,
                    user_id=user_id,
                    subtotal_amount=subtotal,
                    discount_amount=self.discount_value,
                    total_amount=total,
                    payment_method=method,
                    payment_status="paid",
                )
                for item_id, qty in self.cart.items():
                    item = self._item_by_id(item_id)
                    if not item:
                        continue
                    price = float(item.sell_price or 0)
                    SaleDetail.create(
                        sale_id=sale.id,
                        item_id=item_id,
                        quantity=qty,
                        unit_price=price,
                        subtotal=price * qty,
                    )
                    item.update(stock=int(item.stock or 0) - qty)
        except Exception as exc:
            self._toast(f"Gagal menyimpan transaksi: {exc}", error=True)
            return

        self._show_receipt(invoice_no, total, paid, method)
        self._load_items()
        self._render_product_list(getattr(self.search_field, "value", ""))
        self.cart.clear()
        self.discount_value = 0.0
        self.paid_field.value = ""
        self.discount_field.value = "0"
        self._refresh_cart()
        self._toast(f"Transaksi {invoice_no} berhasil")

    def _show_receipt(self, invoice_no: str, total: float, paid: float, method: str) -> None:
        lines = [
            ft.Text(invoice_no, weight="bold", size=16),
            ft.Text(datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), size=11,
                    color=Colors.GREY_600),
            ft.Divider(),
        ]
        for item_id, qty in self.cart.items():
            item = self._item_by_id(item_id)
            if not item:
                continue
            price = float(item.sell_price or 0)
            lines.append(
                ft.Row(
                    [
                        ft.Text(f"{item.name} x{qty}", size=12, expand=True),
                        ft.Text(rupiah(price * qty), size=12),
                    ],
                    alignment="spaceBetween",
                )
            )
        lines += [
            ft.Divider(),
            ft.Row([ft.Text("Total", weight="bold"), ft.Text(rupiah(total), weight="bold")],
                   alignment="spaceBetween"),
            ft.Row([ft.Text(f"Bayar ({method})"), ft.Text(rupiah(paid))],
                   alignment="spaceBetween"),
            ft.Row([ft.Text("Kembalian"), ft.Text(rupiah(max(paid - total, 0)))]),
            ft.Row([ft.Text("Status"), ft.Text("LUNAS", color=Colors.GREEN_700,
                                               weight="bold")]),
        ]

        dialog = ft.AlertDialog(
            title=ft.Row([ft.Icon(Icons.RECEIPT, color=Colors.GREEN_600),
                          ft.Text("Struk Pembayaran")]),
            content=ft.Container(ft.Column(lines, spacing=6, tight=True), width=340),
            actions=[ft.TextButton("Tutup", on_click=lambda e: self._close_dialog(dialog))],
        )
        self._open_dialog(dialog)

    # =====================================================================
    # VIEW: PRODUK
    # =====================================================================
    def view_products(self) -> ft.Control:
        self._load_items()
        rows = []
        for item in self.items_cache:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item.sku or "-")),
                        ft.DataCell(ft.Text(item.name or "-")),
                        ft.DataCell(ft.Text(item.category or "-")),
                        ft.DataCell(ft.Text(rupiah(item.buy_price))),
                        ft.DataCell(ft.Text(rupiah(item.sell_price))),
                        ft.DataCell(ft.Text(f"{int(item.stock or 0)} {item.unit or ''}")),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(Icons.EDIT, icon_size=18,
                                                  on_click=lambda e, i=item: self._product_dialog(i)),
                                    ft.IconButton(Icons.DELETE_OUTLINE, icon_size=18,
                                                  icon_color=Colors.RED_400,
                                                  on_click=lambda e, i=item: self._delete_item(i)),
                                ],
                                spacing=0,
                            )
                        ),
                    ]
                )
            )

        table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(h)) for h in
                     ("SKU", "Nama", "Kategori", "H. Modal", "H. Jual", "Stok", "Aksi")],
            rows=rows,
            heading_row_color=Colors.GREY_100,
        )

        return self._card(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Master Produk", size=18, weight="bold", expand=True),
                            ft.ElevatedButton("Tambah Produk", icon=Icons.ADD,
                                              on_click=lambda e: self._product_dialog(None)),
                        ]
                    ),
                    ft.Divider(),
                    ft.Column([table], scroll="auto", expand=True),
                ],
                expand=True,
            ),
            expand=True,
        )

    def _product_dialog(self, item=None) -> None:
        fields = {
            "sku": ft.TextField(label="SKU / Barcode", value=getattr(item, "sku", "") or ""),
            "name": ft.TextField(label="Nama Produk", value=getattr(item, "name", "") or ""),
            "category": ft.TextField(label="Kategori", value=getattr(item, "category", "") or ""),
            "unit": ft.TextField(label="Satuan", value=getattr(item, "unit", "pcs") or "pcs"),
            "buy_price": ft.TextField(label="Harga Modal", value=str(int(item.buy_price or 0)) if item else "0"),
            "sell_price": ft.TextField(label="Harga Jual", value=str(int(item.sell_price or 0)) if item else "0"),
            "stock": ft.TextField(label="Stok", value=str(int(item.stock or 0)) if item else "0"),
        }

        def save(e):
            data = {k: v.value.strip() for k, v in fields.items()}
            if not data["sku"] or not data["name"]:
                self._toast("SKU dan nama produk wajib diisi", error=True)
                return
            payload = {
                "sku": data["sku"],
                "name": data["name"],
                "category": data["category"],
                "unit": data["unit"] or "pcs",
                "buy_price": to_number(data["buy_price"]),
                "sell_price": to_number(data["sell_price"]),
                "stock": int(to_number(data["stock"])),
            }
            try:
                if item is None:
                    Item.create(**payload)
                else:
                    item.update(**payload)
            except Exception as exc:
                self._toast(f"Gagal menyimpan produk: {exc}", error=True)
                return
            self._close_dialog(dialog)
            self._load_items()
            self.show_page(1)
            self._toast("Produk tersimpan")

        dialog = ft.AlertDialog(
            title=ft.Text("Tambah Produk" if item is None else "Edit Produk"),
            content=ft.Container(
                ft.Column(list(fields.values()), spacing=8, tight=True, scroll="auto"),
                width=380,
                height=460,
            ),
            actions=[
                ft.TextButton("Batal", on_click=lambda e: self._close_dialog(dialog)),
                ft.ElevatedButton("Simpan", on_click=save),
            ],
        )
        self._open_dialog(dialog)

    def _delete_item(self, item) -> None:
        try:
            item.delete()
        except Exception as exc:
            self._toast(f"Gagal menghapus: {exc}", error=True)
            return
        self._load_items()
        self.show_page(1)
        self._toast("Produk dihapus")

    # =====================================================================
    # VIEW: PELANGGAN
    # =====================================================================
    def view_customers(self) -> ft.Control:
        self._load_customers()
        self._refresh_customer_dropdown()
        rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(cust.full_name or "-")),
                    ft.DataCell(ft.Text(cust.company_name or "-")),
                    ft.DataCell(ft.Text(cust.phone_number or "-")),
                    ft.DataCell(ft.Text(cust.address or "-")),
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(Icons.EDIT, icon_size=18,
                                              on_click=lambda e, c=cust: self._customer_dialog(c)),
                                ft.IconButton(Icons.DELETE_OUTLINE, icon_size=18,
                                              icon_color=Colors.RED_400,
                                              on_click=lambda e, c=cust: self._delete_customer(c)),
                            ],
                            spacing=0,
                        )
                    ),
                ]
            )
            for cust in self.customers_cache
        ]

        table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(h)) for h in
                     ("Nama", "Perusahaan", "Telepon", "Alamat", "Aksi")],
            rows=rows,
            heading_row_color=Colors.GREY_100,
        )

        return self._card(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Data Pelanggan", size=18, weight="bold", expand=True),
                            ft.ElevatedButton("Tambah Pelanggan", icon=Icons.ADD,
                                              on_click=lambda e: self._customer_dialog(None)),
                        ]
                    ),
                    ft.Divider(),
                    ft.Column([table], scroll="auto", expand=True),
                ],
                expand=True,
            ),
            expand=True,
        )

    def _customer_dialog(self, customer=None) -> None:
        fields = {
            "full_name": ft.TextField(label="Nama Lengkap",
                                      value=getattr(customer, "full_name", "") or ""),
            "company_name": ft.TextField(label="Perusahaan",
                                         value=getattr(customer, "company_name", "") or ""),
            "phone_number": ft.TextField(label="No. Telepon",
                                         value=getattr(customer, "phone_number", "") or ""),
            "address": ft.TextField(label="Alamat", multiline=True, min_lines=2,
                                    value=getattr(customer, "address", "") or ""),
        }

        def save(e):
            payload = {k: v.value.strip() for k, v in fields.items()}
            if not payload["full_name"]:
                self._toast("Nama pelanggan wajib diisi", error=True)
                return
            try:
                if customer is None:
                    Customer.create(**payload)
                else:
                    customer.update(**payload)
            except Exception as exc:
                self._toast(f"Gagal menyimpan pelanggan: {exc}", error=True)
                return
            self._close_dialog(dialog)
            self.show_page(2)
            self._toast("Pelanggan tersimpan")

        dialog = ft.AlertDialog(
            title=ft.Text("Tambah Pelanggan" if customer is None else "Edit Pelanggan"),
            content=ft.Container(ft.Column(list(fields.values()), spacing=8, tight=True),
                                 width=360),
            actions=[
                ft.TextButton("Batal", on_click=lambda e: self._close_dialog(dialog)),
                ft.ElevatedButton("Simpan", on_click=save),
            ],
        )
        self._open_dialog(dialog)

    def _delete_customer(self, customer) -> None:
        try:
            customer.delete()
        except Exception as exc:
            self._toast(f"Gagal menghapus pelanggan: {exc}", error=True)
            return
        self.show_page(2)
        self._toast("Pelanggan dihapus")

    # =====================================================================
    # VIEW: RIWAYAT
    # =====================================================================
    def view_history(self) -> ft.Control:
        try:
            sales = list(Sale.order_by("id", "DESC").limit(100).get())
        except Exception as exc:
            sales = []
            print(f"[WARN] load sales: {exc}")

        rows = []
        for sale in sales:
            created = str(getattr(sale, "created_at", "") or "")
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(sale.invoice_no or "-")),
                        ft.DataCell(ft.Text(created[:16])),
                        ft.DataCell(ft.Text(sale.payment_method or "-")),
                        ft.DataCell(ft.Text(rupiah(sale.total_amount))),
                        ft.DataCell(ft.Text(sale.payment_status or "-")),
                        ft.DataCell(
                            ft.TextButton("Detail", icon=Icons.VISIBILITY,
                                          on_click=lambda e, s=sale: self._sale_detail(s))
                        ),
                    ]
                )
            )

        table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(h)) for h in
                     ("Invoice", "Tanggal", "Metode", "Total", "Status", "")],
            rows=rows,
            heading_row_color=Colors.GREY_100,
        )

        return self._card(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Riwayat Transaksi", size=18, weight="bold", expand=True),
                            ft.IconButton(Icons.REFRESH, on_click=lambda e: self.show_page(3)),
                        ]
                    ),
                    ft.Divider(),
                    ft.Column([table], scroll="auto", expand=True),
                ],
                expand=True,
            ),
            expand=True,
        )

    def _sale_detail(self, sale) -> None:
        lines = [
            ft.Text(sale.invoice_no or "-", weight="bold", size=15),
            ft.Text(f"Total: {rupiah(sale.total_amount)}  •  {sale.payment_method}",
                    size=12, color=Colors.GREY_700),
            ft.Divider(),
        ]
        try:
            details = list(sale.sale_details)
        except Exception:
            details = []
        for detail in details:
            try:
                name = detail.item.name if detail.item else f"item #{detail.item_id}"
            except Exception:
                name = f"item #{getattr(detail, 'item_id', '?')}"
            lines.append(
                ft.Row(
                    [
                        ft.Text(f"{name} x{detail.quantity}", size=12, expand=True),
                        ft.Text(rupiah(detail.subtotal), size=12),
                    ],
                    alignment="spaceBetween",
                )
            )
        if not details:
            lines.append(ft.Text("Tidak ada detail.", size=12, color=Colors.GREY_600))

        dialog = ft.AlertDialog(
            title=ft.Text("Detail Transaksi"),
            content=ft.Container(ft.Column(lines, spacing=6, tight=True, scroll="auto"),
                                 width=360, height=400),
            actions=[ft.TextButton("Tutup", on_click=lambda e: self._close_dialog(dialog))],
        )
        self._open_dialog(dialog)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main_window(page: ft.Page) -> None:
    """Fungsi target `ft.app(target=main_window)`."""
    ensure_database()
    window = MainWindow(page)
    page.add(window.build())
    page.update()


if __name__ == "__main__":
    try:
        ft.app(target=main_window)
    except AttributeError:  # Flet 0.3x
        ft.run(main_window)
