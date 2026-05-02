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

# ── API: PROJELERs ──
@app.route('/api/projeler')
def api_projeler():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.ProjeID, p.ProjeAdı, m.FirmaAdı AS Musteri,
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
            'Butce':         float(row[3]),
            'HarcananTutar': float(row[4]),
            'Ilerleme':      row[5],
            'Durum':         row[6],
            'Baslangic':     str(row[7]),
            'Bitis':         str(row[8]),
        })
    conn.close()
    return jsonify(result)

# ── API: PERSONELLER ──
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

# ── API: PERSONEL DETAY ──
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

# ── API: GÖREVLER (tüm) ──
@app.route('/api/gorevler')
def api_gorevler():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT g.GörevID, g.GörevAdı, g.Durum, g.Öncelik,
               g.BaşlangıçTarihi, g.BitişTarihi,
               pe.AdSoyad, p.ProjeAdı
        FROM Görevler g
        INNER JOIN Personeller pe ON g.PersonelID = pe.PersonelID
        INNER JOIN Projeler    p  ON g.ProjeID    = p.ProjeID
    ''')
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append({
            'GorevID':   row[0],
            'GorevAdi':  row[1],
            'Durum':     row[2],
            'Oncelik':   row[3],
            'Baslangic': str(row[4]),
            'Bitis':     str(row[5]),
            'Personel':  row[6],
            'Proje':     row[7],
        })
    conn.close()
    return jsonify(result)

# ── API: PERSONEL GÖREVLERİ ──
@app.route('/api/gorevler/<int:personel_id>')
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
        'Bitis':     str(r[4]),
        'Proje':     r[5],
    } for r in rows])

# ── API: STOK ──
@app.route('/api/stok')
def api_stok():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT st.StokID, ma.MalzemeAdı, ma.MalzemeTürü,
               b.BirimAdı, s.ŞantiyeAdı, st.Miktar
        FROM Stok st
        INNER JOIN Malzemeler ma ON st.MalzemeID = ma.MalzemeID
        INNER JOIN Birimler   b  ON ma.BirimID   = b.BirimID
        INNER JOIN Şantiyeler s  ON st.ŞantiyeID = s.ŞantiyeID
    ''')
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append({
            'StokID':  row[0],
            'Malzeme': row[1],
            'Tur':     row[2],
            'Birim':   row[3],
            'Santiye': row[4],
            'Miktar':  float(row[5]),
        })
    conn.close()
    return jsonify(result)

# ── API: SİPARİŞLER ──
@app.route('/api/siparisler')
def api_siparisler():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT si.SiparişID, ma.MalzemeAdı, si.Miktar,
               te.FirmaAdı, s.ŞantiyeAdı, si.SiparişTarihi, si.Durum
        FROM Siparişler si
        INNER JOIN Malzemeler   ma ON si.MalzemeID   = ma.MalzemeID
        INNER JOIN Tedarikçiler te ON si.TedarikçiID = te.TedarikçiID
        INNER JOIN Şantiyeler   s  ON si.ŞantiyeID   = s.ŞantiyeID
    ''')
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append({
            'SiparisID': row[0],
            'Malzeme':   row[1],
            'Miktar':    float(row[2]),
            'Tedarikci': row[3],
            'Santiye':   row[4],
            'Tarih':     str(row[5]),
            'Durum':     row[6],
        })
    conn.close()
    return jsonify(result)

# ── API: MÜŞTERİ PROJELERİ ──
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
        'Bitis':         str(r[7]),
        'Santiye':       r[8] or '—',
        'Lokasyon':      r[9] or '—',
    } for r in rows])

# ── API: LOGIN ──
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()

    # Gelen rolü capitalize et: admin → Admin
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
            'rol':          row[2].lower(),  # Frontend'e küçük harfle gönder
            'personelID':   row[3],
            'musteriID':    row[4],
        })
    return jsonify({'basarili': False})

if __name__ == '__main__':
    app.run(debug=True)
