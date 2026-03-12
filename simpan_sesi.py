import json
import time
from playwright.sync_api import sync_playwright

def simpan_cookie():
    with sync_playwright() as p:
        # Membuka peramban yang bisa Anda lihat (headless=False)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("Membuka halaman login Anekadropship...")
        page.goto("https://anekadropship.id/login")
        
        print("SILAKAN LOGIN SECARA MANUAL DI BROWSER YANG TERBUKA.")
        print("Anda punya waktu 45 detik untuk mengetik email, password, dan klik tombol masuk.")
        
        # Waktu tunggu 45 detik agar Anda bisa login manual
        time.sleep(45) 
        
        # Skrip akan otomatis menyimpan "tiket VIP" (cookies) setelah 45 detik
        cookies = context.cookies()
        with open("cookies.json", "w") as f:
            f.write(json.dumps(cookies))
            
        print("Berhasil! Sesi login telah disimpan ke file cookies.json!")
        browser.close()

if __name__ == "__main__":
    simpan_cookie()