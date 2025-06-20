import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager # Asumsi Hadirku menggunakan Flask-Login

# --- Inisialisasi Aplikasi Flask ---
app = Flask(__name__)

# --- Konfigurasi Aplikasi ---
# SECRET_KEY harus diambil dari environment variable untuk keamanan di produksi
# Berikan nilai default yang kuat untuk pengembangan lokal jika diperlukan,
# tapi PASTIKAN environment variable diset di AWS.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sekret_kunci_sangat_rahasia_dan_panjang_sekali_ini_ubah_ya')

# DATABASE_URL akan diambil dari environment variable (dari AWS RDS)
# Contoh format PostgreSQL: 'postgresql://user:password@hostname:port/dbname'
# Contoh format MySQL: 'mysql+pymysql://user:password@hostname:port/dbname'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

# Nonaktifkan pelacakan modifikasi SQLAlchemy yang tidak perlu (menghemat memori)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Konfigurasi S3 untuk penyimpanan gambar wajah
# Pastikan ENVIRONMENT VARIABLES ini juga diset di EC2
app.config['S3_BUCKET_NAME'] = os.environ.get('S3_BUCKET_NAME')
app.config['AWS_ACCESS_KEY_ID'] = os.environ.get('AWS_ACCESS_KEY_ID') # Lebih baik gunakan IAM Role
app.config['AWS_SECRET_ACCESS_KEY'] = os.environ.get('AWS_SECRET_ACCESS_KEY') # Lebih baik gunakan IAM Role
# Region S3 Anda, contoh: ap-southeast-1 (Jakarta)
app.config['S3_REGION'] = os.environ.get('S3_REGION', 'ap-southeast-1') # Ubah sesuai region S3 Anda


# --- Inisialisasi Ekstensi Flask ---
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app) # Jika Hadirku menggunakan Flask-Login
login_manager.login_view = 'auth.login' # Ubah sesuai nama blueprint login Anda

# Import dan daftarkan Blueprint Anda
from auth import auth as auth_blueprint # Asumsi Anda punya blueprint bernama 'auth' di auth.py
from main import main as main_blueprint # Asumsi Anda punya blueprint bernama 'main' di main.py
# from admin import admin as admin_blueprint # Jika ada blueprint admin terpisah

app.register_blueprint(auth_blueprint)
app.register_blueprint(main_blueprint)
# app.register_blueprint(admin_blueprint, url_prefix='/admin') # Contoh dengan prefix

# --- Import models Anda di sini setelah 'db' diinisialisasi ---
from models import User, Student, Course, Attendance, FaceData # Pastikan ini diimport

# Tambahan: handler untuk user_loader Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # Asumsi User adalah model yang merepresentasikan user untuk login
    return User.query.get(int(user_id))

# Anda mungkin perlu menambahkan rute atau error handler di sini jika ada
# Contoh:
# @app.errorhandler(404)
# def not_found_error(error):
#     return "<h1>404 Not Found</h1>", 404

# Jika Anda memiliki fungsi main() di dalam app.py untuk menjalankan server development
if __name__ == '__main__':
    # HANYA untuk development, jangan gunakan di produksi!
    with app.app_context():
        db.create_all() # Buat tabel jika belum ada (gunakan Flask-Migrate untuk produksi!)
    app.run(debug=True, host='0.0.0.0', port=5000)