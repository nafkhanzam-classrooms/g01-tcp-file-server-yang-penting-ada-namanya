[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/mRmkZGKe)
# Network Programming - Assignment G01

## Anggota Kelompok
| Nama           | NRP        | Kelas     |
| ---            | ---        | ----------|
| Muhammad Irsyad Habibi| 5025221150 | D |
|                |            |           |

## Link Youtube (Unlisted)
Link ditaruh di bawah ini
```

```

## Penjelasan Program

## 📁 Struktur Project

```id="7w9aqo"
.
├── client.py
├── server-sync.py
├── server-thread.py
├── server-select.py
├── server-poll.py
└── files/
```

---

## ⚙️ Cara Kerja

### 🔹 Protokol Komunikasi

Karena TCP bersifat **stream-based**, digunakan protokol khusus:

* Command diakhiri dengan newline:

  ```
  /command args\n
  ```
* Transfer file menggunakan delimiter:

  ```
  <END_OF_FILE>
  ```

---

## 🖥️ Client (`client.py`)

### Fungsi:

* Mengirim command ke server
* Menerima broadcast message
* Menangani upload dan download file

### Alur Kerja:

1. Client terhubung ke server melalui TCP socket
2. Menjalankan thread receiver untuk menerima pesan
3. Memproses input user:

   * `/list` → meminta daftar file
   * `/upload` → mengirim file + delimiter
   * `/download` → menerima file hingga delimiter
   * selain command → broadcast message

### Catatan:

* Menggunakan **single socket reader** untuk menghindari race condition
* Memisahkan penanganan data teks dan data biner

---

## 🧵 Server Thread (`server-thread.py`)

### Model:

* Satu thread untuk setiap client

### Alur Kerja:

1. Menerima koneksi client
2. Membuat thread baru
3. Memproses command:

   * `/list` → kirim daftar file
   * `/upload` → menerima file hingga `<END_OF_FILE>`
   * `/download` → kirim file + delimiter
   * lainnya → broadcast ke client lain

### Karakteristik:

* ✅ Mudah diimplementasikan
* ✅ Mendukung concurrency
* ⚠️ Menggunakan banyak resource jika client banyak

---

## 🧍 Server Sync (`server-sync.py`)

### Model:

* Hanya melayani satu client dalam satu waktu

### Alur Kerja:

* Server menyelesaikan satu client sebelum menerima client berikutnya

### Karakteristik:

* ✅ Sederhana
* ❌ Blocking
* ❌ Tidak scalable

---

## ⚡ Server Select (`server-select.py`)

### Model:

* I/O multiplexing menggunakan `select`

### Alur Kerja:

1. Memantau banyak socket sekaligus
2. Menggunakan buffer untuk setiap client
3. Memproses data secara bertahap
4. Menggunakan state machine:

   * `cmd` → membaca command
   * `upload` → menerima file

### Karakteristik:

* ✅ Lebih efisien dari thread
* ✅ Non-blocking
* ⚠️ Implementasi lebih kompleks

---

## ⚡ Server Poll (`server-poll.py`)

### Model:

* Event-driven menggunakan `poll`

### Alur Kerja:

* Mirip dengan `select`, tetapi menggunakan event berbasis file descriptor

### Karakteristik:

* ✅ Lebih scalable dibanding select
* ✅ Cocok untuk banyak client
* ⚠️ Lebih kompleks

---

## 🔁 Perbandingan Server

| Server | Concurrency | Kompleksitas | Skalabilitas |
| ------ | ----------- | ------------ | ------------ |
| Sync   | ❌           | ⭐            | ❌            |
| Thread | ✅           | ⭐⭐           | ⚠️           |
| Select | ✅           | ⭐⭐⭐          | ✅            |
| Poll   | ✅           | ⭐⭐⭐          | 🚀           |

---

## Screenshot Hasil

Command list, upload, download, and broadcast
<img width="1920" height="1080" alt="Screenshot (185)" src="https://github.com/user-attachments/assets/59825625-b264-4a34-aa4c-d191bc3c44f8" />
