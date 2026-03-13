import json
import os
import time
from playwright.sync_api import sync_playwright

def scrape_detail_massal():
    print("🚀 Memulai proses scraping detail produk (Versi Anti-Logout)...")
    
    # 1. Load data dari hasil scraper home
    try:
        with open('hasil_home.json', 'r', encoding='utf-8') as f:
            daftar_produk = json.load(f)
    except Exception as e:
        print(f"❌ Gagal membaca hasil_home.json: {e}")
        return

    # --- LOGIKA AUTO-RESUME ---
    json_file_path = 'katalog_produk.jsonl'
    start_index = 0
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as f:
            start_index = sum(1 for line in f)
        print(f"♻️  Melanjutkan dari item ke-{start_index + 1}")

    # 2. Jalankan Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        try:
            context = browser.new_context(storage_state="cookies.json")
        except:
            context = browser.new_context()
            
        page = context.new_page()

        # Loop produk
        for index, produk in enumerate(daftar_produk[start_index:], start=start_index):
            
            # Restart browser setiap 50 item
            if index > start_index and index % 50 == 0:
                print("🧹 Membersihkan memori browser...")
                context.close()
                context = browser.new_context(storage_state="cookies.json")
                page = context.new_page()

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
                    
                    # 1. Deskripsi
                    try:
                        deskripsi_raw = page.locator(".prose").first.inner_text().strip()
                        deskripsi_utama = deskripsi_raw.replace("Deskripsi Produk", "").strip()
                    except:
                        deskripsi_utama = "Deskripsi tidak tersedia."

                    # 2. Gambar
                    try:
                        link_gambar = page.locator("#mainImage").get_attribute("src")
                        if link_gambar and not link_gambar.startswith("http"):
                            link_gambar = "https://anekadropship.id" + link_gambar
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

if __name__ == "__main__":
    scrape_detail_massal()