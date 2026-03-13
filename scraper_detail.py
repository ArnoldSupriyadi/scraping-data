import json
import csv
import time
from playwright.sync_api import sync_playwright

def scrape_detail_massal():
    print("Mulai menyedot detail dari produk...")
    
    # 1. Buka data dari file JSON hasil scraper_home
    try:
        with open('hasil_home.json', 'r', encoding='utf-8') as f:
            daftar_produk = json.load(f)
    except Exception as e:
        print(f"Gagal membaca hasil_home.json: {e}")
        return

    # 2. Siapkan file CSV untuk Meta Ads
    csv_file = open('katalog_meta_ads.csv', 'w', newline='', encoding='utf-8')
    writer = csv.writer(csv_file)
    
    # Header Wajib Meta Ads (Facebook/Instagram Catalog)
    writer.writerow(["id", "title", "description", "availability", "condition", "price", "link", "image_link", "brand"])

    # 3. Mulai proses Scraping dengan Playwright
    with sync_playwright() as p:
        # Gunakan parameter anti-bot
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        
        # Suntikkan cookies agar terdeteksi sudah login
        context = browser.new_context(storage_state="cookies.json")
        page = context.new_page()

        for index, produk in enumerate(daftar_produk):
            id_produk = f"AD-{index+1}"
            judul = produk.get("judul", "Tanpa Judul")
            url = produk.get("link", "")
            
            # Mengambil harga jual dari hasil home
            harga_jual = produk.get("rekomendasi_jual", "0")
            
            # Membersihkan format harga (Misal: Rp. 140.000 menjadi 140000 IDR)
            harga_bersih = str(harga_jual).replace("Rp.", "").replace("Rp", "").replace(".", "").strip()
            harga_meta = f"{harga_bersih} IDR"

            print(f"[{index+1}/{len(daftar_produk)}] Mengunjungi: {judul}")

            try:
                page.goto(url, timeout=60000)
                # Jeda 4 detik agar elemen gambar dan deskripsi selesai dimuat
                page.wait_for_timeout(4000) 

                # -- AMBIL DESKRIPSI UTAMA --
                try:
                    # Mencari class "prose" yang membungkus deskripsi produk
                    deskripsi_utama = page.locator('.prose').inner_text().strip()
                except:
                    deskripsi_utama = "Deskripsi tidak tersedia."

                # -- AMBIL LINK GAMBAR UTAMA --
                try:
                    # Menggunakan ID mainImage yang ada di source code HTML
                    link_gambar = page.locator('#mainImage').get_attribute('src')
                except:
                    link_gambar = "https://anekadropship.id/poto/anekamedia.jpeg"

                # -- AMBIL SPESIFIKASI TAMBAHAN --
                try:
                    berat = page.locator("p").filter(has_text="Berat :").first.inner_text().replace('\n', ' ').strip()
                except:
                    berat = "Berat : -"
                    
                try:
                    volume = page.locator("p").filter(has_text="Volume :").first.inner_text().replace('\n', ' ').strip()
                except:
                    volume = "Volume : -"
                    
                try:
                    ekspedisi = page.locator("p").filter(has_text="Rekomendasi Ekspedisi :").first.inner_text().replace('\n', ' ').strip()
                except:
                    ekspedisi = "Rekomendasi Ekspedisi : -"
                    
                try:
                    sistem = page.locator("p").filter(has_text="Sistem :").first.inner_text().replace('\n', ' ').strip()
                except:
                    sistem = "Sistem : -"

                # -- GABUNGKAN DESKRIPSI & SPESIFIKASI --
                deskripsi_lengkap = f"{deskripsi_utama}\n\nSpesifikasi:\n- {berat}\n- {volume}\n- {ekspedisi}\n- {sistem}"

                print("  -> Detail berhasil ditarik!")

            except Exception as e:
                print(f"  -> (Detail gagal ditarik: {e})")
                deskripsi_lengkap = "Produk dropship berkualitas siap kirim."
                link_gambar = "https://anekadropship.id/poto/anekamedia.jpeg"

            # =================================================================
            # 4. TULIS DATA KE DALAM BARIS CSV (Sesuai dengan header Meta Ads)
            # =================================================================
            writer.writerow([id_produk, judul, deskripsi_lengkap, "in stock", "new", harga_meta, url, link_gambar, "Toko Dropshipku"])

            # Jeda 2 detik antar produk agar server Anekadropship tidak down
            time.sleep(2)

        browser.close()
    
    csv_file.close()
    print("\n🎉 Proses Scraping Selesai! Data berhasil disimpan di 'katalog_meta_ads.csv'")

if __name__ == "__main__":
    scrape_detail_massal()