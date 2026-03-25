import json
import time
from playwright.sync_api import sync_playwright

def scrape_homepage():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        # ✅ Load cookies langsung saat buat context (bukan setelah)
        try:
            context = browser.new_context(storage_state="cookies.json")
        except Exception as e:
            print(f"❌ Gagal load cookies.json: {e}")
            print("👉 Jalankan dulu: python3 simpan_sesi.py")
            browser.close()
            return

        page = context.new_page()

        print("Membuka halaman utama Anekadropship...")

        # ✅ domcontentloaded lebih cepat, tidak nunggu script eksternal
        page.goto("https://anekadropship.id/user/home", timeout=60000, wait_until="domcontentloaded")

        # Cek apakah berhasil login (tidak diredirect ke halaman login)
        if "/login" in page.url:
            print("❌ Sesi expired! Jalankan dulu: python3 simpan_sesi.py")
            browser.close()
            return

        print(f"✅ Halaman terbuka: {page.url}")

        # Tunggu produk selesai dimuat
        page.wait_for_timeout(8000)

        data_katalog = list()

        print("--- Memulai Ekstraksi Data Produk ---")

        kartu_produk = page.locator("div.w-64.flex-shrink-0.bg-white")
        jumlah_produk = kartu_produk.count()

        print(f"Ditemukan {jumlah_produk} produk di halaman ini.\n")

        for i in range(jumlah_produk):
            elemen = kartu_produk.nth(i)

            try:
                judul_elemen = elemen.locator("a.line-clamp-2").first
                judul = judul_elemen.inner_text()
                link_produk = judul_elemen.get_attribute("href")

                harga_modal = elemen.locator("span.text-red-500.font-bold").first.inner_text()
                harga_jual = elemen.locator("span.text-green-700.font-semibold").first.inner_text()

                data_katalog.append({
                    "judul": judul,
                    "link": link_produk,
                    "harga_modal": harga_modal,
                    "rekomendasi_jual": harga_jual
                })
                print(f"Berhasil -> {judul} | Modal: {harga_modal} | Jual: {harga_jual}")

            except Exception as e:
                pass

            time.sleep(0.1)

        browser.close()

        with open("hasil_home.json", "w", encoding="utf-8") as f:
            json.dump(data_katalog, f, indent=4, ensure_ascii=False)

        print(f"\nProses Selesai! Total {len(data_katalog)} produk berhasil disimpan ke 'hasil_home.json'.")

if __name__ == "__main__":
    scrape_homepage()