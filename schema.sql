-- ============================================================
-- SCHEMA: Aneka Dropship
-- Dibuat untuk Supabase (PostgreSQL)
-- Urutan eksekusi: dari atas ke bawah
-- ============================================================


-- ─────────────────────────────────────────────────────────────
-- 1. COURIERS
--    Tabel master kurir/ekspedisi (14 kurir baku)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS couriers (
  id    INTEGER       PRIMARY KEY,
  nama  VARCHAR(50)   NOT NULL UNIQUE
);

COMMENT ON TABLE  couriers      IS 'Daftar kurir/ekspedisi yang tersedia';
COMMENT ON COLUMN couriers.nama IS 'Nama baku kurir, e.g. SPX, J&T, JNE';


-- ─────────────────────────────────────────────────────────────
-- 2. SUPPLIERS
--    Data supplier/produsen
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS suppliers (
  id       INTEGER       PRIMARY KEY,
  nama     VARCHAR(100)  NOT NULL,
  alamat   TEXT,
  catatan  TEXT
);

COMMENT ON TABLE  suppliers         IS 'Data supplier/produsen produk';
COMMENT ON COLUMN suppliers.catatan IS 'Catatan operasional supplier, e.g. aturan pickup/dropoff';


-- ─────────────────────────────────────────────────────────────
-- 3. SUPPLIER_PRODUCTS
--    Kategori produk yang dijual tiap supplier
--    (bukan katalog individual — ini level kategori/line produk)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS supplier_products (
  id           INTEGER       PRIMARY KEY,
  supplier_id  INTEGER       NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE,
  nama_produk  VARCHAR(255)  NOT NULL,
  kategori     VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_supplier_products_supplier
  ON supplier_products(supplier_id);

COMMENT ON TABLE  supplier_products             IS 'Line produk per supplier (level kategori)';
COMMENT ON COLUMN supplier_products.nama_produk IS 'Nama/deskripsi lini produk supplier';
COMMENT ON COLUMN supplier_products.kategori    IS 'Kategori produk supplier';


-- ─────────────────────────────────────────────────────────────
-- 4. SUPPLIER_COURIERS
--    Junction table: kurir yang didukung tiap supplier
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS supplier_couriers (
  id           INTEGER  PRIMARY KEY,
  supplier_id  INTEGER  NOT NULL REFERENCES suppliers(id)  ON DELETE CASCADE,
  courier_id   INTEGER  NOT NULL REFERENCES couriers(id)   ON DELETE CASCADE,

  UNIQUE (supplier_id, courier_id)
);

CREATE INDEX IF NOT EXISTS idx_supplier_couriers_supplier
  ON supplier_couriers(supplier_id);

CREATE INDEX IF NOT EXISTS idx_supplier_couriers_courier
  ON supplier_couriers(courier_id);

COMMENT ON TABLE supplier_couriers IS 'Kurir yang tersedia per supplier';


-- ─────────────────────────────────────────────────────────────
-- 5. PRODUCTS (katalog)
--    392 produk individual dari anekadropship.id
--    Sudah ada di Supabase — ALTER TABLE untuk tambah supplier_id
-- ─────────────────────────────────────────────────────────────

-- Jalankan ini HANYA jika kolom belum ada:
ALTER TABLE products
  ADD COLUMN IF NOT EXISTS supplier_id INTEGER REFERENCES suppliers(id) ON DELETE SET NULL;

-- Jika tabel products belum ada sama sekali, gunakan CREATE TABLE ini:
-- (Comment out ALTER TABLE di atas jika pakai CREATE TABLE ini)
/*
CREATE TABLE IF NOT EXISTS products (
  id_produk           VARCHAR(20)       PRIMARY KEY,
  title               TEXT              NOT NULL,
  brand               VARCHAR(100)      NOT NULL,
  category            VARCHAR(100)      NOT NULL,
  price_modal         INTEGER,
  price_recommendation INTEGER          NOT NULL,
  margin              INTEGER,
  margin_pct          NUMERIC(8, 2),
  currency            CHAR(3)           NOT NULL DEFAULT 'IDR',
  link                TEXT              NOT NULL,
  image_link          TEXT,
  description         TEXT,
  specs               JSONB,
  is_active           BOOLEAN           NOT NULL DEFAULT true,
  scraped_at          TIMESTAMP,
  supplier_id         INTEGER           REFERENCES suppliers(id) ON DELETE SET NULL,

  CONSTRAINT chk_price_modal_positive
    CHECK (price_modal IS NULL OR price_modal >= 0),
  CONSTRAINT chk_price_rec_positive
    CHECK (price_recommendation > 0)
);
*/

CREATE INDEX IF NOT EXISTS idx_products_brand
  ON products(brand);

CREATE INDEX IF NOT EXISTS idx_products_category
  ON products(category);

CREATE INDEX IF NOT EXISTS idx_products_supplier
  ON products(supplier_id);

CREATE INDEX IF NOT EXISTS idx_products_is_active
  ON products(is_active);

COMMENT ON TABLE  products                  IS 'Katalog produk individual dari anekadropship.id';
COMMENT ON COLUMN products.id_produk        IS 'ID unik produk, format AD-xxxx';
COMMENT ON COLUMN products.price_modal      IS 'Harga modal supplier (IDR), nullable';
COMMENT ON COLUMN products.specs            IS 'Data spesifikasi: berat, volume, ekspedisi, sistem, harga_rekomendasi_raw';
COMMENT ON COLUMN products.supplier_id      IS 'FK ke tabel suppliers';


-- ─────────────────────────────────────────────────────────────
-- RINGKASAN RELASI
-- ─────────────────────────────────────────────────────────────
--
--  couriers (14)
--      ↑ courier_id
--  supplier_couriers (131) ── supplier_id ──→  suppliers (38)
--                                                    ↑ supplier_id
--                                          supplier_products (51)
--                                                    ↑ supplier_id
--                                              products (392)
--
-- ─────────────────────────────────────────────────────────────
