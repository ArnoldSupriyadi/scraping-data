import json
import os
from collections import Counter

FILE_PATH = 'katalog_produk.jsonl'

def validasi():
    if not os.path.exists(FILE_PATH):
        print(f"❌ File '{FILE_PATH}' tidak ditemukan.")
        return

    produk_list = []
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            try:
                produk_list.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"⚠️  Baris {i} tidak valid JSON, dilewati.")

    total = len(produk_list)
    print(f"\n{'='*55}")
    print(f"  LAPORAN VALIDASI DATA — katalog_produk.jsonl")
    print(f"{'='*55}")
    print(f"  Total produk terbaca : {total}")

    # ── 1. Cek duplikat ID ──────────────────────────────────
    id_list  = [p.get('id_produk', '') for p in produk_list]
    url_list = [p.get('link', '')      for p in produk_list]

    id_duplikat  = [k for k, v in Counter(id_list).items()  if v > 1]
    url_duplikat = [k for k, v in Counter(url_list).items() if v > 1]

    print(f"\n── 1. Duplikat ─────────────────────────────────────")
    if id_duplikat:
        print(f"  ❌ id_produk duplikat ({len(id_duplikat)}):")
        for d in id_duplikat:
            print(f"     • {d}")
    else:
        print(f"  ✅ Tidak ada id_produk duplikat")

    if url_duplikat:
        print(f"  ❌ URL duplikat ({len(url_duplikat)}):")
        for d in url_duplikat:
            print(f"     • {d}")
    else:
        print(f"  ✅ Tidak ada URL duplikat")

    # ── 2. Cek harga nol / tidak wajar ─────────────────────
    print(f"\n── 2. Harga ────────────────────────────────────────")

    modal_nol   = [p for p in produk_list if p.get('price_modal', 0) == 0]
    rekomen_nol = [p for p in produk_list if p.get('price_recommendation', 0) == 0]
    harga_sama  = [p for p in produk_list
                   if p.get('price_modal') == p.get('price_recommendation')
                   and p.get('price_modal', 0) > 0]
    modal_lebih = [p for p in produk_list
                   if p.get('price_modal', 0) > p.get('price_recommendation', 0)]

    def tampil_masalah(label, items):
        if items:
            print(f"  ❌ {label} ({len(items)} produk):")
            for p in items[:5]:
                print(f"     • {p['title'][:50]} | modal={p.get('price_modal')} | rekomen={p.get('price_recommendation')}")
            if len(items) > 5:
                print(f"     ... dan {len(items)-5} lainnya")
        else:
            print(f"  ✅ {label}: tidak ada")

    tampil_masalah("price_modal = 0",                  modal_nol)
    tampil_masalah("price_recommendation = 0",         rekomen_nol)
    tampil_masalah("price_modal == price_recommendation", harga_sama)
    tampil_masalah("price_modal > price_recommendation",  modal_lebih)

    # ── 3. Cek field kosong / fallback ──────────────────────
    print(f"\n── 3. Kelengkapan field ────────────────────────────")

    no_desc    = [p for p in produk_list if not p.get('description') or p['description'] == 'Deskripsi tidak tersedia.']
    no_img     = [p for p in produk_list if 'anekamedia.jpeg' in p.get('image_link', '')]
    no_brand   = [p for p in produk_list if p.get('brand', 'LAINNYA') == 'LAINNYA']
    no_berat   = [p for p in produk_list if p.get('specs', {}).get('berat', '-') == '-']

    def tampil_field(label, items):
        icon = "⚠️ " if items else "✅"
        print(f"  {icon} {label}: {len(items)} produk" if items else f"  {icon} {label}: semua lengkap")
        for p in items[:3]:
            print(f"     • {p['title'][:55]}")
        if len(items) > 3:
            print(f"     ... dan {len(items)-3} lainnya")

    tampil_field("Tanpa deskripsi",        no_desc)
    tampil_field("Tanpa gambar (fallback)", no_img)
    tampil_field("Brand = LAINNYA",        no_brand)
    tampil_field("Tanpa data berat",       no_berat)

    # ── 4. Ringkasan brand & kategori ──────────────────────
    print(f"\n── 4. Distribusi brand & kategori ──────────────────")
    brand_count    = Counter(p.get('brand', 'LAINNYA')    for p in produk_list)
    kategori_count = Counter(p.get('category', 'Lainnya') for p in produk_list)

    print(f"  Brand ({len(brand_count)} brand):")
    for brand, count in brand_count.most_common():
        print(f"     {count:>3} produk  →  {brand}")

    print(f"\n  Kategori ({len(kategori_count)} kategori):")
    for kat, count in kategori_count.most_common():
        print(f"     {count:>3} produk  →  {kat}")

    # ── 5. Statistik margin ─────────────────────────────────
    print(f"\n── 5. Statistik margin ─────────────────────────────")
    margins = [p.get('margin', 0) for p in produk_list if p.get('margin', 0) > 0]
    if margins:
        avg_margin  = sum(margins) / len(margins)
        max_margin  = max(margins)
        min_margin  = min(margins)
        max_produk  = next(p for p in produk_list if p.get('margin') == max_margin)
        min_produk  = next(p for p in produk_list if p.get('margin') == min_margin)

        print(f"  Rata-rata margin : Rp {avg_margin:,.0f}")
        print(f"  Margin tertinggi : Rp {max_margin:,}  →  {max_produk['title'][:45]}")
        print(f"  Margin terendah  : Rp {min_margin:,}  →  {min_produk['title'][:45]}")

    # ── 6. Kesimpulan ───────────────────────────────────────
    total_masalah = (
        len(id_duplikat) + len(url_duplikat) +
        len(modal_nol) + len(rekomen_nol) +
        len(harga_sama) + len(modal_lebih)
    )

    print(f"\n{'='*55}")
    if total_masalah == 0:
        print(f"  ✅ DATA SIAP UPLOAD — tidak ada masalah kritis")
    else:
        print(f"  ❌ ADA {total_masalah} MASALAH KRITIS — selesaikan dulu sebelum upload")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    validasi()