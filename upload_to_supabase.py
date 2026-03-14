import json
import os
from supabase import create_client

<<<<<<< HEAD
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
=======
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BATCH_SIZE = 50  # Upload 50 produk sekaligus


def bersihkan_null(nilai):
    """Konversi nilai kosong / '-' menjadi None (null di database)."""
    if nilai in ["-", "", "null", None]:
        return None
    return nilai


def upload_data_ke_supabase():
    file_path = 'katalog_produk.jsonl'

    if not os.path.exists(file_path):
        print(f"❌ File '{file_path}' tidak ditemukan.")
        return

    # ── 1. Baca semua data dari JSONL ───────────────────────
    semua_produk = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                semua_produk.append(json.loads(line))

    total = len(semua_produk)
    print(f"🚀 Memulai upload {total} produk ke Supabase...")
    print(f"   Batch size : {BATCH_SIZE} produk per request")
    print("-" * 55)

    # ── 2. Set semua produk lama → is_active = False ────────
    # Produk yang tidak muncul di scraping terbaru akan tetap False
    print("🔄 Menonaktifkan semua produk lama (is_active = false)...")
    try:
        supabase.table("products").update({"is_active": False}).neq("id_produk", "").execute()
        print("   ✅ Selesai\n")
    except Exception as e:
        print(f"   ⚠️  Gagal reset is_active: {e}")
        print("   Lanjut upload tanpa reset...\n")

    # ── 3. Siapkan payload ──────────────────────────────────
    payloads = []
    for data in semua_produk:
        specs = data.get("specs", {})
        payload = {
            "id_produk":            data.get("id_produk"),
            "title":                data.get("title"),
            "brand":                data.get("brand", "LAINNYA"),
            "category":             data.get("category", "Lainnya"),
            "price_modal":          data.get("price_modal", 0),
            "price_recommendation": data.get("price_recommendation", 0),
            "margin":               data.get("margin", 0),
            "margin_pct":           data.get("margin_pct", 0),
            "currency":             data.get("currency", "IDR"),
            "link":                 data.get("link"),
            "image_link":           data.get("image_link"),
            "description":          data.get("description"),
            "specs": {
                "berat":                 bersihkan_null(specs.get("berat")),
                "volume":                bersihkan_null(specs.get("volume")),
                "ekspedisi":             bersihkan_null(specs.get("ekspedisi")),
                "sistem":                bersihkan_null(specs.get("sistem")),
                "harga_rekomendasi_raw": bersihkan_null(specs.get("harga_rekomendasi_raw")),
            },
            "is_active":  True,   # produk yang baru di-scrape = aktif
            "scraped_at": data.get("scraped_at"),
        }
        payloads.append(payload)

    # ── 4. Upload dalam batch ───────────────────────────────
    berhasil   = 0
    error_count = 0

    for i in range(0, total, BATCH_SIZE):
        batch      = payloads[i : i + BATCH_SIZE]
        batch_dari = i + 1
        batch_ke   = min(i + BATCH_SIZE, total)

        try:
            supabase.table("products").upsert(batch, on_conflict="id_produk").execute()
            berhasil += len(batch)
            print(f"✅ Batch {batch_dari}–{batch_ke} berhasil ({len(batch)} produk)")

        except Exception as e:
            error_count += len(batch)
            print(f"❌ Batch {batch_dari}–{batch_ke} gagal: {e}")

            # Fallback: coba upload satu per satu di batch yang gagal
            print(f"   🔄 Mencoba ulang satu per satu...")
            berhasil   -= 0  # sudah dikurangi di atas
            error_count -= len(batch)
            for produk in batch:
                try:
                    supabase.table("products").upsert(produk, on_conflict="id_produk").execute()
                    berhasil += 1
                except Exception as e2:
                    error_count += 1
                    print(f"   ❌ Gagal: {produk.get('title', '')[:40]} → {e2}")

    # ── 5. Ringkasan ────────────────────────────────────────
    print("-" * 55)
    print(f"✨ PROSES SELESAI!")
    print(f"📊 Berhasil diupload : {berhasil} produk")
    print(f"📊 Gagal             : {error_count} produk")
    nonaktif = total - berhasil if berhasil < total else 0
    print(f"📊 Produk nonaktif   : produk lama yang tidak ada di scraping terbaru → is_active = false")
    print("-" * 55)

>>>>>>> 8fb10666bd4e62874ad1db2fd50a8d7977209051

if __name__ == "__main__":
    upload_data_ke_supabase()