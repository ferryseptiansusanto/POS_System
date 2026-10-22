# migrate.py
import os
from orm.database_manager import DatabaseManager

def run_migration():
    db_file = "app.db"

    # Hapus file database lama jika ingin reset bersih dari awal
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"[INFO] Database lama '{db_file}' dihapus.")

    # Ambil koneksi (otomatis membuat file app.db baru)
    conn = DatabaseManager.get_connection("default")
    cursor = conn.cursor()

    print("[INFO] Membuat tabel-tabel database...")

    # Path ke file SQL yang berisi DDL
    sql_file = os.path.join(os.path.dirname(__file__), "database.sql")

    # Baca seluruh isi file SQL
    with open(sql_file, "r", encoding="utf-8") as f:
        sql_script = f.read()

    # Jalankan seluruh script SQL (mendukung banyak statement)
    cursor.executescript(sql_script)

    conn.commit()
    print("[OK] Migrasi tabel berhasil! Database 'app.db' siap digunakan.")


if __name__ == "__main__":
    run_migration()
