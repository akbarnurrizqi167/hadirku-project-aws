import os
import cv2
import face_recognition
import numpy as np
import pickle # Untuk menyimpan dan memuat encoding jika Anda tetap ingin file
import boto3 # Untuk interaksi dengan AWS S3
from botocore.exceptions import NoCredentialsError, ClientError

# --- Ambil konfigurasi S3 dari app ---
# Pastikan app sudah terimport atau dilewatkan sebagai parameter
# Jika app diimport, pastikan lingkaran impor tidak terjadi.
# Cara terbaik adalah meneruskan config S3 atau inisialisasi client di sini
# atau mengambil dari environment variables langsung.
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
S3_REGION = os.environ.get('S3_REGION', 'ap-southeast-1') # Default region
# Inisialisasi klien S3. Jika Anda menggunakan IAM Role di EC2, kredensial tidak perlu diset di kode.
# Jika tidak, Anda perlu: aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
s3_client = boto3.client('s3', region_name=S3_REGION)

# --- Fungsi untuk mengunggah file ke S3 ---
def upload_file_to_s3(file_path, s3_object_key):
    """
    Mengunggah file dari path lokal ke bucket S3.
    Mengembalikan URL publik S3 jika berhasil, None jika gagal.
    """
    try:
        s3_client.upload_file(file_path, S3_BUCKET_NAME, s3_object_key)
        # Bentuk URL publik S3
        s3_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{s3_object_key}"
        print(f"File {file_path} berhasil diunggah ke {s3_url}")
        return s3_url
    except FileNotFoundError:
        print(f"Error: File '{file_path}' tidak ditemukan.")
        return None
    except NoCredentialsError:
        print("Error: Kredensial AWS tidak ditemukan.")
        return None
    except ClientError as e:
        print(f"Error S3 client: {e}")
        return None
    except Exception as e:
        print(f"Error tak terduga saat mengunggah ke S3: {e}")
        return None

# --- Fungsi untuk mendownload file dari S3 ---
def download_file_from_s3(s3_object_key, local_path):
    """
    Mendownload file dari bucket S3 ke path lokal sementara.
    Mengembalikan True jika berhasil, False jika gagal.
    """
    try:
        s3_client.download_file(S3_BUCKET_NAME, s3_object_key, local_path)
        print(f"File {s3_object_key} berhasil diunduh ke {local_path}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"Error: Objek S3 '{s3_object_key}' tidak ditemukan.")
        else:
            print(f"Error S3 client saat mengunduh: {e}")
        return False
    except NoCredentialsError:
        print("Error: Kredensial AWS tidak ditemukan.")
        return False
    except Exception as e:
        print(f"Error tak terduga saat mengunduh dari S3: {e}")
        return False

# --- Fungsi Utama untuk Mendapatkan Encoding dari Gambar ---
def get_face_encoding(image_path):
    """
    Mengambil encoding wajah dari sebuah gambar.
    image_path bisa berupa path lokal (jika sudah diunduh) atau URL/data stream.
    Untuk deployment S3, Anda mungkin perlu mengunduh sementara atau memproses stream.
    """
    try:
        # Jika image_path adalah URL S3, Anda perlu mendownloadnya terlebih dahulu
        # Atau jika Anda mengunggah bytes langsung, gunakan bytes langsung
        if image_path.startswith("https://") and "s3.amazonaws.com" in image_path:
            # Ekstrak object_key dari URL S3
            s3_object_key = '/'.join(image_path.split('/')[3:]) # Dapatkan path setelah bucket
            temp_local_path = os.path.join('/tmp', os.path.basename(s3_object_key))
            if not download_file_from_s3(s3_object_key, temp_local_path):
                print(f"Gagal mengunduh gambar wajah dari S3: {image_path}")
                return None
            image = cv2.imread(temp_local_path)
            os.remove(temp_local_path) # Hapus file sementara
        else:
            # Asumsi image_path adalah path lokal
            image = cv2.imread(image_path)

        if image is None:
            print(f"Error: Tidak dapat membaca gambar dari {image_path}")
            return None

        # Konversi gambar dari BGR (OpenCV) ke RGB (face_recognition)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Temukan semua wajah dalam gambar
        face_locations = face_recognition.face_locations(rgb_image)
        
        if len(face_locations) == 0:
            print("Tidak ada wajah yang terdeteksi dalam gambar.")
            return None
        
        # Ambil encoding wajah pertama (asumsi satu wajah per gambar registrasi)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        return face_encodings[0] # Mengembalikan encoding wajah pertama

    except Exception as e:
        print(f"Error saat mendapatkan encoding wajah: {e}")
        return None

# --- Fungsi untuk Menyimpan Encoding Wajah (Setelah Didapat) ---
# Anda akan memanggil ini setelah Anda mendapatkan encoding dari gambar yang diunggah
# Data_encoding akan menjadi numpy array. Anda bisa menyimpannya sebagai binary (pickle) di S3 atau di DB.
# Jika disimpan di DB, ini tidak perlu ke S3 secara langsung.
def save_face_encoding_file(face_encoding, filename):
    """
    Menyimpan encoding wajah ke file lokal sementara, lalu mengunggahnya ke S3.
    """
    if face_encoding is None:
        return None
    
    temp_local_path = os.path.join('/tmp', filename)
    with open(temp_local_path, 'wb') as f:
        pickle.dump(face_encoding, f)
    
    s3_object_key = f"face_encodings/{filename}" # Contoh path di S3
    s3_url = upload_file_to_s3(temp_local_path, s3_object_key)
    os.remove(temp_local_path) # Hapus file sementara
    return s3_url

# --- Fungsi untuk Memuat Semua Encoding yang Tersimpan dari S3 (untuk perbandingan) ---
# Ini adalah bagian kritis untuk deteksi kehadiran.
# Anda perlu memuat semua encoding yang sudah terdaftar.
# Jika encoding disimpan di DB, Anda query dari DB. Jika di S3, Anda list semua objek.
def load_all_known_face_encodings_from_s3():
    """
    Memuat semua encoding wajah yang diketahui dari bucket S3.
    Mengembalikan dictionary {student_id: encoding_array}.
    """
    known_encodings = []
    known_student_ids = [] # Atau nama siswa
    
    # Cara yang lebih efisien: Ambil S3 URLs dari database Anda
    # Lalu download encoding-encoding tersebut satu per satu atau secara batch
    from models import FaceData # Import model FaceData
    all_face_data = FaceData.query.all() # Asumsi ini mengambil data wajah dari DB
    
    for face_data_entry in all_face_data:
        s3_url = face_data_entry.face_image_s3_url
        # Ekstrak object_key dari URL S3
        s3_object_key = '/'.join(s3_url.split('/')[3:])
        
        temp_encoding_path = os.path.join('/tmp', os.path.basename(s3_object_key))
        if download_file_from_s3(s3_object_key, temp_encoding_path):
            with open(temp_encoding_path, 'rb') as f:
                encoding = pickle.load(f)
            known_encodings.append(encoding)
            known_student_ids.append(face_data_entry.student_id) # Atau ID/nama yang sesuai
            os.remove(temp_encoding_path) # Hapus file sementara
        else:
            print(f"Gagal memuat encoding dari S3: {s3_url}")

    return known_encodings, known_student_ids

# --- Fungsi Verifikasi Wajah ---
def verify_face(current_face_encoding, known_face_encodings, tolerance=0.6):
    """
    Membandingkan encoding wajah saat ini dengan encoding yang diketahui.
    Mengembalikan True jika cocok, False jika tidak.
    """
    if not known_face_encodings:
        return False, None # Tidak ada encoding yang diketahui untuk dibandingkan

    # Bandingkan encoding wajah saat ini dengan semua encoding yang diketahui
    matches = face_recognition.compare_faces(known_face_encodings, current_face_encoding, tolerance)
    
    # Ambil jarak wajah (semakin kecil semakin mirip)
    face_distances = face_recognition.face_distance(known_face_encodings, current_face_encoding)
    
    best_match_index = np.argmin(face_distances) if len(face_distances) > 0 else -1

    if best_match_index != -1 and matches[best_match_index]:
        return True, best_match_index
    else:
        return False, None

# --- Fungsi untuk memproses gambar dari kamera/upload ---
def process_uploaded_image_for_recognition(image_file):
    """
    Menerima FileStorage object, menyimpan sementara, dan mengembalikan encoding.
    """
    temp_path = os.path.join('/tmp', image_file.filename)
    image_file.save(temp_path) # Simpan sementara file yang diupload

    encoding = get_face_encoding(temp_path)
    os.remove(temp_path) # Hapus file sementara
    return encoding