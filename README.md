
---

# 🎓 **Hadirku** — Sistem Presensi Mahasiswa Berbasis Face Recognition

**Hadirku** adalah sistem presensi cerdas berbasis pengenalan wajah (face recognition) yang dirancang untuk lingkungan akademik. Dengan teknologi ini, proses presensi menjadi lebih cepat, akurat, dan aman menggantikan metode konvensional yang rawan manipulasi dan ketidakefisienan.

---

## 💡 Filosofi Proyek

Absensi manual sering kali menghadapi kendala seperti pemalsuan kehadiran, antrian panjang, dan rekap data yang memakan waktu. Hadirku memanfaatkan **AI untuk deteksi wajah** sebagai identitas presensi digital, sekaligus menyediakan **dashboard manajemen** untuk admin dan kemudahan akses bagi mahasiswa.

---

## ⚙️ Teknologi yang Digunakan

| Komponen     | Teknologi                              |
|--------------|----------------------------------------|
| Backend      | Flask (Python)                         |
| Database     | SQLAlchemy (SQLite/MySQL)              |
| Frontend     | HTML, CSS, JavaScript, SweetAlert2                 |
| Face Recognition | **face_recognition, dlib, OpenCV**     |
| Embedding    | Pickle (serialisasi data wajah)        |

---

## ✨ Fitur Aplikasi

### 👨‍🎓 Mahasiswa (User)
- **Signup** dengan nama lengkap dan NIM (sebagai password awal).
- **Registrasi wajah** langsung melalui webcam.
- **Presensi otomatis** berbasis kecocokan wajah.
- **Pemilihan kelas** saat melakukan presensi.
- **Riwayat presensi** meliputi:
  - Tanggal dan waktu
  - Kelas yang dihadiri
  - Lokasi presensi
  - Bukti foto hasil presensi
- **Logout** untuk mengakhiri sesi dengan aman.

### 🧑‍💼 Admin
- **Login sebagai admin** (melalui script setup awal).
- **Dashboard admin** untuk:
  - Melihat dan mengelola data presensi
  - Mengelola data kelas dan matakuliah
  - Melakukan analisis dan monitoring kehadiran
- **Logout** untuk keluar dari sistem.

---

## 🧠 Teknologi Face Recognition

Sistem ini mengkombinasikan beberapa library kuat untuk mencapai proses pengenalan wajah yang efisien dan akurat.

### Otak Pengenalan: `face_recognition` & `dlib`
Inti dari sistem ini adalah library **`face_recognition`** yang dibangun di atas toolkit C++ **`dlib`**. Pendekatan ini mengubah gambar wajah menjadi representasi matematis unik yang disebut **face encoding**, yaitu sebuah "sidik jari" digital berupa vektor 128 angka. Saat absensi, *encoding* dari wajah di webcam akan dibandingkan dengan *encoding* yang tersimpan di database. Perbandingan ini menghitung **jarak (distance)** antara kedua vektor; semakin kecil jaraknya, semakin mirip wajahnya.

### Mata & Tangan: Peran Krusial `OpenCV`
Meskipun `dlib` menjadi otak dari proses pengenalan, **OpenCV (diimpor sebagai `cv2`)** memegang peranan pendukung yang tak kalah penting sebagai 'mata dan tangan' dari sistem:

* **Pemrosesan Gambar**: Saat gambar diterima dari webcam (dalam format base64), `OpenCV` menggunakan fungsi `cv2.imdecode` untuk mengubahnya menjadi format gambar yang dapat diolah. Sebaliknya, fungsi `cv2.imwrite` digunakan untuk menyimpan foto bukti presensi ke dalam folder `static/captures`.

* **Konversi Warna**: Ini adalah fungsi vital. OpenCV membaca gambar dalam format warna BGR (Blue-Green-Red), sedangkan `dlib` memerlukan format standar RGB (Red-Green-Blue). Fungsi `cv2.cvtColor` digunakan untuk mengonversi format warna ini, memastikan "otak" (`dlib`) dapat menganalisis gambar dengan benar.

Singkatnya, **OpenCV menangani semua tugas manipulasi data gambar, sementara `dlib` dan `face_recognition` fokus pada analisis untuk mengenali siapa pemilik wajah tersebut.**

### Prosesnya:

1.  Tangkap satu foto wajah berkualitas saat pendaftaran.
2.  Hasilkan *face encoding* (vektor 128-d) menggunakan library `face_recognition`.
3.  Simpan *encoding* ke dalam database pengguna.
4.  Saat absensi, bandingkan *encoding* wajah baru dengan semua *encoding* di database untuk validasi.

---

## 🚀 Cara Menjalankan Hadirku di Komputer Lokal

Ikuti langkah-langkah berikut di terminal atau command prompt:

### 1. Clone Repository

```bash
git clone https://github.com/akbarnurrizqi167/hadirku-project.git
```
```bash
cd hadirku-project
```

### 2. Prasyarat Instalasi (Penting!)
Sebelum menginstal dependensi Python, pastikan sistem Anda memiliki alat yang dibutuhkan untuk mengkompilasi dlib, yaitu library inti yang digunakan untuk pengenalan wajah.

Untuk Pengguna Windows:
Anda wajib menginstal kedua alat berikut:

#### A. Visual Studio Build Tools (C++ Compiler)

- Link Unduhan: https://visualstudio.microsoft.com/downloads/
  - Tutorial Singkat:
  1. Buka link di atas, scroll ke bawah hingga menemukan Tools for Visual Studio.
  2. Klik tombol Download pada opsi Build Tools for Visual Studio.
  3. Jalankan installer yang telah diunduh.
  4. Pada tab Workloads, centang kotak "Desktop development with C++". Ini adalah langkah paling penting.
  5. Klik "Install" di pojok kanan bawah dan tunggu hingga prosesnya selesai.

#### B. CMake

- Link Unduhan: https://cmake.org/download/
  - Tutorial Singkat:
  1. Buka link di atas, cari versi "Windows x64 Installer" terbaru (file yang berakhiran .msi).
  2. Jalankan installer.
  3. Saat proses instalas, Anda akan diberikan pilihan untuk modifikasi PATH. Pilih opsi "Add CMake to the system PATH for all users". Ini wajib agar CMake bisa ditemukan oleh terminal.
  4. Selesaikan  instalasi dengan mengklik "Next" hingga "Finish".

- Utuk Pengguna Linux (Debian/Ubuntu):

```bash
sudo apt-get update && sudo apt-get install build-essential cmake
```
Setelah semua prasyarat di atas terpenuhi, restart terminal Anda sebelum melanjutkan ke langkah berikutnya.

### 3. Install Dependencies
Disarankan menggunakan Python versi 3.9 atau 3.10.

Dengan prasyarat yang sudah terpasang, sekarang jalankan perintah berikut untuk menginstal semua library Python yang dibutuhkan.

```bash
pip install -r requirements.txt
```

### 4. Buat Akun Admin
Jalankan skrip ini untuk membuat akun admin pertama Anda.

```bash
python create_admin.py
```
> "Ikuti prompt untuk memasukkan username dan password admin"

### 5. Inisialisasi Database
Jalankan skrip ini untuk mengisi data awal (seperti daftar mata kuliah) ke dalam database.

```bash
python seed_db.py
```

### 6. Jalankan Aplikasi

```bash
flask run
```

Akses aplikasi di browser Anda:
📍 http://localhost:5000

---

## 📁 Struktur Direktori (Singkat)

```
hadirku-project/
├── instance/                  # Folder instance (otomatis dibuat oleh Flask)
│   └── attendance.db          # File database SQLite 
├── static/                    # Folder untuk aset statis 
│   ├── captures/              # Menyimpan foto bukti presensi 
│   ├── css/                   # File-file CSS 
│   │   └── style.css
│   └── js/                    # File-file JavaScript 
│       └── main.js
├── templates/                 # Folder untuk template HTML 
│   ├── admin/                 # Template khusus untuk halaman admin 
│   │   ├── index.html
│   │   └── my_master.html
│   ├── base.html              # Template dasar/induk
│   ├── index.html             # Halaman utama presensi
│   ├── login.html             # Halaman login
│   ├── records.html           # Halaman riwayat presensi
│   ├── register_face.html     # Halaman pendaftaran wajah
│   └── signup.html            # Halaman pendaftaran akun
├── app.py                     # Konfigurasi utama dan factory aplikasi Flask 
├── auth.py                    # Rute untuk otentikasi (login, signup) 
├── create_admin.py            # Skrip untuk membuat akun admin awal 
├── face_utils.py              # Fungsi-fungsi untuk pengenalan wajah 
├── main.py                    # Rute utama aplikasi (presensi, riwayat) 
├── models.py                  # Definisi model database (SQLAlchemy) 
├── README.md                  # File dokumentasi proyek 
├── requirements.txt           # Daftar dependensi Python 
└── seed_db.py                 # Skrip untuk mengisi data awal database 
```

---

## 🔒 Catatan Keamanan

* Gunakan password yang kuat saat membuat akun admin.
* Pastikan kamera aktif saat registrasi wajah dan presensi.
* Disarankan dijalankan di lingkungan jaringan lokal untuk pengujian.

---

## 🤝 Kontribusi

Kami terbuka untuk kolaborasi dan kontribusi dari siapa saja!
Bantu kami mengembangkan Hadirku menjadi sistem presensi berbasis AI yang lebih kuat dan inklusif.

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE).

---

## 📬 Kontak Pengembang

**Akbar Nur Rizqi**
📧 [akbarnurrizqi167@gmail.com](mailto:akbarnurrizqi167@gmail.com)
🌐 GitHub: [github.com/akbarnurrizqi167](https://github.com/akbarnurrizqi167)
