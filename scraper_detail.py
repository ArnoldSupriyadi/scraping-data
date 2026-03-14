import json
import os
<<<<<<< HEAD
import time
from playwright.sync_api import sync_playwright

def scrape_detail_massal():
    print("🚀 Memulai proses scraping detail produk (Versi Anti-Logout)...")
    
=======
import re
import time
from playwright.sync_api import sync_playwright


def ekstrak_brand_dan_kategori(judul: str):
    """
    Ekstrak brand dan kategori dari prefix judul produk.
    Contoh: "[CHERBAL] Dragon Blood Cream" → brand="CHERBAL", kategori="Kesehatan & Herbal"
    """
    match = re.match(r'\[(.+?)\]', judul)
    brand = match.group(1).strip() if match else "LAINNYA"

    # Mapping brand → kategori
    kategori_map = {
        "CHERBAL":    "Kesehatan & Herbal",
        "HERBALUNA":  "Kesehatan & Herbal",
        "SERBAINDO":  "Kesehatan & Herbal",
        "BIOZARIA":   "Kesehatan & Herbal",
        "MADU OCEAN": "Kesehatan & Herbal",
        "BRAVINA":    "Kesehatan & Herbal",
        "SLIMPLUS":   "Kesehatan & Herbal",
        "ZENSIUM":    "Kesehatan & Herbal",
        "BATIK":      "Fashion Pria",
        "SRK":        "Fashion Muslim",
        "SKL":        "Sepatu & Sandal",
        "DANTE":      "Sepatu & Sandal",
        "TAS":        "Tas & Aksesoris",
        "CHELSEA":    "Fashion Anak",
        "DR A":       "Fashion Anak",
        "PG STORE":   "Perawatan Rumah",
        "MISS CLEAN": "Perawatan Rumah",
        "Pak Arief":  "Parfum & Wewangian",
        "AMARA":      "Parfum & Wewangian",
        "INDORAYA":   "Kesehatan Pria",
        "R46":        "Perawatan Kendaraan",
        "BROAZMI":    "Perawatan Kendaraan",
        "BA":         "Perawatan Kendaraan",
        "ESSEN":      "Perlengkapan Mancing",
        "BOOM":       "Perlengkapan Mancing",
        "AMBYAR":     "Perawatan Rumah",
        "PAKET BUNDLE GET 5": "Perawatan Rumah",
    }

    # Cek partial match juga (misal "Pak Arief" vs "PAK ARIEF")
    kategori = "Lainnya"
    for key, val in kategori_map.items():
        if key.upper() in brand.upper():
            kategori = val
            break

    return brand, kategori


def scrape_detail_massal():
    print("🚀 Memulai proses scraping detail produk (Versi Final)...")

>>>>>>> 8fb10666bd4e62874ad1db2fd50a8d7977209051
    # 1. Load data dari hasil scraper home
    try:
        with open('hasil_home.json', 'r', encoding='utf-8') as f:
            daftar_produk = json.load(f)
    except Exception as e:
        print(f"❌ Gagal membaca hasil_home.json: {e}")
        return

<<<<<<< HEAD
=======
    # Deduplikasi berdasarkan URL produk sebelum scraping
    seen_urls = set()
    produk_unik = []
    for p in daftar_produk:
        url = p.get("link", "")
        if url not in seen_urls:
            seen_urls.add(url)
            produk_unik.append(p)

    duplikat = len(daftar_produk) - len(produk_unik)
    if duplikat > 0:
        print(f"⚠️  Ditemukan {duplikat} produk duplikat, dilewati otomatis.")
    print(f"📦 Total produk unik yang akan di-scrape: {len(produk_unik)}")

>>>>>>> 8fb10666bd4e62874ad1db2fd50a8d7977209051
    # --- LOGIKA AUTO-RESUME ---
    json_file_path = 'katalog_produk.jsonl'
    start_index = 0
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as f:
            start_index = sum(1 for line in f)
        print(f"♻️  Melanjutkan dari item ke-{start_index + 1}")

    # 2. Jalankan Playwright
    with sync_playwright() as p:
<<<<<<< HEAD
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        try:
            context = browser.new_context(storage_state="cookies.json")
        except:
            context = browser.new_context()
            
        page = context.new_page()

        # Loop produk
        for index, produk in enumerate(daftar_produk[start_index:], start=start_index):
            
            # Restart browser setiap 50 item
=======
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        try:
            context = browser.new_context(storage_state="cookies.json")
        except Exception:
            context = browser.new_context()

        page = context.new_page()

        # Loop produk
        for index, produk in enumerate(produk_unik[start_index:], start=start_index):

            # Restart browser setiap 50 item untuk cegah memory leak
>>>>>>> 8fb10666bd4e62874ad1db2fd50a8d7977209051
            if index > start_index and index % 50 == 0:
                print("🧹 Membersihkan memori browser...")
                context.close()
                context = browser.new_context(storage_state="cookies.json")
                page = context.new_page()

<<<<<<< HEAD
            # --- LOGIKA PENGULANGAN JIKA GAGAL (ANTI-SKIP) ---
            success = False
            while not success:
                judul = produk.get("judul", "Tanpa Judul")
                url = produk.get("link", "")
                harga_jual = produk.get("rekomendasi_jual", "0")
                harga_bersih = str(harga_jual).replace("Rp.", "").replace("Rp", "").replace(".", "").replace(",", "").strip()

                print(f"[{index+1}/{len(daftar_produk)}] Mengunjungi: {judul}")

                try:
                    page.goto(url, timeout=60000, wait_until="domcontentloaded")
                    
                    # CEK APAKAH LOGOUT/MENTAL
                    try:
                        # Tunggu deskripsi muncul
                        page.wait_for_selector(".prose", timeout=10000)
                    except:
                        print(f"\n🚨 KONTEN TIDAK MUNCUL di produk ke-{index+1}!")
                        print("👉 Sepertinya kamu logout otomatis atau sesi habis.")
                        print("🛠  TINDAKAN: Silakan LOGIN ULANG di jendela browser yang terbuka.")
                        input("⌨️  SUDAH LOGIN? Tekan [ENTER] di terminal ini untuk mencoba lagi produk ini...")
                        continue # Kembali ke atas 'while' untuk produk yang sama

                    # --- EKSTRAKSI DATA ---
                    page.wait_for_timeout(1000) 
                    
=======
            success = False
            while not success:
                judul = produk.get("judul", "Tanpa Judul")
                url   = produk.get("link", "")

                # ✅ ID stabil dari URL, bukan nomor urut
                product_id = url.split("/")[-1]

                # ✅ Harga modal dari hasil_home.json (tidak ada di halaman web)
                harga_modal_raw = produk.get("harga_modal", "0")
                harga_bersih = (
                    str(harga_modal_raw)
                    .replace("Rp.", "").replace("Rp", "")
                    .replace(".", "").replace(",", "")
                    .strip()
                )

                # ✅ Ekstrak brand & kategori dari judul
                brand, kategori = ekstrak_brand_dan_kategori(judul)

                print(f"[{index+1}/{len(produk_unik)}] {judul[:55]}...")

                try:
                    page.goto(url, timeout=60000, wait_until="domcontentloaded")

                    # Cek apakah sesi masih aktif
                    try:
                        page.wait_for_selector(".prose", timeout=10000)
                    except Exception:
                        print(f"\n🚨 KONTEN TIDAK MUNCUL di produk ke-{index+1}!")
                        print("👉 Sepertinya sesi habis. Silakan LOGIN ULANG di browser.")
                        input("⌨️  Sudah login? Tekan [ENTER] untuk mencoba lagi...")
                        continue

                    page.wait_for_timeout(1000)

                    # --- EKSTRAKSI DATA ---

>>>>>>> 8fb10666bd4e62874ad1db2fd50a8d7977209051
                    # 1. Deskripsi
                    try:
                        deskripsi_raw = page.locator(".prose").first.inner_text().strip()
                        deskripsi_utama = deskripsi_raw.replace("Deskripsi Produk", "").strip()
<<<<<<< HEAD
                    except:
                        deskripsi_utama = "Deskripsi tidak tersedia."

                    # 2. Gambar
=======
                    except Exception:
                        deskripsi_utama = "Deskripsi tidak tersedia."

                    # 2. Gambar utama
>>>>>>> 8fb10666bd4e62874ad1db2fd50a8d7977209051
                    try:
                        link_gambar = page.locator("#mainImage").get_attribute("src")
                        if link_gambar and not link_gambar.startswith("http"):
                            link_gambar = "https://anekadropship.id" + link_gambar
<<<<<<< HEAD
                    except:
                        link_gambar = "https://anekadropship.id/poto/anekamedia.jpeg"

                    # 3. Spesifikasi
                    def get_strong_text(label_name):
                        try:
                            return page.locator(f"p:has-text('{label_name}')").locator("strong").inner_text(timeout=3000).strip()
                        except: return "-"

                    # Ambil harga rekomendasi dari teks web (Contoh: "Rp. 140.000")
                    raw_rekomendasi = get_strong_text("Rekomendasi Harga Jual :")
                    # Bersihkan jadi angka saja (140000)
                    harga_rekomendasi_bersih = str(raw_rekomendasi).replace("Rp.", "").replace("Rp", "").replace(".", "").replace(",", "").strip()

                    data_final = {
                    "id_produk": f"AD-{index+1}",
                    "title": judul,
                    "price_modal": int(harga_bersih) if harga_bersih.isdigit() else 0, # Harga dari hasil_home
                    "price_recommendation": int(harga_rekomendasi_bersih) if harga_rekomendasi_bersih.isdigit() else 0, # Harga dari detail web
                    "currency": "IDR",
                    "link": url,
                    "image_link": link_gambar,
                    "description": deskripsi_utama,
                    "specs": {
                        "berat": get_strong_text("Berat :"),
                        "volume": get_strong_text("Volume :"),
                        "ekspedisi": get_strong_text("Rekomendasi Ekspedisi :"),
                        "sistem": get_strong_text("Sistem :"),
                        "harga_rekomendasi_raw": raw_rekomendasi # Versi teks asli Rp. xxx
                    },
                    "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }

                    # Simpan data
                    with open(json_file_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(data_final) + '\n')
                    
                    print(f"   ✅ Berhasil ditarik!")
                    success = True # Keluar dari while, lanjut ke produk next index
                    time.sleep(2) # Kasih jeda lebih lama biar awet login-nya

                except Exception as e:
                    print(f"   ⚠️ Terjadi kesalahan: {e}")
                    if "closed" in str(e).lower():
                        print("🚨 Browser tertutup. Script berhenti.")
                        return
                    print("Mencoba ulang dalam 5 detik...")
                    time.sleep(5)

        browser.close()
    print(f"\n✨ Selesai! Data aman di: {json_file_path}")
=======
                    except Exception:
                        link_gambar = "https://anekadropship.id/poto/anekamedia.jpeg"

                    # 3. Helper ambil nilai dari tag <strong>
                    def get_strong_text(label_name):
                        try:
                            return (
                                page.locator(f"p:has-text('{label_name}')")
                                .locator("strong")
                                .inner_text(timeout=3000)
                                .strip()
                            )
                            return result if result else None 
                        except Exception:
                            return None

                    # 4. Harga rekomendasi dari halaman web (lebih akurat)
                    raw_rekomendasi = get_strong_text("Rekomendasi Harga Jual :")
                    harga_rekomendasi_bersih = (
                        str(raw_rekomendasi)
                        .replace("Rp.", "").replace("Rp", "")
                        .replace(".", "").replace(",", "")
                        .strip()
                    )

                    # 5. Hitung margin (computed, untuk referensi cepat)
                    modal_int = int(harga_bersih) if harga_bersih.isdigit() else 0
                    rekomen_int = int(harga_rekomendasi_bersih) if harga_rekomendasi_bersih.isdigit() else 0
                    margin = rekomen_int - modal_int
                    margin_pct = round((margin / modal_int * 100), 1) if modal_int > 0 else 0

                    data_final = {
                        "id_produk":          f"AD-{product_id}",   # ✅ ID stabil dari URL
                        "title":              judul,
                        "brand":              brand,                 # ✅ baru
                        "category":           kategori,              # ✅ baru
                        "price_modal":        modal_int,             # ✅ dari hasil_home.json
                        "price_recommendation": rekomen_int,         # ✅ dari halaman web
                        "margin":             margin,                # ✅ computed (rekomen - modal)
                        "margin_pct":         margin_pct,            # ✅ computed dalam %
                        "currency":           "IDR",
                        "link":               url,
                        "image_link":         link_gambar,
                        "description":        deskripsi_utama,
                        "specs": {
                            "berat":                  get_strong_text("Berat :"),
                            "volume":                 get_strong_text("Volume :"),
                            "ekspedisi":              get_strong_text("Rekomendasi Ekspedisi :"),
                            "sistem":                 get_strong_text("Sistem :"),
                            "harga_rekomendasi_raw":  raw_rekomendasi,
                        },
                        "is_active":   True,                         # ✅ baru, berguna di Next.js
                        "scraped_at":  time.strftime("%Y-%m-%d %H:%M:%S"),
                    }

                    # Simpan ke file JSONL
                    with open(json_file_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(data_final, ensure_ascii=False) + '\n')

                    print(f"   ✅ [{brand}] modal={modal_int:,} | rekomen={rekomen_int:,} | margin={margin_pct}%")
                    success = True
                    time.sleep(2)

                except Exception as e:
                    print(f"   ⚠️  Kesalahan: {e}")
                    if "closed" in str(e).lower():
                        print("🚨 Browser tertutup. Script berhenti.")
                        return
                    print("   🔄 Mencoba ulang dalam 5 detik...")
                    time.sleep(5)

        browser.close()

    print(f"\n✨ Selesai! {len(produk_unik) - start_index} produk disimpan ke: {json_file_path}")

>>>>>>> 8fb10666bd4e62874ad1db2fd50a8d7977209051

if __name__ == "__main__":
    scrape_detail_massal()