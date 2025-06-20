# Contoh Rute Registrasi Wajah
# Asumsi Anda mengimport db dan FaceData dari app dan models
from flask import request, redirect, url_for, flash, Blueprint
from flask_login import login_required, current_user # Jika menggunakan Flask-Login
from werkzeug.utils import secure_filename # Untuk nama file yang aman
from app import db # Asumsi db dari app.py
from models import Student, FaceData # Asumsi model Anda
from face_utils import get_face_encoding, upload_file_to_s3, save_face_encoding_file # Import fungsi S3

# Ini contoh blueprint, sesuaikan dengan struktur Anda
main = Blueprint('main', __name__) # Contoh jika ini di main.py

@main.route('/register_face', methods=['GET', 'POST'])
@login_required # Hanya user yang login bisa register
def register_face():
    if request.method == 'POST':
        if 'face_image' not in request.files:
            flash('Tidak ada file gambar yang diunggah.')
            return redirect(request.url)
        
        file = request.files['face_image']
        if file.filename == '':
            flash('Tidak ada file yang dipilih.')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            # --- Langkah 1: Simpan file sementara di server untuk diproses ---
            temp_filepath = os.path.join('/tmp', filename)
            file.save(temp_filepath)

            # --- Langkah 2: Dapatkan encoding wajah ---
            face_encoding = get_face_encoding(temp_filepath)
            
            # Hapus file sementara setelah mendapatkan encoding
            os.remove(temp_filepath) 

            if face_encoding is None:
                flash('Tidak dapat mendeteksi wajah atau encoding.')
                return redirect(request.url)
            
            # --- Langkah 3: Unggah gambar asli ke S3 ---
            s3_object_key_image = f"student_faces/{current_user.id}/{filename}" # Path di S3
            s3_image_url = upload_file_to_s3(temp_filepath, s3_object_key_image) # Gunakan path temp yang disimpan sebelumnya
            
            if not s3_image_url:
                flash('Gagal mengunggah gambar wajah ke S3.')
                return redirect(request.url)

            # --- Langkah 4 (Opsional): Unggah encoding ke S3 jika Anda menyimpannya sebagai file ---
            # Jika Anda menyimpan encoding sebagai binary/PickleType di DB (lebih disarankan):
            # face_encoding_binary = pickle.dumps(face_encoding)
            # Jika Anda menyimpannya di S3 sebagai file encoding:
            encoding_filename = f"{os.path.splitext(filename)[0]}.pkl"
            s3_object_key_encoding = f"student_face_encodings/{current_user.id}/{encoding_filename}"
            s3_encoding_url = save_face_encoding_file(face_encoding, encoding_filename)

            # --- Langkah 5: Simpan URL S3 (dan encoding jika di DB) ke database ---
            # Asumsi user yang login adalah Student atau kita bisa cari Student berdasarkan User ID
            student = Student.query.filter_by(student_id=current_user.username).first() # Contoh, sesuaikan
            if student:
                new_face_data = FaceData(
                    student_id=student.id,
                    face_image_s3_url=s3_image_url,
                    # face_encoding = face_encoding_binary # Jika disimpan di DB
                )
                db.session.add(new_face_data)
                db.session.commit()
                flash('Wajah berhasil didaftarkan!')
                return redirect(url_for('main.dashboard')) # Atau halaman lain
            else:
                flash('Siswa tidak ditemukan untuk pendaftaran wajah.')

    return render_template('register_face.html') # Sesuaikan dengan template Anda