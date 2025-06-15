from app import create_app, db
from models import User
from werkzeug.security import generate_password_hash
import getpass
import os

def create_admin_user():
    """
    Script command-line untuk membuat pengguna admin baru.
    """
    app = create_app()
    with app.app_context():
        print("--- Membuat Akun Admin Baru ---")
        
        # Minta input nama
        while True:
            name = input("Masukkan Nama Lengkap Admin: ").strip()
            if not name:
                print("Nama tidak boleh kosong.")
            elif User.query.filter_by(name=name).first():
                print("Nama tersebut sudah terdaftar. Silakan gunakan nama lain.")
            else:
                break
        
        # Minta input password dengan konfirmasi
        while True:
            password = getpass.getpass("Masukkan Password: ")
            if not password:
                print("Password tidak boleh kosong.")
                continue
            confirm_password = getpass.getpass("Konfirmasi Password: ")
            if password == confirm_password:
                break
            else:
                print("Password tidak cocok. Silakan coba lagi.")

        # Buat user baru dengan flag is_admin = True
        new_admin = User(
            name=name,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            is_admin=True  # Langsung set sebagai admin
        )

        db.session.add(new_admin)
        db.session.commit()
        
        print(f"\nAkun admin '{name}' berhasil dibuat!")

if __name__ == '__main__':
    create_admin_user()
