import json
import os
from supabase import create_client

# --- [BAGIAN 2: ISI DATA DI SINI] ---
# Ambil data ini dari menu Settings > API di dashboard Supabase kamu
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Inisialisasi koneksi ke Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_data_ke_supabase():
    file_path = 'katalog_produk.jsonl'
    
    # Cek apakah file JSONL-nya ada
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' tidak ditemukan di folder ini.")
        return

    print(f"🚀 Memulai proses upload ke tabel 'products'...")
    print("-" * 50)

    berhasil = 0
    dilewati = 0
    error_count = 0

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                # 1. Baca data dari baris JSONL
                data = json.loads(line)
                
                # 2. Mapping data sesuai kolom di tabel Supabase kamu
                # Pastikan nama key di data.get() sesuai dengan hasil scraping terakhir
                payload = {
                    "id_produk": data.get("id_produk"),
                    "title": data.get("title"),
                    "price_modal": data.get("price_modal"),
                    "price_recommendation": data.get("price_recommendation"),
                    "currency": data.get("currency", "IDR"),
                    "link": data.get("link"),
                    "image_link": data.get("image_link"),
                    "description": data.get("description"),
                    "specs": data.get("specs"),
                    "scraped_at": data.get("scraped_at")
                }

                # 3. Masukkan ke database
                supabase.table("products").upsert(payload, on_conflict="id_produk").execute()
                
                berhasil += 1
                print(f"✅ [{berhasil}] Berhasil: {payload['title'][:40]}...")

            except Exception as e:
                # Menangani jika data sudah ada (duplicate id_produk)
                if "duplicate key" in str(e).lower():
                    dilewati += 1
                    print(f"⏩ Dilewati: {data.get('title', 'Produk')[:30]}... (Sudah ada)")
                else:
                    error_count += 1
                    print(f"❌ Gagal pada produk {data.get('title', 'N/A')}: {e}")

    # Ringkasan Akhir
    print("-" * 50)
    print(f"✨ PROSES SELESAI!")
    print(f"📊 Total Berhasil : {berhasil}")
    print(f"📊 Total Dilewati : {dilewati} (Data Duplikat)")
    print(f"📊 Total Error    : {error_count}")
    print("-" * 50)

if __name__ == "__main__":
    upload_data_ke_supabase()