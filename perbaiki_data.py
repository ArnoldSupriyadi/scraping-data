import json
import os

def perbaiki_jsonl():
    file_path = 'katalog_produk.jsonl'
    file_temp = 'katalog_produk_temp.jsonl'

    # Kamus pintar untuk mendeteksi brand dari kata kunci di dalam judul
    keyword_map = {
        "AMBYAR": {"brand": "AMBYAR", "category": "Perawatan Rumah"},
        "DANTE": {"brand": "DANTE", "category": "Sepatu & Sandal"},
        "SPREI": {"brand": "SPREI", "category": "Rumah Tangga"},
        "SANDAL": {"brand": "DANTE", "category": "Sepatu & Sandal"},
        "SEPATU PANTOFEL": {"brand": "SKL", "category": "Sepatu & Sandal"},
        "MADU BAWANG": {"brand": "SERBAINDO", "category": "Kesehatan & Herbal"},
        "BATIK": {"brand": "BATIK", "category": "Fashion Pria"},
        "BUNDLING": {"brand": "PROMO", "category": "Lainnya"},
        
        # --- TAMBAHAN BARU ---
        "PG STORE": {"brand": "PG STORE", "category": "Perawatan Rumah"},
        "BRAVINA": {"brand": "BRAVINA", "category": "Kesehatan & Herbal"},
        "ITEMAX": {"brand": "ITEMAX", "category": "Perawatan Kendaraan"},

        # --- TAMBAHAN BARU ---
        "ZENSIUM": {"brand": "ZENSIUM", "category": "Kesehatan & Herbal"},
        "MADU OCEAN": {"brand": "MADU OCEAN", "category": "Kesehatan & Herbal"},
        "SLIMPLUS": {"brand": "SLIMPLUS", "category": "Kesehatan & Herbal"},
        "BOOM": {"brand": "BOOM", "category": "Perlengkapan Mancing"},
        "ESSEN": {"brand": "ESSEN", "category": "Perlengkapan Mancing"},
        "BROAZMI": {"brand": "BROAZMI", "category": "Perawatan Kendaraan"},
        "BRO AZMI": {"brand": "BROAZMI", "category": "Perlengkapan Mancing"},
        "BLACK COMPOUND": {"brand": "BA", "category": "Perawatan Kendaraan"},
        "ULTRAFOAM": {"brand": "BA", "category": "Perawatan Kendaraan"},
        "JAMUR KACA": {"brand": "BA", "category": "Perawatan Kendaraan"},
        "SEMIR BAN": {"brand": "BA", "category": "Perawatan Kendaraan"},
        "INSTANT GLOSS": {"brand": "BA", "category": "Perawatan Kendaraan"},
        "GENTLE CLEAN": {"brand": "BA", "category": "Perawatan Kendaraan"},
        "RUBBING COMPOUND": {"brand": "BA", "category": "Perawatan Kendaraan"},
        "GLASS COATING": {"brand": "BA", "category": "Perawatan Kendaraan"},
        "BLACK MAGIC": {"brand": "BA", "category": "Perawatan Kendaraan"},
        "SHOES CLEANER": {"brand": "MISS CLEAN", "category": "Perawatan Rumah"}
    }

    count_brand_fixed = 0
    count_berat_fixed = 0

    print("🛠️ Memulai perbaikan data katalog_produk.jsonl...")

    with open(file_path, 'r', encoding='utf-8') as f_in, open(file_temp, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            data = json.loads(line)
            
            # --- 1. PERBAIKI BRAND "LAINNYA" ---
            if data.get("brand") == "LAINNYA":
                title_upper = data.get("title", "").upper()
                # Cek apakah ada kata kunci di dalam judul
                for kw, info in keyword_map.items():
                    if kw in title_upper:
                        data["brand"] = info["brand"]
                        data["category"] = info["category"]
                        count_brand_fixed += 1
                        break # Berhenti mencari jika sudah ketemu
            
            # --- 2. PERBAIKI BERAT KOSONG ---
            if "specs" in data:
                berat = data["specs"].get("berat", "-")
                if berat == "-" or berat is None or berat.strip() == "":
                    data["specs"]["berat"] = "1000.00 Gram"
                    count_berat_fixed += 1
            
            # Tulis data yang sudah bersih ke file sementara
            f_out.write(json.dumps(data, ensure_ascii=False) + '\n')

    # Timpa file lama dengan file yang sudah diperbaiki
    os.replace(file_temp, file_path)

    print("-" * 40)
    print("✅ PERBAIKAN SELESAI!")
    print(f"✨ Jumlah Brand 'LAINNYA' yang berhasil dikoreksi : {count_brand_fixed} produk")
    print(f"✨ Jumlah data berat kosong yang diisi 1 Kg      : {count_berat_fixed} produk")
    print("-" * 40)

if __name__ == "__main__":
    perbaiki_jsonl()