import json
import os
import re
import time
from playwright.sync_api import sync_playwright


def ekstrak_brand_dan_kategori(judul: str):
    match = re.match(r'\[(.+?)\]', judul)
    brand = match.group(1).strip() if match else "LAINNYA"

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

    kategori = "Lainnya"
    for key, val in kategori_map.items():
        if key.upper() in brand.upper():
            kategori = val
            break

    return brand, kategori


def scrape_detail_massal():
    print("🚀 Memulai proses scraping detail produk (Versi Final + Marketing Kit)...")

    try:
        with open('hasil_home.json', 'r', encoding='utf-8') as f:
            daftar_produk = json.load(f)
    except Exception as e:
        print(f"❌ Gagal membaca hasil_home.json: {e}")
        return

    # Deduplikasi
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

    # Auto-resume
    json_file_path = 'katalog_produk.jsonl'
    start_index = 0
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as f:
            start_index = sum(1 for line in f)
        print(f"♻️  Melanjutkan dari item ke-{start_index + 1}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        try:
            context = browser.new_context(storage_state="cookies.json")
        except Exception:
            context = browser.new_context()

        page = context.new_page()

        for index, produk in enumerate(produk_unik[start_index:], start=start_index):

            # Restart browser setiap 50 item
            if index > start_index and index % 50 == 0:
                print("🧹 Membersihkan memori browser...")
                context.close()
                context = browser.new_context(storage_state="cookies.json")
                page = context.new_page()

            success = False
            while not success:
                judul = produk.get("judul", "Tanpa Judul")
                url   = produk.get("link", "")
                product_id = url.split("/")[-1]

                harga_modal_raw = produk.get("harga_modal", "0")
                harga_bersih = (
                    str(harga_modal_raw)
                    .replace("Rp.", "").replace("Rp", "")
                    .replace(".", "").replace(",", "")
                    .strip()
                )

                brand, kategori = ekstrak_brand_dan_kategori(judul)

                print(f"[{index+1}/{len(produk_unik)}] {judul[:55]}...")

                try:
                    page.goto(url, timeout=60000, wait_until="domcontentloaded")

                    # Cek sesi aktif
                    try:
                        page.wait_for_selector(".prose", timeout=10000)
                    except Exception:
                        print(f"\n🚨 KONTEN TIDAK MUNCUL di produk ke-{index+1}!")
                        print("👉 Sepertinya sesi habis. Silakan LOGIN ULANG di browser.")
                        input("⌨️  Sudah login? Tekan [ENTER] untuk mencoba lagi...")
                        continue

                    page.wait_for_timeout(1000)

                    # ── Deskripsi ──────────────────────────────────────
                    try:
                        deskripsi_raw = page.locator(".prose").first.inner_text().strip()
                        deskripsi_utama = deskripsi_raw.replace("Deskripsi Produk", "").strip()
                    except Exception:
                        deskripsi_utama = "Deskripsi tidak tersedia."

                    # ── Gambar utama ───────────────────────────────────
                    try:
                        link_gambar = page.locator("#mainImage").get_attribute("src")
                        if link_gambar and not link_gambar.startswith("http"):
                            link_gambar = "https://anekadropship.id" + link_gambar
                    except Exception:
                        link_gambar = "https://anekadropship.id/poto/anekamedia.jpeg"

                    # ── Semua thumbnail/gambar produk ──────────────────
                    try:
                        thumbnail_els = page.locator("#thumbnailContainer img")
                        semua_gambar = []
                        for i in range(thumbnail_els.count()):
                            src = thumbnail_els.nth(i).get_attribute("src")
                            if src:
                                semua_gambar.append(src)
                    except Exception:
                        semua_gambar = [link_gambar] if link_gambar else []

                    # ── Helper ambil nilai dari <strong> ───────────────
                    def get_strong_text(label_name):
                        try:
                            return (
                                page.locator(f"p:has-text('{label_name}')")
                                .locator("strong")
                                .inner_text(timeout=3000)
                                .strip()
                            )
                        except Exception:
                            return None

                    # ── Marketing Kit URL ──────────────────────────────
                    # Selector: <a> yang mengandung teks "Download Marketing Kit"
                    # atau <a> di dalam section Marketing Kit
                    marketing_kit_url = None
                    try:
                        mk_link = page.locator("a:has-text('Download Marketing Kit')").first
                        if mk_link.count() > 0:
                            marketing_kit_url = mk_link.get_attribute("href")
                    except Exception:
                        pass

                    # Fallback: cari <a> di dalam h3 "Marketing Kit"
                    if not marketing_kit_url:
                        try:
                            marketing_kit_url = (
                                page.locator("h3:has-text('Marketing Kit') + * a, h3:has-text('Marketing Kit') ~ div a")
                                .first
                                .get_attribute("href")
                            )
                        except Exception:
                            pass

                    # ── Landing Page URL ───────────────────────────────
                    landing_page_url = None
                    try:
                        lp_link = page.locator("a:has-text('Preview')").first
                        if lp_link.count() > 0:
                            landing_page_url = lp_link.get_attribute("href")
                    except Exception:
                        pass

                    # ── Harga rekomendasi ──────────────────────────────
                    raw_rekomendasi = get_strong_text("Rekomendasi Harga Jual :")
                    harga_rekomendasi_bersih = (
                        str(raw_rekomendasi)
                        .replace("Rp.", "").replace("Rp", "")
                        .replace(".", "").replace(",", "")
                        .strip()
                    )

                    # ── Hitung margin ──────────────────────────────────
                    modal_int   = int(harga_bersih) if harga_bersih.isdigit() else 0
                    rekomen_int = int(harga_rekomendasi_bersih) if harga_rekomendasi_bersih.isdigit() else 0
                    margin      = rekomen_int - modal_int
                    margin_pct  = round((margin / modal_int * 100), 1) if modal_int > 0 else 0

                    data_final = {
                        "id_produk":              f"AD-{product_id}",
                        "title":                  judul,
                        "brand":                  brand,
                        "category":               kategori,
                        "price_modal":            modal_int,
                        "price_recommendation":   rekomen_int,
                        "margin":                 margin,
                        "margin_pct":             margin_pct,
                        "currency":               "IDR",
                        "link":                   url,
                        "image_link":             link_gambar,
                        "images":                 semua_gambar,        # ✅ BARU: semua foto produk
                        "marketing_kit_url":      marketing_kit_url,   # ✅ BARU: link Google Drive / Canva
                        "landing_page_url":       landing_page_url,    # ✅ BARU: link landing page preview
                        "description":            deskripsi_utama,
                        "specs": {
                            "berat":                 get_strong_text("Berat :"),
                            "volume":                get_strong_text("Volume :"),
                            "ekspedisi":             get_strong_text("Rekomendasi Ekspedisi :"),
                            "sistem":                get_strong_text("Sistem :"),
                            "harga_rekomendasi_raw": raw_rekomendasi,
                        },
                        "is_active":  True,
                        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    }

                    with open(json_file_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(data_final, ensure_ascii=False) + '\n')

                    mk_status = "✅ Ada" if marketing_kit_url else "❌ Tidak ada"
                    lp_status = "✅ Ada" if landing_page_url else "❌ Tidak ada"
                    print(f"   ✅ [{brand}] modal={modal_int:,} | margin={margin_pct}% | MK: {mk_status} | LP: {lp_status}")
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


if __name__ == "__main__":
    scrape_detail_massal()