import os
import base64
import pickle
from datetime import date, datetime
import numpy as np
import cv2
import pytz

from flask import Blueprint, render_template, jsonify, request, current_app, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload

from models import db, User, MataKuliah, AttendanceRecord
from face_utils import generate_encoding_from_image, find_match_in_db

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    if current_user.is_admin:
        return redirect(url_for('admin.index'))
    else:
        # Cek apakah pengguna sudah mendaftarkan wajah (punya encoding)
        if current_user.face_encoding is None:
            flash('Anda belum mendaftarkan wajah. Silakan selesaikan pendaftaran.', 'warning')
            return redirect(url_for('main.register_face'))
        
        courses = MataKuliah.query.order_by(MataKuliah.nama_mk).all()
        return render_template('index.html', name=current_user.name, courses=courses)


@main.route('/records')
@login_required
def records():
    if current_user.is_admin:
        return redirect(url_for('admin.index'))

    wib = pytz.timezone('Asia/Jakarta')
    user_records = AttendanceRecord.query.options(
        joinedload(AttendanceRecord.matakuliah)
    ).filter_by(user_id=current_user.id).order_by(AttendanceRecord.timestamp.desc()).all()

    for record in user_records:
        record.local_time = record.timestamp.replace(tzinfo=pytz.utc).astimezone(wib)
        
    return render_template('records.html', records=user_records, name=current_user.name)


@main.route('/mark_attendance', methods=['POST'])
@login_required
def mark_attendance():
    data = request.get_json()
    if not all(k in data for k in ['image_data', 'location', 'matakuliah_id']):
        return jsonify({'status': 'error', 'message': 'Permintaan tidak lengkap.'}), 400

    # Cek absensi duplikat
    today = date.today()
    if AttendanceRecord.query.filter(
        AttendanceRecord.user_id == current_user.id,
        AttendanceRecord.matakuliah_id == data['matakuliah_id'],
        db.func.date(AttendanceRecord.timestamp) == today
    ).first():
        return jsonify({'status': 'warning', 'message': 'Anda sudah presensi untuk mata kuliah ini hari ini.'})

    # Decode gambar dan konversi ke RGB
    try:
        image_data = data['image_data'].split(',')[1]
        img_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Format data gambar tidak valid: {e}'})

    # Panggil fungsi pencocokan dari face_utils
    matched_user_id, message = find_match_in_db(rgb_frame)

    if matched_user_id == current_user.id:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"{current_user.name}_{timestamp_str}.jpg"
        full_image_path = os.path.join(current_app.static_folder, 'captures', image_filename)
        cv2.imwrite(full_image_path, frame)
        
        new_record = AttendanceRecord(
            user_id=current_user.id,
            matakuliah_id=data['matakuliah_id'],
            latitude=data['location'].get('latitude'),
            longitude=data['location'].get('longitude'),
            image_path=f"captures/{image_filename}"
        )
        db.session.add(new_record)
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'Presensi untuk {current_user.name} berhasil!'})
    
    elif matched_user_id is not None:
        matched_user = User.query.get(matched_user_id)
        return jsonify({'status': 'error', 'message': f'Wajah terdeteksi sebagai {matched_user.name}, bukan {current_user.name}.'})
    else:
        return jsonify({'status': 'error', 'message': message})


@main.route('/register_face')
@login_required
def register_face():
    return render_template('register_face.html')


@main.route('/save_face', methods=['POST'])
@login_required
def save_face():
    data = request.get_json()
    if 'image_data' not in data:
        return jsonify({'status': 'error', 'message': 'Data gambar tidak ditemukan.'})

    try:
        image_data = data['image_data'].split(',')[1]
        img_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except Exception:
        return jsonify({'status': 'error', 'message': 'Format data gambar tidak valid.'})

    encoding = generate_encoding_from_image(rgb_frame)
    
    if encoding is None:
        return jsonify({'status': 'error', 'message': 'Gagal memproses wajah. Pastikan hanya ada SATU wajah di foto dan terlihat jelas.'})

    user = User.query.get(current_user.id)
    user.face_encoding = pickle.dumps(encoding)
    db.session.commit()

    flash("Wajah Anda berhasil didaftarkan!", "success")
    return jsonify({'status': 'success', 'message': 'Wajah berhasil didaftarkan! Anda akan diarahkan ke halaman utama.'})