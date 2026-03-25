import json
import time
from playwright.sync_api import sync_playwright

def simpan_cookie():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("Membuka halaman login Anekadropship...")
        page.goto("https://anekadropship.id/login", timeout=60000, wait_until="domcontentloaded")

        print("=" * 50)
        print("SILAKAN LOGIN MANUAL DI BROWSER YANG TERBUKA.")
        print("Ketik email + password lalu klik tombol Login.")
        print("Script akan otomatis lanjut setelah kamu berhasil masuk.")
        print("=" * 50)

        # ✅ Tunggu sampai URL berubah dari /login ke halaman lain (dashboard)
        # Maksimal tunggu 120 detik
        try:
            page.wait_for_url(
                lambda url: "/login" not in url,
                timeout=120000
            )
            print(f"✅ Login berhasil! URL sekarang: {page.url}")
        except Exception:
            print("⚠️  Timeout menunggu login. Coba lagi.")
            browser.close()
            return

        # Tunggu sebentar agar semua cookies ter-set sempurna
        time.sleep(3)

        # Simpan storage state (cookies + localStorage)
        context.storage_state(path="cookies.json")

        print("✅ Sesi login berhasil disimpan ke cookies.json!")
        print("Sekarang bisa jalankan: python3 scraper_home.py")

        browser.close()

if __name__ == "__main__":
    simpan_cookie()