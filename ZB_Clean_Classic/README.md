# ZB Cleaner Classic

![ZBRose Labs](https://img.shields.io/badge/Product-ZBRose%20Labs-blue?style=flat-square) 
![Language](https://img.shields.io/badge/Python-3.x-yellow?style=flat-square) 
![Status](https://img.shields.io/badge/Status-Development%20(Beta)-orange?style=flat-square)

**ZB Cleaner Classic** adalah utilitas otomatisasi manajemen file (CLI) yang dirancang untuk merapikan direktori yang tidak terstruktur dengan mengelompokkan file berdasarkan ekstensinya secara instan. 

Dibangun dengan prinsip *Universal Compatibility*, program ini berjalan mulus di lingkungan **Windows** maupun **Linux**, serta dilengkapi mekanisme perlindungan data untuk mencegah kehilangan file yang tidak disengaja.

> **⚠️ DEVELOPMENT NOTICE (WIP)**
> 
> Program ini saat ini berada dalam tahap **Pengembangan Aktif (Beta)**. 
> Meskipun logika inti telah diuji untuk keamanan dan integritas data, pengguna **SANGAT DISARANKAN** untuk selalu menggunakan mode **"1. SIMULASI (Dry Run)"** terlebih dahulu untuk memverifikasi hasil sebelum melakukan eksekusi pemindahan file yang sebenarnya.

---

## 🚀 Fitur Utama

### 1. Cross-Platform Architecture
Secara cerdas mendeteksi sistem operasi (OS) dan menyesuaikan format path direktori (Backslash `\` untuk Windows atau Slash `/` untuk Linux) secara otomatis.

### 2. Data Integrity Protection
* **Anti-Overwrite:** Mencegah penimpaan file jika terdapat nama file yang sama di folder tujuan. Program akan otomatis melakukan *renaming* (Contoh: `data.csv` -> `data_1.csv`).
* **Simulation Mode (Dry Run):** Memungkinkan pengguna melihat pratinjau ("What-If Scenario") tentang ke mana file akan dipindahkan tanpa mengubah struktur file asli.

### 3. Smart Filtering Engine
* **System Noise Filter:** Secara otomatis mengabaikan file sampah sistem seperti `Thumbs.db`, `desktop.ini`, `.DS_Store`, dan temporary files (`~$...`).
* **Dotfiles Handling:** Mendeteksi file konfigurasi (seperti `.env`, `.gitignore`) dan mengelompokkannya ke dalam folder khusus `Dotfiles`, bukan dianggap sebagai error.

### 4. Safety Mechanisms
* **Self-Preservation:** Script tidak akan memindahkan dirinya sendiri meskipun berada di dalam folder target.
* **Recursion Guard:** Mencegah error fatal dengan mendeteksi jika folder destinasi berada di dalam folder target (*Infinite Loop Prevention*).

---

## 🛠️ Persyaratan Sistem

* **Python 3.6** atau yang lebih baru.
* Tidak memerlukan instalasi library eksternal (menggunakan *Standard Library* Python).

---

## 📖 Cara Penggunaan

1.  **Jalankan Program**
    Buka terminal atau CMD/PowerShell, lalu jalankan perintah:
    ```bash
    python ZB_Clean_Classic.py
    ```

2.  **Input Parameter**
    * **Target Folder:** Masukkan path folder yang ingin dirapikan.
    * **Destinasi Folder:** Masukkan path folder tempat hasil pengelompokan disimpan.
    * *(Tips: Anda dapat melakukan drag & drop folder ke jendela terminal untuk input path otomatis).*

3.  **Pilih Mode Operasi**
    * Tekan `1` untuk **SIMULASI (Dry Run)** -> *Disarankan untuk pemakaian pertama.*
    * Tekan `2` untuk **EKSEKUSI (Live)** -> *Memindahkan file secara permanen.*

---

## 📂 Contoh Hasil Struktur

**Sebelum (Berantakan):**
```text
Downloads/
├── Laporan_Keuangan.xlsx
├── script_bot.py
├── foto_liburan.jpg
├── .env
└── README.txt

**sesudah (Rapi Dan Tersimpar Perfolder):**
Destinasi/
├── xlsx/
│   └── Laporan_Keuangan.xlsx
├── py/
│   └── script_bot.py
├── jpg/
│   └── foto_liburan.jpg
├── Dotfiles/
│   └── .env
└── No_Extension/
    └── README.txt
