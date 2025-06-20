from app import db # Pastikan ini mengimpor instance 'db' dari app.py Anda
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # Anda mungkin punya kolom role atau is_admin
    is_admin = db.Column(db.Boolean, default=False)
    # Tambahan untuk Flask-Login
    def is_active(self): return True
    def is_authenticated(self): return True
    def is_anonymous(self): return False
    def get_id(self): return str(self.id)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=False) # NISN/NIM
    # Satu siswa bisa punya banyak data wajah
    faces = db.relationship('FaceData', backref='owner_student', lazy=True)
    attendances = db.relationship('Attendance', backref='student_attendee', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    attendances = db.relationship('Attendance', backref='course_attended', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # Anda mungkin punya status kehadiran (hadir, absen, dll)
    status = db.Column(db.String(20), default='Hadir')

class FaceData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    # --- PENTING: Ganti cara penyimpanan path gambar wajah ---
    # Sekarang simpan URL S3, bukan path lokal
    face_image_s3_url = db.Column(db.String(500), nullable=False) # URL S3 bisa cukup panjang
    # Anda juga bisa menyimpan face_encoding di sini jika ukurannya tidak terlalu besar
    # face_encoding = db.Column(db.PickleType, nullable=False) # Contoh menyimpan encoding sebagai binary/pickle
    
    # Menghubungkan ke objek student untuk akses mudah
    student = db.relationship('Student', backref='face_data', uselist=False)

    def __repr__(self):
        return f"<FaceData {self.face_image_s3_url}>"