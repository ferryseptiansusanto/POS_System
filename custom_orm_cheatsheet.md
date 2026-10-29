# CUSTOM ORM (ELOQUENT-STYLE) CHEATSHEET

**CRITICAL RULE:** DILARANG KERAS menggunakan kueri SQL mentah (`cursor.execute()`) di aplikasi utama. Selalu gunakan Custom ORM bawaan project.

## 1. MULTI-DATABASE & DYNAMIC SWITCHING
*   Dukung perpindahan koneksi dinamis via method `.from_connection()`.
*   Contoh: `User.from_connection("pg_connection").all()`

## 2. OPERASI CRUD & MASS ASSIGNMENT
*   Gunakan operasi instan: `Model.create(**kwargs)`, `Model.find(id)`, `model_instance.save()`, `model_instance.update()`, dan `model_instance.delete()`.
*   **Proteksi:** Patuhi atribut `fillable = [...]` pada class model untuk menghindari celah *Mass Assignment*.

## 3. DIRTY TRACKING
*   Fitur `get_dirty()` otomatis bekerja di belakang layar. Pastikan pemanggilan `.save()` atau `.update()` hanya mengeksekusi *query* `UPDATE` pada kolom yang benar-benar mengalami perubahan nilai.

## 4. MANAJEMEN TRANSAKSI
*   Setiap operasi beruntun (lebih dari 1 query) WAJIB menggunakan Context Manager. Otomatis *commit* jika sukses, *rollback* jika ada exception.
```python
with DB.transaction():
    # operasi db di sini
```

## 5. FLUENT QUERY BUILDER & PAGINATION
*   Gunakan method chaining (`snake_case` / `camelCase`): `.select()`, `.where()`, `.order_by()`, `.limit()`.
*   **Pagination:** Gunakan `.paginate(per_page=15, page=1)`. Ini akan mengembalikan dictionary berisi data dan metadata (`data`, `current_page`, `last_page`, `total`).

## 6. RELASI & ANTI N+1 (EAGER LOADING)
*   **Definisi Relasi:** Gunakan `has_many`, `belongs_to`, `belongs_to_many` (dengan fitur `.attach()`, `.detach()`, `.sync()`), serta polymorphic `morph_many` / `morph_to`.
*   **Eager Loading:** Untuk mencegah masalah N+1 Query, WAJIB memanggil `.with_relations()` atau `.with_("nama_relasi")` saat meload relasi.

## 7. LIFECYCLE, TIMESTAMPS & SOFT DELETES
*   Gunakan otomatisasi `created_at` dan `updated_at`.
*   Untuk tabel Soft Deletes, gunakan modifier query: `.with_trashed()`, `.only_trashed()`, `.restore()`, atau `.force_delete()`.

## 8. TRANSFORMASI & OBSERVERS
*   **Accessors & Mutators:** Gunakan format `get_<attr>_attribute` dan `set_<attr>_attribute` untuk memodifikasi format data saat masuk/keluar.
*   **Query Scopes:** Gunakan prefix `scope_<nama>()` untuk logika kueri spesifik yang sering dipakai.
*   **Observers:** Pisahkan *lifecycle hooks* (seperti aksi sebelum simpan/setelah simpan) ke kelas *Observer* tersendiri agar model tetap bersih.