from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import pyodbc

app = Flask(__name__)
CORS(app)

# ── VERİTABANI BAĞLANTISI ──
def get_db():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=ARAGORN\\SQLEXPRESS;'
        'DATABASE=İnşaat Proje Yönetim Sistemi;'
        'Trusted_Connection=yes;'
    )
    return conn

# ── SAYFALAR ──
@app.route('/')
def anasayfa():
    return render_template('indexAnaSayfa.html')

@app.route('/giris')
def giris():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/personel')
def personel():
    return render_template('personel.html')

@app.route('/musteri')
def musteri():
    return render_template('musteri.html')


# ═══════════════════════════════════════════════
# PROJELER
# ═══════════════════════════════════════════════

@app.route('/api/projeler')
def api_projeler():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.ProjeID, p.ProjeAdı, m.FirmaAdı AS Musteri, p.MüşteriID,
               p.Bütçe, p.HarcananTutar, p.İlerleme, p.Durum,
               p.BaşlangıçTarihi, p.BitişTarihi
        FROM Projeler p
        INNER JOIN Müşteriler m ON p.MüşteriID = m.MüşteriID
    ''')
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append({
            'ProjeID':       row[0],
            'ProjeAdı':      row[1],
            'Musteri':       row[2],
            'MusteriID':     row[3],
            'Butce':         float(row[4]),
            'HarcananTutar': float(row[5]),
            'Ilerleme':      row[6],
            'Durum':         row[7],
            'Baslangic':     str(row[8]),
            'Bitis':         str(row[9]) if row[9] else '',
        })
    conn.close()
    return jsonify(result)

@app.route('/api/projeler', methods=['POST'])
def api_proje_ekle():
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Projeler (ProjeAdı, BaşlangıçTarihi, BitişTarihi, Bütçe, Durum, MüşteriID, İlerleme, HarcananTutar)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', data['ProjeAdı'], data['Baslangic'], data['Bitis'],
         data['Butce'], data['Durum'], data['MusteriID'],
         data.get('Ilerleme', 0), data.get('HarcananTutar', 0))
    conn.commit()
    conn.close()
    return jsonify({'basarili': True})

@app.route('/api/projeler/<int:proje_id>', methods=['PUT'])
def api_proje_guncelle(proje_id):
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Projeler
        SET ProjeAdı = ?, Bütçe = ?, Durum = ?, İlerleme = ?, HarcananTutar = ?
        WHERE ProjeID = ?
    ''', data['ProjeAdı'], data['Butce'], data['Durum'],
         data['Ilerleme'], data['HarcananTutar'], proje_id)
    conn.commit()
    conn.close()
    return jsonify({'basarili': True})

@app.route('/api/projeler/<int:proje_id>', methods=['DELETE'])
def api_proje_sil(proje_id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM Görevler WHERE ProjeID = ?', proje_id)
        cursor.execute('DELETE FROM ProjePersonelBilgi WHERE ProjeID = ?', proje_id)
        cursor.execute('DELETE FROM Stok WHERE ŞantiyeID IN (SELECT ŞantiyeID FROM Şantiyeler WHERE ProjeID = ?)', proje_id)
        cursor.execute('DELETE FROM Siparişler WHERE ŞantiyeID IN (SELECT ŞantiyeID FROM Şantiyeler WHERE ProjeID = ?)', proje_id)
        cursor.execute('DELETE FROM Şantiyeler WHERE ProjeID = ?', proje_id)
        cursor.execute('DELETE FROM Projeler WHERE ProjeID = ?', proje_id)
        conn.commit()
        conn.close()
        return jsonify({'basarili': True})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'basarili': False, 'hata': str(e)})


# ═══════════════════════════════════════════════
# PERSONELLER
# ═══════════════════════════════════════════════

@app.route('/api/personeller')
def api_personeller():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT PersonelID, AdSoyad, Pozisyon, Maaş, Telefon FROM Personeller')
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append({
            'PersonelID': row[0],
            'AdSoyad':    row[1],
            'Pozisyon':   row[2],
            'Maas':       float(row[3]),
            'Telefon':    row[4],
        })
    conn.close()
    return jsonify(result)

@app.route('/api/personeller', methods=['POST'])
def api_personel_ekle():
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Personeller (AdSoyad, Pozisyon, Maaş, Telefon)
        VALUES (?, ?, ?, ?)
    ''', data['AdSoyad'], data['Pozisyon'], data['Maas'], data['Telefon'])
    conn.commit()
    conn.close()
    return jsonify({'basarili': True})

@app.route('/api/personeller/<int:personel_id>', methods=['PUT'])
def api_personel_guncelle(personel_id):
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Personeller
        SET AdSoyad = ?, Pozisyon = ?, Maaş = ?, Telefon = ?
        WHERE PersonelID = ?
    ''', data['AdSoyad'], data['Pozisyon'], data['Maas'], data['Telefon'], personel_id)
    conn.commit()
    conn.close()
    return jsonify({'basarili': True})

@app.route('/api/personeller/<int:personel_id>', methods=['DELETE'])
def api_personel_sil(personel_id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM Görevler WHERE PersonelID = ?', personel_id)
        cursor.execute('DELETE FROM ProjePersonelBilgi WHERE PersonelID = ?', personel_id)
        cursor.execute('DELETE FROM Kullanicilar WHERE PersonelID = ?', personel_id)
        cursor.execute('DELETE FROM Personeller WHERE PersonelID = ?', personel_id)
        conn.commit()
        conn.close()
        return jsonify({'basarili': True})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'basarili': False, 'hata': str(e)})

@app.route('/api/personel/<int:personel_id>')
def api_personel_detay(personel_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT pe.PersonelID, pe.AdSoyad, pe.Pozisyon, pe.Maaş, pe.Telefon,
               p.ProjeAdı
        FROM Personeller pe
        LEFT JOIN ProjePersonelBilgi ppb ON pe.PersonelID = ppb.PersonelID
        LEFT JOIN Projeler p ON ppb.ProjeID = p.ProjeID
        WHERE pe.PersonelID = ?
    ''', personel_id)
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({
            'PersonelID': row[0],
            'AdSoyad':    row[1],
            'Pozisyon':   row[2],
            'Maas':       float(row[3]),
            'Telefon':    row[4],
            'Proje':      row[5] or '—',
        })
    return jsonify({'hata': 'Bulunamadi'})


# ═══════════════════════════════════════════════
# GÖREVLER
# ═══════════════════════════════════════════════

@app.route('/api/gorevler')
def api_gorevler():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT g.GörevID, g.GörevAdı, g.Durum, g.Öncelik,
               g.BaşlangıçTarihi, g.BitişTarihi,
               pe.AdSoyad, p.ProjeAdı, g.ProjeID, g.PersonelID
        FROM Görevler g
        INNER JOIN Personeller pe ON g.PersonelID = pe.PersonelID
        INNER JOIN Projeler    p  ON g.ProjeID    = p.ProjeID
    ''')
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append({
            'GorevID':    row[0],
            'GorevAdi':   row[1],
            'Durum':      row[2],
            'Oncelik':    row[3],
            'Baslangic':  str(row[4]),
            'Bitis':      str(row[5]) if row[5] else '',
            'Personel':   row[6],
            'Proje':      row[7],
            'ProjeID':    row[8],
            'PersonelID': row[9],
        })
    conn.close()
    return jsonify(result)

@app.route('/api/gorevler', methods=['POST'])
def api_gorev_ekle():
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Görevler (ProjeID, PersonelID, GörevAdı, BaşlangıçTarihi, BitişTarihi, Durum, Öncelik)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', data['ProjeID'], data['PersonelID'], data['GorevAdi'],
         data['Baslangic'], data['Bitis'], data['Durum'], data.get('Oncelik', 'Normal'))
    conn.commit()
    conn.close()
    return jsonify({'basarili': True})

@app.route('/api/gorevler/<int:gorev_id>', methods=['PUT'])
def api_gorev_guncelle(gorev_id):
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Görevler SET Durum = ?, Öncelik = ? WHERE GörevID = ?
    ''', data['Durum'], data['Oncelik'], gorev_id)
    conn.commit()
    conn.close()
    return jsonify({'basarili': True})

@app.route('/api/gorevler/<int:gorev_id>', methods=['DELETE'])
def api_gorev_sil(gorev_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Görevler WHERE GörevID = ?', gorev_id)
    conn.commit()
    conn.close()
    return jsonify({'basarili': True})

@app.route('/api/gorevler/personel/<int:personel_id>')
def api_personel_gorevler(personel_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT g.GörevAdı, g.Durum, g.Öncelik,
               g.BaşlangıçTarihi, g.BitişTarihi, p.ProjeAdı
        FROM Görevler g
        INNER JOIN Projeler p ON g.ProjeID = p.ProjeID
        WHERE g.PersonelID = ?
        ORDER BY g.BaşlangıçTarihi
    ''', personel_id)
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{
        'GorevAdi':  r[0],
        'Durum':     r[1],
        'Oncelik':   r[2],
        'Baslangic': str(r[3]),
        'Bitis':     str(r[4]) if r[4] else '',
        'Proje':     r[5],
    } for r in rows])


# ═══════════════════════════════════════════════
# STOK
# ═══════════════════════════════════════════════

@app.route('/api/stok')
def api_stok():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT st.StokID, ma.MalzemeAdı, ma.MalzemeTürü,
               b.BirimAdı, s.ŞantiyeAdı, st.Miktar,
               st.MalzemeID, st.ŞantiyeID
        FROM Stok st
        INNER JOIN Malzemeler ma ON st.MalzemeID = ma.MalzemeID
        INNER JOIN Birimler   b  ON ma.BirimID   = b.BirimID
        INNER JOIN Şantiyeler s  ON st.ŞantiyeID = s.ŞantiyeID
    ''')
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append({
            'StokID':    row[0],
            'Malzeme':   row[1],
            'Tur':       row[2],
            'Birim':     row[3],
            'Santiye':   row[4],
            'Miktar':    float(row[5]),
            'MalzemeID': row[6],
            'SantiyeID': row[7],
        })
    conn.close()
    return jsonify(result)

@app.route('/api/stok', methods=['POST'])
def api_stok_ekle():
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Stok (MalzemeID, ŞantiyeID, Miktar)
        VALUES (?, ?, ?)
    ''', data['MalzemeID'], data['SantiyeID'], data['Miktar'])
    conn.commit()
    conn.close()
    return jsonify({'basarili': True})

@app.route('/api/stok/<int:stok_id>', methods=['PUT'])
def api_stok_guncelle(stok_id):
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE Stok SET Miktar = ? WHERE StokID = ?', data['Miktar'], stok_id)
    conn.commit()
    conn.close()
    return jsonify({'basarili': True})

@app.route('/api/stok/<int:stok_id>', methods=['DELETE'])
def api_stok_sil(stok_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Stok WHERE StokID = ?', stok_id)
    conn.commit()
    conn.close()
    return jsonify({'basarili': True})


# ═══════════════════════════════════════════════
# SİPARİŞLER
# ═══════════════════════════════════════════════

@app.route('/api/siparisler')
def api_siparisler():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT si.SiparişID, ma.MalzemeAdı, si.Miktar,
               te.FirmaAdı, s.ŞantiyeAdı, si.SiparişTarihi, si.Durum,
               si.MalzemeID, si.ŞantiyeID, si.TedarikçiID
        FROM Siparişler si
        INNER JOIN Malzemeler   ma ON si.MalzemeID   = ma.MalzemeID
        INNER JOIN Tedarikçiler te ON si.TedarikçiID = te.TedarikçiID
        INNER JOIN Şantiyeler   s  ON si.ŞantiyeID   = s.ŞantiyeID
    ''')
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append({
            'SiparisID':   row[0],
            'Malzeme':     row[1],
            'Miktar':      float(row[2]),
            'Tedarikci':   row[3],
            'Santiye':     row[4],
            'Tarih':       str(row[5]),
            'Durum':       row[6],
            'MalzemeID':   row[7],
            'SantiyeID':   row[8],
            'TedarikciID': row[9],
        })
    conn.close()
    return jsonify(result)

@app.route('/api/siparisler', methods=['POST'])
def api_siparis_ekle():
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Siparişler (MalzemeID, ŞantiyeID, TedarikçiID, Miktar, SiparişTarihi, Durum)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', data['MalzemeID'], data['SantiyeID'], data['TedarikciID'],
         data['Miktar'], data['Tarih'], data.get('Durum', 'Bekliyor'))
    conn.commit()
    conn.close()
    return jsonify({'basarili': True})

@app.route('/api/siparisler/<int:siparis_id>', methods=['PUT'])
def api_siparis_guncelle(siparis_id):
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE Siparişler SET Durum = ? WHERE SiparişID = ?', data['Durum'], siparis_id)
    conn.commit()
    conn.close()
    return jsonify({'basarili': True})

@app.route('/api/siparisler/<int:siparis_id>', methods=['DELETE'])
def api_siparis_sil(siparis_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Siparişler WHERE SiparişID = ?', siparis_id)
    conn.commit()
    conn.close()
    return jsonify({'basarili': True})


# ═══════════════════════════════════════════════
# MÜŞTERİLER
# ═══════════════════════════════════════════════

@app.route('/api/musteriler')
def api_musteriler():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT MüşteriID, FirmaAdı, İletişim, Email, Adres FROM Müşteriler')
    rows = cursor.fetchall()
    result = [{
        'MusteriID': r[0],
        'FirmaAdi':  r[1],
        'Iletisim':  r[2] or '',
        'Email':     r[3] or '',
        'Adres':     r[4] or '',
    } for r in rows]
    conn.close()
    return jsonify(result)

@app.route('/api/musteriler', methods=['POST'])
def api_musteri_ekle():
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Müşteriler (FirmaAdı, İletişim, Email, Adres)
        VALUES (?, ?, ?, ?)
    ''', data['FirmaAdi'], data['Iletisim'], data['Email'], data['Adres'])
    conn.commit()
    conn.close()
    return jsonify({'basarili': True})

@app.route('/api/musteriler/<int:musteri_id>', methods=['PUT'])
def api_musteri_guncelle(musteri_id):
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Müşteriler SET FirmaAdı = ?, İletişim = ?, Email = ?, Adres = ?
        WHERE MüşteriID = ?
    ''', data['FirmaAdi'], data['Iletisim'], data['Email'], data['Adres'], musteri_id)
    conn.commit()
    conn.close()
    return jsonify({'basarili': True})

@app.route('/api/musteriler/<int:musteri_id>', methods=['DELETE'])
def api_musteri_sil(musteri_id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM Kullanicilar WHERE MusteriID = ?', musteri_id)
        cursor.execute('DELETE FROM Müşteriler WHERE MüşteriID = ?', musteri_id)
        conn.commit()
        conn.close()
        return jsonify({'basarili': True})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'basarili': False, 'hata': str(e)})

@app.route('/api/musteri/<int:musteri_id>')
def api_musteri_projeler(musteri_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.ProjeID, p.ProjeAdı, p.Bütçe, p.HarcananTutar,
               p.İlerleme, p.Durum, p.BaşlangıçTarihi, p.BitişTarihi,
               s.ŞantiyeAdı, s.Lokasyon
        FROM Projeler p
        LEFT JOIN Şantiyeler s ON s.ProjeID = p.ProjeID
        WHERE p.MüşteriID = ?
    ''', musteri_id)
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{
        'ProjeID':       r[0],
        'ProjeAdi':      r[1],
        'Butce':         float(r[2]),
        'HarcananTutar': float(r[3]),
        'Ilerleme':      r[4],
        'Durum':         r[5],
        'Baslangic':     str(r[6]),
        'Bitis':         str(r[7]) if r[7] else '',
        'Santiye':       r[8] or '—',
        'Lokasyon':      r[9] or '—',
    } for r in rows])


# ═══════════════════════════════════════════════
# MALZEMELER, BİRİMLER, ŞANTİYELER, TEDARİKÇİLER (yardımcı)
# ═══════════════════════════════════════════════

@app.route('/api/malzemeler')
def api_malzemeler():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m.MalzemeID, m.MalzemeAdı, m.MalzemeTürü, m.BirimFiyat, b.BirimAdı, m.BirimID
        FROM Malzemeler m
        INNER JOIN Birimler b ON m.BirimID = b.BirimID
    ''')
    rows = cursor.fetchall()
    result = [{
        'MalzemeID':   r[0],
        'MalzemeAdi':  r[1],
        'MalzemeTuru': r[2],
        'BirimFiyat':  float(r[3]),
        'Birim':       r[4],
        'BirimID':     r[5],
    } for r in rows]
    conn.close()
    return jsonify(result)

@app.route('/api/birimler')
def api_birimler():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT BirimID, BirimAdı FROM Birimler')
    rows = cursor.fetchall()
    result = [{'BirimID': r[0], 'BirimAdi': r[1]} for r in rows]
    conn.close()
    return jsonify(result)

@app.route('/api/santiyeler')
def api_santiyeler():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.ŞantiyeID, s.ŞantiyeAdı, s.Lokasyon, s.BaşlamaTarihi, p.ProjeAdı, s.ProjeID
        FROM Şantiyeler s
        INNER JOIN Projeler p ON s.ProjeID = p.ProjeID
    ''')
    rows = cursor.fetchall()
    result = [{
        'SantiyeID':     r[0],
        'SantiyeAdi':    r[1],
        'Lokasyon':      r[2],
        'BaslamaTarihi': str(r[3]),
        'Proje':         r[4],
        'ProjeID':       r[5],
    } for r in rows]
    conn.close()
    return jsonify(result)

@app.route('/api/tedarikciler')
def api_tedarikciler():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT TedarikçiID, FirmaAdı, İletişimNum FROM Tedarikçiler')
    rows = cursor.fetchall()
    result = [{
        'TedarikciID': r[0],
        'FirmaAdi':    r[1],
        'Iletisim':    r[2],
    } for r in rows]
    conn.close()
    return jsonify(result)


# ═══════════════════════════════════════════════
# PROJE TEKLİFLERİ (Müşterilerin yeni proje önerileri)
# ═══════════════════════════════════════════════

@app.route('/api/teklifler')
def api_teklifler():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.TeklifID, m.FirmaAdı, t.ProjeAdı, t.Aciklama,
               t.TahminiButce, t.TeklifTarihi, t.Durum, t.MusteriID
        FROM ProjeTeklifleri t
        INNER JOIN Müşteriler m ON t.MusteriID = m.MüşteriID
        ORDER BY t.TeklifTarihi DESC
    ''')
    rows = cursor.fetchall()
    result = [{
        'TeklifID':     r[0],
        'FirmaAdi':     r[1],
        'ProjeAdi':     r[2],
        'Aciklama':     r[3] or '',
        'TahminiButce': float(r[4]),
        'Tarih':        str(r[5]),
        'Durum':        r[6],
        'MusteriID':    r[7],
    } for r in rows]
    conn.close()
    return jsonify(result)

@app.route('/api/teklifler', methods=['POST'])
def api_teklif_ekle():
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ProjeTeklifleri (MusteriID, ProjeAdı, Aciklama, TahminiButce, TeklifTarihi, Durum)
        VALUES (?, ?, ?, ?, GETDATE(), 'Beklemede')
    ''', data['MusteriID'], data['ProjeAdi'], data.get('Aciklama', ''), data['TahminiButce'])
    conn.commit()
    conn.close()
    return jsonify({'basarili': True})

@app.route('/api/teklifler/<int:teklif_id>', methods=['PUT'])
def api_teklif_guncelle(teklif_id):
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE ProjeTeklifleri SET Durum = ? WHERE TeklifID = ?', data['Durum'], teklif_id)
    conn.commit()
    conn.close()
    return jsonify({'basarili': True})

@app.route('/api/teklifler/<int:teklif_id>', methods=['DELETE'])
def api_teklif_sil(teklif_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM ProjeTeklifleri WHERE TeklifID = ?', teklif_id)
    conn.commit()
    conn.close()
    return jsonify({'basarili': True})

@app.route('/api/teklifler/musteri/<int:musteri_id>')
def api_musteri_teklifler(musteri_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT TeklifID, ProjeAdı, Aciklama, TahminiButce, TeklifTarihi, Durum
        FROM ProjeTeklifleri
        WHERE MusteriID = ?
        ORDER BY TeklifTarihi DESC
    ''', musteri_id)
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{
        'TeklifID':     r[0],
        'ProjeAdi':     r[1],
        'Aciklama':     r[2] or '',
        'TahminiButce': float(r[3]),
        'Tarih':        str(r[4]),
        'Durum':        r[5],
    } for r in rows])


# ═══════════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════════

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    rol = data['rol'].capitalize()
    cursor.execute('''
        SELECT KullaniciID, KullaniciAdi, Rol, PersonelID, MusteriID
        FROM Kullanicilar
        WHERE KullaniciAdi = ? AND Sifre = ? AND Rol = ?
    ''', data['kullaniciAdi'], data['sifre'], rol)
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({
            'basarili':     True,
            'kullaniciAdi': row[1],
            'rol':          row[2].lower(),
            'personelID':   row[3],
            'musteriID':    row[4],
        })
    return jsonify({'basarili': False})


if __name__ == '__main__':
    app.run(debug=True)
