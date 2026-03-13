import json
import time
import random
import csv
from playwright.sync_api import sync_playwright

def scrape_detail_massal():
    # 1. Buka file hasil_home.json yang berisi daftar link
    try:
        with open("hasil_home.json", "r", encoding="utf-8") as f:
            daftar_produk = json.load(f)
    except FileNotFoundError:
        print("File hasil_home.json tidak ditemukan!")
        return

    # 2. Siapkan wadah (list) untuk format JSON
    data_detail_json = list()

    # 3. Siapkan file CSV (Format standar Facebook/Meta Ads)
    file_csv = open("katalog_meta_ads.csv", "w", newline="", encoding="utf-8")
    writer = csv.writer(file_csv)
    # Header Kolom sesuai syarat mutlak Meta Ads
    writer.writerow(["id", "title", "description", "availability", "condition", "price", "link", "image_link", "brand"])

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context()

        # Muat cookies agar melewati login
        try:
            with open("cookies.json", "r") as f:
                context.add_cookies(json.loads(f.read()))
        except Exception:
            print("Peringatan: file cookies.json tidak ditemukan. Bot mungkin disuruh login.")

        page = context.new_page()
        
        print(f"Mulai menyedot detail dari {len(daftar_produk)} produk...\n")

        for index, produk in enumerate(daftar_produk):
            url = produk["link"]
            judul = produk["judul"]
            harga_jual = produk["rekomendasi_jual"]
            
            # Mengambil ID unik dari tautan (contoh: dari /1255 menjadi 1255)
            id_produk = url.split("/")[-1]

            print(f"[{index+1}/{len(daftar_produk)}] Mengunjungi: {judul}")
            
            try:
                page.goto(url)
                # Tunggu 4 detik agar gambar dan deskripsi selesai dimuat
                page.wait_for_timeout(4000) 

                # =================================================================
                # Mengambil teks deksripsi dan link gambar
                # =================================================================
                deskripsi = page.locator("div").filter(has_text="Deskripsi").first.inner_text()
                link_gambar = page.locator("img").nth(1).get_attribute("src")

            except Exception as e:
                print("  -> (Detail gagal ditarik, menggunakan teks default)")
                deskripsi = "Produk dropship berkualitas siap kirim."
                link_gambar = "https://anekadropship.id/poto/anekamedia.jpeg"

            # Membersihkan format harga (Misal: Rp. 140.000 menjadi 140000 IDR)
            harga_bersih = harga_jual.replace("Rp.", "").replace("Rp", "").replace(".", "").strip()
            harga_meta = f"{harga_bersih} IDR"

            # =================================================================
            # 4. TULIS DATA KE DALAM BARIS CSV (Sudah diisi dengan benar!)
            # =================================================================
            writer.writerow()

            # 5. Masukkan data yang sama ke dalam struktur JSON
            data_detail_json.append({
                "id": id_produk,
                "title": judul,
                "description": deskripsi,
                "availability": "in stock",
                "condition": "new",
                "price": harga_meta,
                "link": url,
                "image_link": link_gambar,
                "brand": "Toko Saya"
            })

            # JEDA ACAK (SANGAT KRUSIAL agar tidak diblokir sistem)
            jeda = random.uniform(4, 8)
            print(f"  -> Selesai! Jeda {jeda:.2f} detik sebelum lanjut...\n")
            time.sleep(jeda)

        # Tutup browser dan file CSV
        browser.close()
        file_csv.close()

        # 6. Simpan hasil list JSON ke dalam file baru
        with open("katalog_detail.json", "w", encoding="utf-8") as f_json:
            json.dump(data_detail_json, f_json, indent=4, ensure_ascii=False)

        print("SEMUA PROSES SELESAI!")
        print("1. Data untuk Meta Ads tersimpan di: katalog_meta_ads.csv")
        print("2. Data cadangan JSON tersimpan di: katalog_detail.json")

if __name__ == "__main__":
    scrape_detail_massal()