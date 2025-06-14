from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Inisialisasi db di sini
db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    
    # Kolom untuk menyimpan data encoding wajah (vektor 128-dimensi)
    face_encoding = db.Column(db.LargeBinary, nullable=True)
    
    records = db.relationship('AttendanceRecord', back_populates='user', lazy='dynamic')

class MataKuliah(db.Model):
    __tablename__ = 'mata_kuliah'
    id = db.Column(db.Integer, primary_key=True)
    kode_mk = db.Column(db.String(20), unique=True, nullable=False)
    nama_mk = db.Column(db.String(100), nullable=False)
    dosen_pengampu = db.Column(db.String(100), nullable=False)
    records = db.relationship('AttendanceRecord', back_populates='matakuliah', lazy='dynamic')

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_record'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    matakuliah_id = db.Column(db.Integer, db.ForeignKey('mata_kuliah.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    location = db.Column(db.String(200), nullable=True)
    image_path = db.Column(db.String(200), nullable=False)

    user = db.relationship('User', back_populates='records')
    matakuliah = db.relationship('MataKuliah', back_populates='records')