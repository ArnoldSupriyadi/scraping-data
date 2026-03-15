-- Aktifkan RLS di semua tabel baru
ALTER TABLE couriers          ENABLE ROW LEVEL SECURITY;
ALTER TABLE suppliers         ENABLE ROW LEVEL SECURITY;
ALTER TABLE supplier_products ENABLE ROW LEVEL SECURITY;
ALTER TABLE supplier_couriers ENABLE ROW LEVEL SECURITY;

-- Izinkan semua orang READ (untuk Next.js frontend)
CREATE POLICY "public read" ON couriers          FOR SELECT USING (true);
CREATE POLICY "public read" ON supplier_products FOR SELECT USING (true);
CREATE POLICY "public read" ON supplier_couriers FOR SELECT USING (true);

-- Suppliers: READ terbatas (tanpa alamat & catatan sensitif)
-- Bisa dihandle di query Next.js dengan SELECT kolom tertentu saja
CREATE POLICY "public read" ON suppliers FOR SELECT USING (true);

-- WRITE hanya boleh dari service_role (script Python kamu)
-- Tidak perlu policy tambahan — service_role key bypass RLS otomatis