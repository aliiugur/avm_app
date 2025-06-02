# db.py
import sqlite3

DB_PATH = "magazadb.sqlite"

def get_connection():
    return sqlite3.connect(DB_PATH)

# ----- MAĞAZALAR -----

def get_all_magazalar():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Magazalar")
    results = cursor.fetchall()
    conn.close()
    return results

def get_magaza_by_id(magaza_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Magazalar WHERE id=?", (magaza_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def add_magaza(isim, aciklama, tur):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Magazalar (isim, aciklama, tur) VALUES (?, ?, ?)",
        (isim, aciklama, tur)
    )
    conn.commit()
    conn.close()

# ----- PERSONELLER -----

def get_personeller_by_magaza(magaza_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Personeller WHERE magaza_id=?", (magaza_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def add_personel(isim, pozisyon, maas, magaza_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Personeller (isim, pozisyon, maas, magaza_id) VALUES (?, ?, ?, ?)",
        (isim, pozisyon, maas, magaza_id)
    )
    conn.commit()
    conn.close()

def update_personel(personel_id, pozisyon, maas):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Personeller SET pozisyon=?, maas=? WHERE id=?",
        (pozisyon, maas, personel_id)
    )
    conn.commit()
    conn.close()

def delete_personel(personel_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Personeller WHERE id=?", (personel_id,))
    conn.commit()
    conn.close()

# ----- STOK -----

def get_stok_by_magaza(magaza_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Stok WHERE magaza_id=?", (magaza_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def add_stok(isim, adet, fiyat, magaza_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Stok (isim, adet, fiyat, magaza_id) VALUES (?, ?, ?, ?)",
        (isim, adet, fiyat, magaza_id)
    )
    conn.commit()
    conn.close()

# Bu fonksiyonları db.py dosyanızın STOK bölümüne ekleyin

def update_stok(stok_id, isim, adet, fiyat):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Stok SET isim=?, adet=?, fiyat=? WHERE id=?",
        (isim, adet, fiyat, stok_id)
    )
    conn.commit()
    conn.close()

def delete_stok(stok_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Stok WHERE id=?", (stok_id,))
    conn.commit()
    conn.close()

def get_stok_by_id(stok_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Stok WHERE id=?", (stok_id,))
    result = cursor.fetchone()
    conn.close()
    return result

# ----- MÜŞTERİLER -----

def get_all_musteriler():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Musteriler")
    results = cursor.fetchall()
    conn.close()
    return results

def add_musteri(isim, telefon, email, adres):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Musteriler (isim, telefon, email, adres) VALUES (?, ?, ?, ?)",
        (isim, telefon, email, adres)
    )
    conn.commit()
    musteri_id = cursor.lastrowid
    conn.close()
    return musteri_id

# ----- SİPARİŞLER -----

def add_siparis(musteri_id, magaza_id, toplam_fiyat, siparis_tarihi):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Siparisler (musteri_id, magaza_id, toplam_fiyat, siparis_tarihi) VALUES (?, ?, ?, ?)",
        (musteri_id, magaza_id, toplam_fiyat, siparis_tarihi)
    )
    conn.commit()
    siparis_id = cursor.lastrowid
    conn.close()
    return siparis_id

def add_siparis_detay(siparis_id, stok_id, adet, birim_fiyat):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO SiparisDetay (siparis_id, stok_id, adet, birim_fiyat) VALUES (?, ?, ?, ?)",
        (siparis_id, stok_id, adet, birim_fiyat)
    )
    conn.commit()
    conn.close()

def update_stok_adet(stok_id, yeni_adet):
    """Stok adedini günceller (satış sonrası)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Stok SET adet=? WHERE id=?",
        (yeni_adet, stok_id)
    )
    conn.commit()
    conn.close()

def get_musteri_siparisleri(musteri_id):
    """Müşterinin geçmiş siparişleri"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, s.toplam_fiyat, s.siparis_tarihi, m.isim as magaza_isim
        FROM Siparisler s
        JOIN Magazalar m ON s.magaza_id = m.id
        WHERE s.musteri_id = ?
        ORDER BY s.siparis_tarihi DESC
    """, (musteri_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_siparis_detaylari(siparis_id):
    """Sipariş detaylarını getir"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sd.adet, sd.birim_fiyat, st.isim as urun_isim
        FROM SiparisDetay sd
        JOIN Stok st ON sd.stok_id = st.id
        WHERE sd.siparis_id = ?
    """, (siparis_id,))
    results = cursor.fetchall()
    conn.close()
    return results

# ----- VERİTABANI TABLOSU OLUŞTURMA (eğer yoksa) -----
def create_tables_if_not_exists():
    """Gerekli tabloları oluştur (eğer yoksa)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Müşteriler tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Musteriler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT NOT NULL,
            telefon TEXT,
            email TEXT,
            adres TEXT
        )
    """)
    
    # Siparişler tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Siparisler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            musteri_id INTEGER,
            magaza_id INTEGER,
            toplam_fiyat REAL,
            siparis_tarihi TEXT,
            FOREIGN KEY (musteri_id) REFERENCES Musteriler (id),
            FOREIGN KEY (magaza_id) REFERENCES Magazalar (id)
        )
    """)
    
    # Sipariş detay tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SiparisDetay (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            siparis_id INTEGER,
            stok_id INTEGER,
            adet INTEGER,
            birim_fiyat REAL,
            FOREIGN KEY (siparis_id) REFERENCES Siparisler (id),
            FOREIGN KEY (stok_id) REFERENCES Stok (id)
        )
    """)
    
    conn.commit()
    conn.close()