# FLET 1.0.0+ BREAKING CHANGES & MIGRATION CHEATSHEET

**PERHATIAN UNTUK AI:** Jika Anda membaca file ini, Anda WAJIB mematuhi seluruh aturan penggantian sintaks di bawah ini saat menulis kode Flet. Pembaruan 1.0.0 adalah perombakan besar. Seluruh sintaks lawas dan API *deprecated* dari versi 0.x telah DIHAPUS TANPA SISA dan akan menyebabkan CRASH.

## 1. PEMISAHAN PAGE PROPERTIES MENJADI STANDALONE SERVICES
Fitur non-visual yang dulunya menempel di `page` kini telah dipisah menjadi *Class* Service mandiri yang harus diinisialisasi secara terpisah. **DILARANG** memanggilnya dari `page`.
* `page.browser_context_menu` ➡️ GUNAKAN: `ft.BrowserContextMenu()`
* `page.clipboard` ➡️ GUNAKAN: `ft.Clipboard()`
* `page.shared_preferences` ➡️ GUNAKAN: `ft.SharedPreferences()`
* `page.storage_paths` ➡️ GUNAKAN: `ft.StoragePaths()`
* `page.launch_url()` / `can_launch_url()` / `close_in_app_web_view()` / `page.url_launcher` ➡️ GUNAKAN: `ft.UrlLauncher().launch_url(...)`

## 2. PENGHAPUSAN API DEPRECATED PADA KONTROL & TIPE DATA
Semua API lawas di bawah ini telah dihapus. Anda wajib menggunakan sintaks penggantinya:
| Dihapus / Lawas (JANGAN DIPAKAI) | Pengganti v1.x (GUNAKAN INI) |
| :--- | :--- |
| `ft.ElevatedButton` | `ft.Button` |
| `ft.ConstrainedControl` | `ft.LayoutControl` |
| `DragTargetEvent.x` / `.y` | `DragTargetEvent.local_position` |
| `DragTargetEvent.offset` | `DragTargetEvent.global_position` |
| `Video.show_controls` | Set `Video.controls = None` |
| `Video.playlist_add()` / `remove()` | Mutasi list langsung (misal: `Video.playlist.append()`) |
| `ft.colors.black12`, `ft.Colors.WHITE70` | Gunakan underscore: `ft.Colors.BLACK_12`, `ft.Colors.WHITE_70` |

*(Catatan Pengecualian: `DropdownM2` TIDAK dihapus. Peringatan deprecation-nya dicabut dan komponen ini tetap didukung penuh).*

## 3. INPUTBORDER (HIERARKI CLASS)
Border sekarang adalah **Class (instansiasi)**, BUKAN Enum.
* Gunakan `ft.OutlineInputBorder()` ➡️ (DILARANG: `ft.InputBorder.OUTLINE`).
* Gunakan `ft.UnderlineInputBorder()` ➡️ (DILARANG: `ft.InputBorder.UNDERLINE`).
* Gunakan `ft.NoInputBorder()` ➡️ (DILARANG: `ft.InputBorder.NONE`).

## 4. APLIKASI DAN ROUTING (PAGE)
* **Inisialisasi:** Gunakan `ft.run(main)` atau `ft.run_async(main)`. **DILARANG** menggunakan `ft.app(target=main)`.
* **Routing/Navigasi:** Gunakan `page.push_route("/path")`. **DILARANG** menggunakan `page.go()`.
* **Startup Screen:** API `FletApp.show_app_startup_screen` & `app_startup_screen_message` diganti dengan `FletApp.boot_screen_options`.

## 5. PERUBAHAN ARSITEKTUR KOMPONEN BARU
* **Tabs:** `ft.Tabs` tidak lagi menerima list tab langsung. Anda WAJIB menggunakan `ft.TabBar` (dengan parameter `tabs=[ft.Tab(label="...")]`), lalu memasukkannya ke dalam `ft.Tabs(content=nama_tab_bar)`. DILARANG menggunakan parameter `text` pada `ft.Tab`.
* **Visual Density:** Gunakan `ft.VisualDensity` (BUKAN `ft.ThemeVisualDensity`).
* **Kapitalisasi Enum:** Selalu gunakan UPPERCASE untuk Enum (contoh: `ft.Alignment.TOP_CENTER`, bukan `ft.alignment.top_center`).

## 6. SIKLUS HIDUP & ASYNC (LIFECYCLE)
* **RuntimeError pada Update:** Flet secara otomatis memanggil `update()` di akhir berjalannya event handler. DILARANG KERAS memanggil `self.update()` di dalam fungsi `__init__` sebelum komponen fisik ditambahkan ke layar (`page.add()`). Selalu bungkus update mandiri dengan `try: self.update() except RuntimeError: pass`.
* **Single-Thread UI:** Flet 1.0 berjalan pada model single-thread. Jangan gunakan pemblokiran sinkron seperti `time.sleep()`. Gunakan `async def` dan `await asyncio.sleep()`.

## 7. PENGATURAN LAINNYA & KONFIGURASI iOS
* **iOS Signing (Per-Method vs Global):** Pengaturan *signing* yang ditulis spesifik untuk sebuah *method* ekspor di file konfigurasi (misal `[tool.flet.ios.export_methods.app-store-connect]`) kini akan menimpa (*override*) pengaturan global di `[tool.flet.ios]`.
* **CLI Clean Cache:** Gunakan command mandiri `flet clean` (bukan `flet build --clear-cache`).
* **State-key Kosong:** String kosong `""` untuk tipe state diganti menjadi `"default"` atau `ft.ControlState.DEFAULT`.