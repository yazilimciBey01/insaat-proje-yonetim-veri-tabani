# insaat-proje-yonetim-veri-tabani
MG İnşaat olarak yapılarımızın takibat ve yönetiminin yapıldığı veri tabanıdır

Sistemi ayağa kaldırmak için:

## Gereksinimler

- Python 3.10+
- Microsoft SQL Server (MSSQL)
- ODBC Driver 17 for SQL Server
- Git (opsiyonel)

---

## Kurulum Adımları

### 1. Projeyi İndir

Proje dosyalarını bilgisayarına indir ve bir klasöre çıkar.
Klasör yapısı şu şekilde olmalıdır:

```
📁 MGInsaat
├── app.py
├── 📁 templates
│   ├── index.html
│   ├── indexAnaSayfa.html
│   ├── admin.html
│   ├── personel.html
│   └── musteri.html
└── 📁 static
    ├── style.css
    ├── logo3.png
    └── bg.png
```

---

### 2. Python Kütüphanelerini Kur

Komut satırını (CMD) aç ve şu komutları sırayla çalıştır:

```bash
pip install flask
pip install pyodbc
pip install flask-cors
```

---

### 3. Veritabanını Hazırla

- Microsoft SQL Server Management Studio'yu aç
- `İnşaat Proje Yönetim Sistemi` adında yeni bir veritabanı oluştur
- Proje klasöründeki SQL dosyasını çalıştırarak tabloları ve verileri oluştur

---

### 4. Bağlantı Ayarını Güncelle

`app.py` dosyasını bir metin editörüyle aç.
Aşağıdaki satırda `ARAGORN\\SQLEXPRESS` yazan kısmı
**kendi bilgisayarının SQL Server adıyla** değiştir:

```python
def get_db():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=ARAGORN\\SQLEXPRESS;'   # ← buraya kendi server adını yaz
        'DATABASE=İnşaat Proje Yönetim Sistemi;'
        'Trusted_Connection=yes;'
    )
    return conn
```

> SQL Server adını öğrenmek için SQL Server Management Studio'yu aç,
> bağlantı ekranında "Server name" alanındaki değeri kopyala.

---

### 5. Uygulamayı Başlat

Komut satırında proje klasörüne git ve şu komutu çalıştır:

```bash
cd Desktop\MGInsaat
python app.py
```

Şu çıktıyı görürsen uygulama çalışıyor demektir:

```
* Running on http://127.0.0.1:5000
```

---

### 6. Tarayıcıda Aç

Herhangi bir tarayıcıda şu adresi aç:

```
http://127.0.0.1:5000
```

---

## Demo Hesapları

| Rol | Kullanıcı Adı | Şifre |
|---|---|---|
| Yönetici | admin | 1234 |
| Personel | ahmet_yilmaz | 1234 |
| Müşteri | karayollar_gm | 1234 |

---

## Teknik Bilgiler

| Bileşen | Teknoloji |
|---|---|
| Veritabanı | Microsoft SQL Server |
| Backend | Python — Flask |
| Frontend | HTML / CSS / JavaScript |
| DB Bağlantısı | pyodbc (ODBC Driver 17) |

---

## Sık Karşılaşılan Hatalar

**"No module named flask" hatası:**
```bash
pip install flask
```

**"Data source name not found" hatası:**
ODBC Driver 17 kurulu değil demektir.
Şu adresten indir: https://aka.ms/odbc17

**"Login failed" hatası:**
`app.py` dosyasındaki SERVER adını kontrol et,
kendi SQL Server adınla eşleştiğinden emin ol.
