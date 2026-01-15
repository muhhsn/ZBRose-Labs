import os
import shutil
import platform
import sys

# ==========================================
# PRODUCT OF ZBROSE LABS
# Program : ZB Cleaner Classic
# Version : 1.0 (Stable - No Logs - No Loop)
# Author  : ZBRose
# ==========================================

# Daftar file yang diabaikan (Sampah Sistem)
IGNORE_LIST = {
    'Thumbs.db', 'desktop.ini', '.DS_Store', 
    'ntuser.dat', 'pagefile.sys'
}

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + "="*42)
    print("   Z B R O S E   L A B S   P R E S E N T S")
    print("="*42)
    print("      >>> ZB CLEANER CLASSIC <<<")
    print(f"      OS: {platform.system()}")
    print("="*42 + "\n")

def get_unique_filename(target_folder, filename):
    """Fungsi auto-rename jika file duplikat (file_1, file_2)"""
    base_name, extension = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(target_folder, new_filename)):
        new_filename = f"{base_name}_{counter}{extension}"
        counter += 1
    return new_filename

def zb_cleaner_process():
    print_header()
    
    # Proteksi: Jangan pindahkan script ini sendiri
    script_filename = os.path.basename(sys.argv[0])
    script_location = os.path.normcase(os.path.abspath(sys.argv[0]))

    # --- 1. INPUT DATA ---
    print("[INPUT DATA]")
    source_path = input(" > Target Folder Path: ").strip().strip('"').strip("'")
    if not os.path.exists(source_path):
        print(" [X] Error: Target tidak ditemukan!")
        input("\nTekan [ENTER] untuk keluar...")
        return
    source_path = os.path.abspath(source_path)

    dest_path = input(" > Destinasi Folder Path: ").strip().strip('"').strip("'")
    dest_path = os.path.abspath(dest_path)

    # Safety: Mencegah folder tujuan ada di dalam folder target
    if dest_path.startswith(source_path) and dest_path != source_path:
        print("\n [!] WARNING: Destinasi ada di dalam Target.")
        if input("     Lanjut? (y/n): ").lower() != 'y': return

    # --- 2. PILIH MODE ---
    print("\n[MODE OPERASI]")
    print(" 1. SIMULASI (Dry Run) - Cek doang")
    print(" 2. EKSEKUSI (Live)    - Pindah beneran")
    mode = input(" Pilih (1/2): ")
    dry_run = True if mode == '1' else False

    # Buat folder destinasi kalau belum ada (Hanya mode Live)
    if not dry_run and not os.path.exists(dest_path):
        try:
            os.makedirs(dest_path)
        except OSError as e:
            print(f" [X] Gagal buat folder: {e}")
            input("\nTekan [ENTER] untuk keluar...")
            return

    print(f"\n--- Memulai Proses ({'SIMULASI' if dry_run else 'LIVE'}) ---\n")
    
    processed = 0
    ignored = 0
    errors = 0

    # --- 3. PROSES SCANNING ---
    # Kita pakai 'with' biar aman memorinya
    with os.scandir(source_path) as entries:
        for entry in entries:
            if entry.is_file():
                filename = entry.name
                
                # FILTER: Skip script sendiri & file sampah
                if filename == script_filename: continue
                if os.path.normcase(os.path.abspath(entry.path)) == script_location: continue
                if filename in IGNORE_LIST or filename.startswith('~$'):
                    ignored += 1
                    continue

                # LOGIKA: Tentukan nama folder berdasarkan ekstensi
                _, extension = os.path.splitext(filename)
                if filename.startswith('.') and not extension:
                    folder_name = "Dotfiles"
                elif extension:
                    folder_name = extension[1:].lower()
                else:
                    folder_name = "No_Extension"

                target_folder_path = os.path.join(dest_path, folder_name)
                
                # LOGIKA: Cek Duplikat
                final_filename = filename
                if not dry_run:
                    if not os.path.exists(target_folder_path):
                        os.makedirs(target_folder_path)
                    final_filename = get_unique_filename(target_folder_path, filename)

                # EKSEKUSI: Pindahkan file
                try:
                    src = entry.path
                    dst = os.path.join(target_folder_path, final_filename)

                    if dry_run:
                        print(f" [SIM] {filename} -> {folder_name}/{final_filename}")
                    else:
                        shutil.move(src, dst)
                        if filename != final_filename:
                            print(f" [REN] {filename} -> {folder_name}/{final_filename}")
                        else:
                            print(f" [MOV] {filename} -> {folder_name}/")
                    
                    processed += 1

                except Exception as e:
                    print(f" [ERR] {filename}: {e}")
                    errors += 1
    
    # --- 4. LAPORAN AKHIR ---
    # (Perhatikan: Bagian ini SEJAJAR dengan 'with', jadi dia cuma jalan 1x)
    print("\n" + "="*42)
    print(f" STATUS: {'SIMULASI' if dry_run else 'CLEANING'} SELESAI")
    print(f" [v] Berhasil : {processed}")
    print(f" [-] Diabaikan: {ignored}")
    print(f" [x] Error    : {errors}")
    print("="*42)
    print(" ZBRose Labs - Keeping your data structured.")

    # Biar program gak langsung nutup sendiri
    input("\nTekan [ENTER] untuk menutup program...")

if __name__ == "__main__":
    zb_cleaner_process()
