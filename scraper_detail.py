import json
import os
import time
from playwright.sync_api import sync_playwright

def scrape_detail_to_json():
    print("🚀 Memulai proses scraping detail produk (Output: JSON)...")
    
    # 1. Load data hasil home
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
        context = browser.new_context(storage_state="cookies.json")
        page = context.new_page()

        # Proses produk yang belum terserap
        for index, produk in enumerate(daftar_produk[start_index:], start=start_index):
            
            # RESTART BROWSER TIAP 50 PRODUK (Anti-Crash RAM)
            if index > start_index and index % 50 == 0:
                print("🧹 Refreshing browser memory...")
                context.close()
                context = browser.new_context(storage_state="cookies.json")
                page = context.new_page()

            judul = produk.get("judul", "Tanpa Judul")
            url = produk.get("link", "")
            harga_jual = produk.get("rekomendasi_jual", "0")
            
            # Cleaning harga
            harga_bersih = str(harga_jual).replace("Rp.", "").replace("Rp", "").replace(".", "").strip()

            print(f"[{index+1}/{len(daftar_produk)}] Mengunjungi: {judul}")

            try:
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
                page.wait_for_timeout(3000) 

                # Scrape data
                try:
                    deskripsi_utama = page.locator('.prose').inner_text(timeout=5000).strip()
                except:
                    deskripsi_utama = "Deskripsi tidak tersedia."

                try:
                    link_gambar = page.locator('#mainImage').get_attribute('src', timeout=5000)
                except:
                    link_gambar = "https://anekadropship.id/poto/anekamedia.jpeg"

                def get_spec(text):
                    try:
                        return page.locator("p").filter(has_text=text).first.inner_text(timeout=3000).split(":")[-1].strip()
                    except: return "-"

                # Nyalakan struktur JSON
                data_final = {
                    "id_produk": f"AD-{index+1}",
                    "title": judul,
                    "price": int(harga_bersih) if harga_bersih.isdigit() else 0,
                    "currency": "IDR",
                    "link": url,
                    "image_link": link_gambar,
                    "description": deskripsi_utama,
                    "specs": {
                        "berat": get_spec("Berat :"),
                        "volume": get_spec("Volume :"),
                        "ekspedisi": get_spec("Rekomendasi Ekspedisi :"),
                        "sistem": get_spec("Sistem :")
                    },
                    "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }

                # SIMPAN LANGSUNG (JSON Lines)
                with open(json_file_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(data_final) + '\n')
                
                print("   ✅ Data disimpan ke JSONL")

            except Exception as e:
                print(f"   ⚠️ Error di item {index+1}: {e}")
                if "closed" in str(e).lower():
                    print("🚨 Browser mati mendadak. Silakan jalankan ulang script.")
                    break
            
            time.sleep(1.5)

        browser.close()

    print(f"\n✨ Selesai! File tersimpan di: {json_file_path}")

if __name__ == "__main__":
    scrape_detail_to_json()