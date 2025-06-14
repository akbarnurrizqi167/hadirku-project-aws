import face_recognition
import numpy as np
import pickle
from models import User

def generate_encoding_from_image(image_rgb):
    """
    Menghasilkan satu face encoding dari sebuah gambar (format RGB).
    Mengembalikan None jika tidak ada wajah atau ada lebih dari satu wajah.
    """
    # Deteksi lokasi wajah dalam gambar
    face_locations = face_recognition.face_locations(image_rgb)

    # Validasi: Pastikan hanya ada SATU wajah untuk pendaftaran
    if len(face_locations) != 1:
        return None

    # Hasilkan encoding dari wajah yang ditemukan
    # Ambil encoding pertama (dan satu-satunya)
    face_encodings = face_recognition.face_encodings(image_rgb, known_face_locations=face_locations)
    
    return face_encodings[0]

def find_match_in_db(unknown_image_rgb):
    """
    Mencari kecocokan wajah dari gambar dengan semua encoding yang ada di database.
    Mengembalikan ID user yang cocok atau None.
    """
    # Ambil semua pengguna yang sudah punya data encoding wajah
    users_with_faces = User.query.filter(User.face_encoding.isnot(None)).all()
    if not users_with_faces:
        return None, "Database wajah kosong. Tidak ada referensi untuk perbandingan."

    # Siapkan data untuk perbandingan
    known_encodings = [pickle.loads(user.face_encoding) for user in users_with_faces]
    known_user_ids = [user.id for user in users_with_faces]

    # Deteksi semua wajah di gambar dari webcam
    unknown_face_locations = face_recognition.face_locations(unknown_image_rgb)
    if not unknown_face_locations:
        return None, "Tidak ada wajah terdeteksi di kamera."
        
    unknown_face_encodings = face_recognition.face_encodings(unknown_image_rgb, known_face_locations=unknown_face_locations)

    # Bandingkan setiap wajah yang ditemukan dengan database
    for unknown_encoding in unknown_face_encodings:
        # Fungsi compare_faces mengembalikan list [True, False, True, ...]
        matches = face_recognition.compare_faces(known_encodings, unknown_encoding, tolerance=0.5)
        
        # Cari indeks pertama yang cocok (bernilai True)
        if True in matches:
            first_match_index = matches.index(True)
            matched_user_id = known_user_ids[first_match_index]
            return matched_user_id, "Wajah dikenali."
            
    return None, "Wajah tidak dikenali di dalam database."