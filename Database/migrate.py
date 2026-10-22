# migrate.py
import os
from orm.database_manager import DatabaseManager
# migrate.py

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

    cursor.execute("""

    """)

    conn.commit()
    print("[OK] Migrasi tabel berhasil! Database 'app.db' siap digunakan.")



if __name__ == "__main__":
    run_migration()