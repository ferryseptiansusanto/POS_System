# config.py (Berada di main folder)
import os

# Menemukan path absolut dari folder utama (POS_System)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path absolut menuju lokasi file database dan hasil models.py
DATABASE_PATH = os.path.join(BASE_DIR, "database", "app.db")
MODELS_OUTPUT_PATH = os.path.join(BASE_DIR, "model", "models.py")

# Konfigurasi database untuk digunakan oleh DatabaseManager atau ORMGenerator
DATABASES = {
    "default": {
        "provider": "sqlite",
        "database_url": DATABASE_PATH
    }
}
