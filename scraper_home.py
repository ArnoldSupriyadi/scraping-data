import json
import time
from playwright.sync_api import sync_playwright

def scrape_homepage():
    with sync_playwright() as p:
        # Membuka browser dengan anti-deteksi bot bawaan
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        ) 
        context = browser.new_context()
        
        # 1. Muat cookies agar tidak perlu login
        try:
            with open("cookies.json", "r") as f:
                cookies = json.loads(f.read())
                context.add_cookies(cookies)
        except FileNotFoundError:
            print("File cookies.json tidak ditemukan! Pastikan Anda sudah menjalankan simpan_sesi.py")
            return
            
        page = context.new_page()
        
        print("Membuka halaman utama Anekadropship...")
        page.goto("https://anekadropship.id/user/home")
        
        # Tunggu 8 detik agar semua gambar dan produk selesai dimuat
        page.wait_for_timeout(8000)
        
        # INISIALISASI WADAH KOSONG (Ini bagian yang error sebelumnya)
        data_katalog = list()
        
        print("--- Memulai Ekstraksi Data Produk ---")
        
        # 2. Mencari semua kotak produk berdasarkan HTML asli
        kartu_produk = page.locator("div.w-64.flex-shrink-0.bg-white") 
        jumlah_produk = kartu_produk.count()
        
        print(f"Ditemukan {jumlah_produk} produk di halaman ini.\n")
        
        for i in range(jumlah_produk):
            elemen = kartu_produk.nth(i)
            
            try:
                # Mengekstrak Judul dan Link menggunakan tag 'a'
                judul_elemen = elemen.locator("a.line-clamp-2").first
                judul = judul_elemen.inner_text()
                link_produk = judul_elemen.get_attribute("href")
                
                # Mengekstrak Harga Diskon/Modal (Warna Merah)
                harga_modal = elemen.locator("span.text-red-500.font-bold").first.inner_text()
                
                # Mengekstrak Harga Rekomendasi Jual (Warna Hijau)
                harga_jual = elemen.locator("span.text-green-700.font-semibold").first.inner_text()
                
                # Memasukkan data ke dalam wadah
                data_katalog.append({
                    "judul": judul,
                    "link": link_produk,
                    "harga_modal": harga_modal,
                    "rekomendasi_jual": harga_jual
                })
                print(f"Berhasil -> {judul} | Modal: {harga_modal} | Jual: {harga_jual}")
                
            except Exception as e:
                # Jika ada elemen iklan atau kotak yang strukturnya beda, akan dilewati
                pass
            
            # Beri sedikit jeda mikro antar ekstraksi
            time.sleep(0.1)

        browser.close()
        
        # 3. Simpan hasil ke file JSON
        with open("hasil_home.json", "w", encoding="utf-8") as f:
            json.dump(data_katalog, f, indent=4, ensure_ascii=False)
            
        print(f"\nProses Selesai! Total {len(data_katalog)} produk berhasil disimpan ke 'hasil_home.json'.")

if __name__ == "__main__":
    scrape_homepage()