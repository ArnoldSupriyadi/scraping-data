"""
upload_to_supabase.py
=====================
Upload semua data ke Supabase: couriers, suppliers, supplier_products,
supplier_couriers, dan products (katalog).

Urutan upload otomatis dijaga agar FK tidak error.

Cara pakai:
  1. Pastikan file .env ada di folder yang sama, isinya:
       SUPABASE_URL=https://xxxx.supabase.co
       SUPABASE_KEY=your_service_role_key

  2. Jalankan:
       python upload_to_supabase.py              # upload semua tabel
       python upload_to_supabase.py --tabel products   # hanya products
       python upload_to_supabase.py --tabel suppliers couriers  # pilih beberapa

  3. Flag tambahan:
       --dry-run   Tampilkan data tanpa benar-benar upload
       --reset     Hapus semua data lama sebelum upload (hati-hati!)
"""

import json
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Path ke file data (sesuaikan jika berbeda)
BASE_DIR = Path(__file__).parent
DATA_FILES = {
    "couriers":          BASE_DIR / "couriers.json",
    "suppliers":         BASE_DIR / "suppliers.json",
    "supplier_products": BASE_DIR / "supplier_products.json",
    "supplier_couriers": BASE_DIR / "supplier_couriers.json",
    "products":          BASE_DIR / "katalog_produk_final.jsonl",
}

# Urutan upload wajib dijaga (FK dependency)
UPLOAD_ORDER = [
    "couriers",
    "suppliers",
    "supplier_products",
    "supplier_couriers",
    "products",
]

BATCH_SIZE = 50


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def bersihkan_null(nilai):
    """Konversi nilai kosong / '-' / 'null' menjadi None."""
    if nilai in ["-", "", "null", "NULL", None]:
        return None
    return nilai


def baca_file(path: Path) -> list:
    """Baca JSON atau JSONL, return list of dict."""
    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {path}")

    if path.suffix == ".jsonl":
        rows = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows
    else:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else [data]


def build_payload(tabel: str, row: dict) -> dict:
    """
    Buat payload bersih sesuai schema tabel.
    Hanya field yang ada di schema yang dikirim — field asing dibuang.
    """
    if tabel == "couriers":
        return {
            "id":   row["id"],
            "nama": row["nama"].strip(),
        }

    if tabel == "suppliers":
        return {
            "id":      row["id"],
            "nama":    row["nama"].strip(),
            "alamat":  bersihkan_null(row.get("alamat", "").replace("\n", " ").strip()),
            "catatan": bersihkan_null(row.get("catatan")),
        }

    if tabel == "supplier_products":
        return {
            "id":          row["id"],
            "supplier_id": row["supplier_id"],
            "nama_produk": row["nama_produk"].strip(),
            "kategori":    bersihkan_null(row.get("kategori")),
        }

    if tabel == "supplier_couriers":
        return {
            "id":          row["id"],
            "supplier_id": row["supplier_id"],
            "courier_id":  row["courier_id"],
        }

    if tabel == "products":
        specs_raw = row.get("specs") or {}
        return {
            "id_produk":            row["id_produk"],
            "title":                row.get("title"),
            "brand":                row.get("brand", "LAINNYA"),
            "category":             row.get("category", "Lainnya"),
            "price_modal":          bersihkan_null(row.get("price_modal")),
            "price_recommendation": row.get("price_recommendation", 0),
            "margin":               bersihkan_null(row.get("margin")),
            "margin_pct":           bersihkan_null(row.get("margin_pct")),
            "currency":             row.get("currency", "IDR"),
            "link":                 row.get("link"),
            "image_link":           bersihkan_null(row.get("image_link")),
            "description":          bersihkan_null(row.get("description")),
            "specs": {
                "berat":                 bersihkan_null(specs_raw.get("berat")),
                "volume":                bersihkan_null(specs_raw.get("volume")),
                "ekspedisi":             bersihkan_null(specs_raw.get("ekspedisi")),
                "sistem":                bersihkan_null(specs_raw.get("sistem")),
                "harga_rekomendasi_raw": bersihkan_null(specs_raw.get("harga_rekomendasi_raw")),
            },
            "is_active":   True,
            "scraped_at":  row.get("scraped_at"),
            "supplier_id": row.get("supplier_id"),
        }

    raise ValueError(f"Tabel tidak dikenal: {tabel}")


def conflict_key(tabel: str) -> str:
    """Primary key / unique key untuk upsert per tabel."""
    mapping = {
        "couriers":          "id",
        "suppliers":         "id",
        "supplier_products": "id",
        "supplier_couriers": "id",
        "products":          "id_produk",
    }
    return mapping[tabel]


# ─────────────────────────────────────────────────────────────
# UPLOAD
# ─────────────────────────────────────────────────────────────
def upload_tabel(
    supabase: Client,
    tabel: str,
    dry_run: bool = False,
    reset: bool = False,
):
    path = DATA_FILES[tabel]
    rows = baca_file(path)
    total = len(rows)
    conflict = conflict_key(tabel)

    print(f"\n{'─'*55}")
    print(f"📦 Tabel: {tabel}  ({total} rows)  |  file: {path.name}")
    print(f"{'─'*55}")

    if dry_run:
        print(f"   [DRY RUN] Sample payload:")
        sample = build_payload(tabel, rows[0])
        for k, v in sample.items():
            print(f"   {k}: {repr(str(v)[:60])}")
        print(f"   ... (total {total} rows — tidak diupload)")
        return

    # Optional reset: hapus semua data lama di tabel ini
    if reset:
        print(f"   ⚠️  RESET: menghapus semua data lama di '{tabel}'...")
        try:
            supabase.table(tabel).delete().neq(conflict, "").execute()
            print(f"   ✅ Reset selesai")
        except Exception as e:
            print(f"   ❌ Reset gagal: {e} — lanjut tanpa reset")

    # Khusus products: set semua is_active = False dulu
    # Produk yang tidak ada di scraping terbaru otomatis nonaktif
    if tabel == "products":
        print("   🔄 Set semua produk lama → is_active = false...")
        try:
            supabase.table("products").update({"is_active": False}).neq("id_produk", "").execute()
            print("   ✅ Selesai\n")
        except Exception as e:
            print(f"   ⚠️  Gagal reset is_active: {e} — lanjut...\n")

    # Build semua payload
    payloads = [build_payload(tabel, row) for row in rows]

    berhasil = 0
    gagal = 0

    for i in range(0, total, BATCH_SIZE):
        batch = payloads[i : i + BATCH_SIZE]
        dari  = i + 1
        ke    = min(i + BATCH_SIZE, total)

        try:
            supabase.table(tabel).upsert(batch, on_conflict=conflict).execute()
            berhasil += len(batch)
            print(f"   ✅ [{dari:>3}–{ke:<3}] {len(batch)} rows OK")

        except Exception as e:
            print(f"   ❌ [{dari:>3}–{ke:<3}] Batch gagal: {e}")
            print(f"   🔄 Retry satu per satu...")

            for payload in batch:
                pid = payload.get(conflict, "?")
                try:
                    supabase.table(tabel).upsert(payload, on_conflict=conflict).execute()
                    berhasil += 1
                except Exception as e2:
                    gagal += 1
                    print(f"      ❌ {pid}: {e2}")

    print(f"\n   📊 Berhasil : {berhasil} / {total}")
    if gagal:
        print(f"   📊 Gagal    : {gagal} / {total}")


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Upload data ke Supabase")
    parser.add_argument(
        "--tabel",
        nargs="*",
        choices=UPLOAD_ORDER,
        default=None,
        help="Tabel yang diupload. Default: semua tabel sesuai urutan.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Tampilkan sample payload tanpa upload ke Supabase.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Hapus data lama sebelum insert. Hati-hati dengan FK!",
    )
    args = parser.parse_args()

    # Validasi env
    if not args.dry_run:
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("❌ SUPABASE_URL dan SUPABASE_KEY belum diset di .env")
            sys.exit(1)

    # Pilih tabel
    tabel_dipilih = args.tabel if args.tabel else UPLOAD_ORDER

    # Jaga urutan sesuai UPLOAD_ORDER walau user pilih bebas
    tabel_dipilih = [t for t in UPLOAD_ORDER if t in tabel_dipilih]

    print("=" * 55)
    print("🚀 UPLOAD KE SUPABASE")
    print(f"   Tabel   : {', '.join(tabel_dipilih)}")
    print(f"   Dry run : {args.dry_run}")
    print(f"   Reset   : {args.reset}")
    print("=" * 55)

    if not args.dry_run:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        supabase = None  # tidak dipakai saat dry-run

    for tabel in tabel_dipilih:
        try:
            upload_tabel(supabase, tabel, dry_run=args.dry_run, reset=args.reset)
        except FileNotFoundError as e:
            print(f"\n⚠️  Skip '{tabel}': {e}")
        except Exception as e:
            print(f"\n❌ Error di tabel '{tabel}': {e}")
            print("   Lanjut ke tabel berikutnya...")

    print("\n" + "=" * 55)
    print("✨ SELESAI")
    print("=" * 55)


if __name__ == "__main__":
    main()