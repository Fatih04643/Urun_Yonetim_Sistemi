import sys
import hashlib
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import sqlite3
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve

# Veritabanı bağlantısı
baglanti = sqlite3.connect("urunler.db")
islem = baglanti.cursor()

# Ürün tablosu oluşturma
islem.execute("""
CREATE TABLE IF NOT EXISTS urun (
    urunKodu INTEGER PRIMARY KEY,
    urunAdi TEXT,
    birimFiyat INTEGER,
    stokMiktari INTEGER,
    urunAciklamasi TEXT,
    marka TEXT,
    kategori TEXT
)
""")

# Kullanıcılar tablosu oluşturma
islem.execute("""
CREATE TABLE IF NOT EXISTS kullanicilar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kullaniciAdi TEXT UNIQUE,
    sifre TEXT,
    email TEXT,
    yetki TEXT DEFAULT 'kullanici'
)
""")

# Örnek admin kullanıcısını ekleme (eğer yoksa)
admin_sifre = hashlib.sha256("1234".encode()).hexdigest()
islem.execute("SELECT * FROM kullanicilar WHERE kullaniciAdi = ?", ("admin",))
if not islem.fetchone():
    islem.execute(
        "INSERT INTO kullanicilar (kullaniciAdi, sifre, email, yetki) VALUES (?, ?, ?, ?)",
        ("admin", admin_sifre, "admin@example.com", "admin"),
    )

baglanti.commit()

ORTAK_STIL = """
    QWidget {
        background-color: #2c3e50;
        font-family: 'Segoe UI';
        color: MediumSeaGreen;
    }
    QLineEdit, QTableWidget {
        padding: 8px 12px;
        border: none;
        border-radius: 8px;
        background-color: rgb(240, 240, 240);
        color: black;
        font-size: 14px;
    }
    QPushButton {
        background-color: #1abc9c;
        color: black;
        padding: 10px;
        font-size: 15px;
        border: none;
        border-radius: 8px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #16a085;
    }
    QTableWidget {
        gridline-color: #16a085;
        font-size: 13px;
    }
    QLabel {
        color: white;
    }
    QTabWidget::pane {
        border: none;
        background-color: #2c3e50;
    }
    QTabBar::tab {
        background-color: #34495e;
        color: white;
        padding: 8px 12px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background-color: #1abc9c;
    }
    QMessageBox {
        background-color: #2c3e50;
    }
    QMessageBox QPushButton {
        min-width: 100px;
    }
"""


class KayitPenceresi(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Yeni Kullanıcı Kaydı")
        self.setFixedSize(420, 400)
        self.setStyleSheet(ORTAK_STIL)

        ana_layout = QVBoxLayout()
        ana_layout.setAlignment(QtCore.Qt.AlignCenter)

        kart = QFrame()
        kart.setStyleSheet("""
            QFrame {
                background-color: rgb(233,177,47);
                border-radius: 12px;
                border: 2px solid #374151;
            }
        """)
        kart.setFixedSize(350, 340)

        kart_layout = QVBoxLayout()
        kart_layout.setContentsMargins(25, 25, 25, 25)
        kart_layout.setSpacing(15)

        baslik = QLabel("Yeni Kullanıcı Kaydı")
        baslik.setObjectName("baslik")
        baslik.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: black;
            margin-bottom: 2px;
            border:none;
        """)
        baslik.setAlignment(QtCore.Qt.AlignCenter)

        self.kullanici_adi = QLineEdit()
        self.kullanici_adi.setPlaceholderText("Kullanıcı Adı")

        self.email = QLineEdit()
        self.email.setPlaceholderText("E-posta Adresi")

        self.sifre = QLineEdit()
        self.sifre.setPlaceholderText("Şifre")
        self.sifre.setEchoMode(QLineEdit.Password)

        self.sifre_tekrar = QLineEdit()
        self.sifre_tekrar.setPlaceholderText("Şifre Tekrar")
        self.sifre_tekrar.setEchoMode(QLineEdit.Password)

        butonlar_layout = QHBoxLayout()

        self.btn_kaydet = QPushButton("Kayıt Ol")
        self.btn_kaydet.clicked.connect(self.kullanici_kaydet)
        self.btn_kaydet.setStyleSheet("""background-color:rgb(223,110,24);""")

        self.btn_iptal = QPushButton("İptal")
        self.btn_iptal.clicked.connect(self.close)
        self.btn_iptal.setStyleSheet("""
            background-color: rgb(223,110,24);
        """)

        butonlar_layout.addWidget(self.btn_iptal)
        butonlar_layout.addWidget(self.btn_kaydet)

        kart_layout.addWidget(baslik)
        kart_layout.addWidget(self.kullanici_adi)
        kart_layout.addWidget(self.email)
        kart_layout.addWidget(self.sifre)
        kart_layout.addWidget(self.sifre_tekrar)
        kart_layout.addLayout(butonlar_layout)

        kart.setLayout(kart_layout)
        ana_layout.addWidget(kart)
        self.setLayout(ana_layout)

    def kullanici_kaydet(self):
        kullanici_adi = self.kullanici_adi.text()
        email = self.email.text()
        sifre = self.sifre.text()
        sifre_tekrar = self.sifre_tekrar.text()

        # Validasyon
        if not kullanici_adi or not email or not sifre or not sifre_tekrar:
            QMessageBox.warning(self, "Hata", "Tüm alanlar doldurulmalıdır!")
            return

        if sifre != sifre_tekrar:
            QMessageBox.warning(self, "Hata", "Şifreler eşleşmiyor!")
            return

        if len(sifre) < 4:
            QMessageBox.warning(self, "Hata", "Şifre en az 4 karakter olmalıdır!")
            return

        # Email validasyonu basit kontrol
        if not "@" in email or not "." in email:
            QMessageBox.warning(self, "Hata", "Geçerli bir e-posta adresi giriniz!")
            return

        # Kullanıcı adı kontrolü
        islem.execute(
            "SELECT * FROM kullanicilar WHERE kullaniciAdi = ?", (kullanici_adi,)
        )
        if islem.fetchone():
            QMessageBox.warning(self, "Hata", "Bu kullanıcı adı zaten kullanılmakta!")
            return

        # Şifre hashleme
        hash_sifre = hashlib.sha256(sifre.encode()).hexdigest()

        try:
            islem.execute(
                "INSERT INTO kullanicilar (kullaniciAdi, sifre, email) VALUES (?, ?, ?)",
                (kullanici_adi, hash_sifre, email),
            )
            baglanti.commit()
            QMessageBox.information(self, "Başarılı", "Kullanıcı kaydı oluşturuldu!")
            self.close()
        except Exception as e:
            QMessageBox.warning(self, "Hata", str(e))


class GirisPenceresi(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ürün Yönetimi - Giriş")
        self.setFixedSize(420, 340)
        self.setStyleSheet(ORTAK_STIL)

        ana_layout = QVBoxLayout()
        
        ana_layout.setAlignment(QtCore.Qt.AlignCenter)

        kart = QFrame()
        kart.setStyleSheet("""
            QFrame {
                background-color: rgb(233,177,47);
                border-radius: 12px;
                border: 2px solid #374151;
            }
        """)
        kart.setFixedSize(350, 280)

        kart_layout = QVBoxLayout()
        kart_layout.setContentsMargins(25, 25, 25, 25)
        kart_layout.setSpacing(15)

        baslik = QLabel("Kullanıcı Girişi")
        baslik.setObjectName("baslik")
        baslik.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: black;
            margin-bottom: 10px;
            border:none;
        """)
        baslik.setAlignment(QtCore.Qt.AlignCenter)

        self.kullanici_adi = QLineEdit()
        self.kullanici_adi.setPlaceholderText("Kullanıcı Adı")

        self.sifre = QLineEdit()
        self.sifre.setPlaceholderText("Şifre")
        self.sifre.setEchoMode(QLineEdit.Password)

        butonlar_layout = QHBoxLayout()

        self.btn_kayit = QPushButton("Kayıt Ol")
        self.btn_kayit.clicked.connect(self.kayit_ac)
        self.btn_kayit.setStyleSheet("""
            background-color: rgb(223,110,24);
        """)

        self.btn_giris = QPushButton("Giriş Yap")
        self.btn_giris.clicked.connect(self.giris_kontrol)
        self.btn_giris.setStyleSheet("""background-color:rgb(223,110,24)""")

        butonlar_layout.addWidget(self.btn_kayit)
        butonlar_layout.addWidget(self.btn_giris)

        kart_layout.addWidget(baslik)
        kart_layout.addWidget(self.kullanici_adi)
        kart_layout.addWidget(self.sifre)
        kart_layout.addLayout(butonlar_layout)

        kart.setLayout(kart_layout)
        ana_layout.addWidget(kart)
        self.setLayout(ana_layout)

        # Animasyon için property
        self.setProperty("opacity", 2.0)
        self.fade_in()

    def fade_in(self):
        """Pencere açılışında fade-in animasyonu"""
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()

    def kayit_ac(self):
        self.kayit_pencere = KayitPenceresi()  
        self.kayit_pencere.show()

    def giris_kontrol(self):
        kullanici = self.kullanici_adi.text()
        sifre = self.sifre.text()

        if not kullanici or not sifre:
            QMessageBox.warning(self, "Hata", "Kullanıcı adı ve şifre giriniz!")
            return

        # Şifreyi hashleme
        hash_sifre = hashlib.sha256(sifre.encode()).hexdigest()

        # Veritabanında kullanıcıyı arama
        islem.execute(
            "SELECT * FROM kullanicilar WHERE kullaniciAdi = ? AND sifre = ?",
            (kullanici, hash_sifre),
        )
        kullanici_bilgi = islem.fetchone()

        if kullanici_bilgi:
            self.ana_pencere = AnaPencere(kullanici_bilgi)
            self.ana_pencere.show()
            self.close()
        else:
            QMessageBox.warning(
                self, "Hatalı Giriş", "Kullanıcı adı veya şifre hatalı!"
            )


class KullaniciPenceresi(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kullanıcı Yönetimi")
        self.setGeometry(200, 200, 600, 400)
        self.setStyleSheet(ORTAK_STIL)

        layout = QVBoxLayout()

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(4)
        self.tablo.setHorizontalHeaderLabels(
            ["ID", "Kullanıcı Adı", "E-posta", "Yetki"]
        )

        butonlar_layout = QHBoxLayout()
        self.btn_yeni = QPushButton("Yeni Kullanıcı")
        self.btn_sil = QPushButton("Seçili Kullanıcıyı Sil")
        self.btn_sil.setStyleSheet("background-color: #e74c3c;")

        butonlar_layout.addWidget(self.btn_yeni)
        butonlar_layout.addWidget(self.btn_sil)

        layout.addWidget(self.tablo)
        layout.addLayout(butonlar_layout)

        self.setLayout(layout)

        self.btn_yeni.clicked.connect(self.yeni_kullanici_ac)
        self.btn_sil.clicked.connect(self.kullanici_sil)

        self.kullanicilari_listele()

    def kullanicilari_listele(self):
        islem.execute("SELECT id, kullaniciAdi, email, yetki FROM kullanicilar")
        veriler = islem.fetchall()
        self.tablo.setRowCount(len(veriler))
        for i, satir in enumerate(veriler):
            for j, deger in enumerate(satir):
                self.tablo.setItem(i, j, QTableWidgetItem(str(deger)))

    def yeni_kullanici_ac(self):
        self.kayit_pencere = KayitPenceresi(self)
        self.kayit_pencere.show()
        # Kayıt penceresini kapatınca tabloyu güncelle
        self.kayit_pencere.destroyed.connect(self.kullanicilari_listele)

    def kullanici_sil(self):
        secili_satir = self.tablo.currentRow()
        if secili_satir == -1:
            QMessageBox.warning(self, "Hata", "Lütfen silinecek kullanıcıyı seçin!")
            return

        kullanici_id = self.tablo.item(secili_satir, 0).text()

        cevap = QMessageBox.question(
            self,
            "Kullanıcı Sil",
            "Bu kullanıcıyı silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if cevap == QMessageBox.Yes:
            islem.execute("DELETE FROM kullanicilar WHERE id = ?", (kullanici_id,))
            baglanti.commit()
            self.kullanicilari_listele()
            QMessageBox.information(self, "Başarılı", "Kullanıcı silindi!")


class AnaPencere(QWidget):
    def __init__(self, kullanici_bilgi=None):
        super().__init__()
        self.kullanici_bilgi = kullanici_bilgi
        self.setWindowTitle("Ürün Ekleme Uygulaması")
        self.setGeometry(200, 200, 400, 400)
        self.setStyleSheet(ORTAK_STIL)

        ana_layout = QVBoxLayout()

        # Karşılama mesajı
        if kullanici_bilgi:
            hosgeldin = QLabel(f"Hoşgeldin, {kullanici_bilgi[1]}!")
            hosgeldin.setStyleSheet(
                "color: white; font-size: 16px; font-weight: bold; margin-bottom: 10px;"
            )
            hosgeldin.setAlignment(QtCore.Qt.AlignCenter)
            ana_layout.addWidget(hosgeldin)

        # İçerik kart
        kart = QFrame()
        kart.setStyleSheet("background-color: #3c4f65; border-radius: 12px;")

        kart_layout = QVBoxLayout()
        kart_layout.setContentsMargins(20, 20, 20, 20)
        kart_layout.setSpacing(15)

        self.btn_ekle = QPushButton("Ürün Ekle")
        self.btn_ekle.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))

        self.btn_listele = QPushButton("Tüm Ürünleri Listele")
        self.btn_listele.setIcon(
            self.style().standardIcon(QStyle.SP_FileDialogListView)
        )

        self.btn_kategori = QPushButton("Kategoriye Göre Listele")
        self.btn_kategori.setIcon(
            self.style().standardIcon(QStyle.SP_FileDialogDetailedView)
        )

        self.btn_guncelle = QPushButton("Kayıt Güncelle/Sil")
        self.btn_guncelle.setIcon(
            self.style().standardIcon(QStyle.SP_FileDialogContentsView)
        )

        # Admin ise kullanıcı yönetimi butonunu ekle
        self.btn_kullanicilar = None
        if kullanici_bilgi and kullanici_bilgi[4] == "admin":
            self.btn_kullanicilar = QPushButton("Kullanıcı Yönetimi")
            self.btn_kullanicilar.setIcon(
                self.style().standardIcon(QStyle.SP_DialogApplyButton)
            )
            self.btn_kullanicilar.setStyleSheet("background-color: #3498db;")

        self.btn_kapat = QPushButton("Çıkış")
        self.btn_kapat.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
        self.btn_kapat.setStyleSheet("background-color: #e74c3c;")

        kart_layout.addWidget(self.btn_ekle)
        kart_layout.addWidget(self.btn_listele)
        kart_layout.addWidget(self.btn_kategori)
        kart_layout.addWidget(self.btn_guncelle)
        if self.btn_kullanicilar:
            kart_layout.addWidget(self.btn_kullanicilar)
        kart_layout.addWidget(self.btn_kapat)

        kart.setLayout(kart_layout)
        ana_layout.addWidget(kart)
        self.setLayout(ana_layout)

        self.btn_ekle.clicked.connect(self.urun_ekle_ac)
        self.btn_listele.clicked.connect(self.urun_listele_ac)
        self.btn_kategori.clicked.connect(self.kategori_listele_ac)
        self.btn_guncelle.clicked.connect(self.guncelle_sil_ac)
        if self.btn_kullanicilar:
            self.btn_kullanicilar.clicked.connect(self.kullanici_yonetimi_ac)
        self.btn_kapat.clicked.connect(self.close)

        # Animasyon için
        self.setProperty("opacity", 1.2)
        self.fade_in()

    def fade_in(self):
        """Pencere açılışında fade-in animasyonu"""
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()

    def urun_ekle_ac(self):
        self.ekle_pencere = UrunEklePencere()
        self.ekle_pencere.show()

    def urun_listele_ac(self):
        self.listele_pencere = UrunListelePencere()
        self.listele_pencere.show()

    def kategori_listele_ac(self):
        self.kategori_pencere = KategoriListelePencere()
        self.kategori_pencere.show()

    def guncelle_sil_ac(self):
        self.guncelle_pencere = GuncelleSilPencere()
        self.guncelle_pencere.show()

    def kullanici_yonetimi_ac(self):
        self.kullanici_pencere = KullaniciPenceresi()
        self.kullanici_pencere.show()


class UrunEklePencere(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ürün Ekle")
        self.setGeometry(200, 200, 400, 350)
        self.setStyleSheet(ORTAK_STIL)

        form = QFormLayout()
        self.kod = QLineEdit()
        self.ad = QLineEdit()
        self.fiyat = QLineEdit()
        self.stok = QLineEdit()
        self.aciklama = QLineEdit()
        self.marka = QLineEdit()
        self.kategori = QLineEdit()
        self.ekle_btn = QPushButton("Ekle")

        form.addRow("Ürün Kodu:", self.kod)
        form.addRow("Ürün Adı:", self.ad)
        form.addRow("Birim Fiyat:", self.fiyat)
        form.addRow("Stok Miktarı:", self.stok)
        form.addRow("Açıklama:", self.aciklama)
        form.addRow("Marka:", self.marka)
        form.addRow("Kategori:", self.kategori)
        form.addRow(self.ekle_btn)

        self.setLayout(form)
        self.ekle_btn.clicked.connect(self.kaydet)

    def kaydet(self):
        try:
            islem.execute(
                "INSERT INTO urun VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    int(self.kod.text()),
                    self.ad.text(),
                    int(self.fiyat.text()),
                    int(self.stok.text()),
                    self.aciklama.text(),
                    self.marka.text(),
                    self.kategori.text(),
                ),
            )
            baglanti.commit()
            QMessageBox.information(self, "Başarılı", "Ürün başarıyla eklendi")
            self.temizle()
        except Exception as e:
            QMessageBox.warning(self, "Hata", str(e))

    def temizle(self):
        for field in [
            self.kod,
            self.ad,
            self.fiyat,
            self.stok,
            self.aciklama,
            self.marka,
            self.kategori,
        ]:
            field.clear()
        self.kod.setFocus()


class UrunListelePencere(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ürünleri Listele")
        self.setGeometry(200, 200, 800, 500)
        self.setStyleSheet(ORTAK_STIL)

        layout = QVBoxLayout()
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(7)
        self.tablo.setHorizontalHeaderLabels(
            ["Kodu", "Adı", "Fiyat", "Stok", "Açıklama", "Marka", "Kategori"]
        )
        layout.addWidget(self.tablo)

        self.setLayout(layout)
        self.listele()

    def listele(self):
        islem.execute("SELECT * FROM urun")
        veriler = islem.fetchall()
        self.tablo.setRowCount(len(veriler))
        for i, satir in enumerate(veriler):
            for j, deger in enumerate(satir):
                self.tablo.setItem(i, j, QTableWidgetItem(str(deger)))

        # Tablo sütunlarını içeriğe göre genişlet
        self.tablo.resizeColumnsToContents()


class KategoriListelePencere(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kategoriye Göre Listele")
        self.setGeometry(200, 200, 800, 500)
        self.setStyleSheet(ORTAK_STIL)

        self.layout = QVBoxLayout()

        # Kategori seçim kısmı
        form_layout = QHBoxLayout()

        self.kategori_input = QLineEdit()
        self.kategori_input.setPlaceholderText("Kategori giriniz")
        self.btn_listele = QPushButton("Listele")

        form_layout.addWidget(QLabel("Kategori:"))
        form_layout.addWidget(self.kategori_input, 1)
        form_layout.addWidget(self.btn_listele)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(7)
        self.tablo.setHorizontalHeaderLabels(
            ["Kodu", "Adı", "Fiyat", "Stok", "Açıklama", "Marka", "Kategori"]
        )

        self.layout.addLayout(form_layout)
        self.layout.addWidget(self.tablo)
        self.setLayout(self.layout)

        self.btn_listele.clicked.connect(self.listele)

    def listele(self):
        kategori = self.kategori_input.text()
        if not kategori:
            QMessageBox.warning(self, "Hata", "Lütfen bir kategori giriniz!")
            return

        islem.execute("SELECT * FROM urun WHERE kategori = ?", (kategori,))
        veriler = islem.fetchall()
        self.tablo.setRowCount(len(veriler))

        if len(veriler) == 0:
            QMessageBox.information(
                self, "Bilgi", f"'{kategori}' kategorisinde ürün bulunamadı!"
            )

        for i, satir in enumerate(veriler):
            for j, deger in enumerate(satir):
                self.tablo.setItem(i, j, QTableWidgetItem(str(deger)))

        # Tablo sütunlarını içeriğe göre genişlet
        self.tablo.resizeColumnsToContents()


class GuncelleSilPencere(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kayıt Güncelle/Sil")
        self.setGeometry(200, 200, 800, 500)
        self.setStyleSheet(ORTAK_STIL)

        ana_layout = QVBoxLayout()

        # Ürün seçim kısmı
        ust_layout = QHBoxLayout()
        self.kod_input = QLineEdit()
        self.kod_input.setPlaceholderText("Ürün Kodu")
        self.btn_ara = QPushButton("Ara")

        ust_layout.addWidget(QLabel("Ürün Kodu:"))
        ust_layout.addWidget(self.kod_input, 1)
        ust_layout.addWidget(self.btn_ara)

        # Ürün bilgileri
        self.form_layout = QFormLayout()

        self.urun_adi = QLineEdit()
        self.birim_fiyat = QLineEdit()
        self.stok_miktari = QLineEdit()
        self.aciklama = QLineEdit()
        self.marka = QLineEdit()
        self.kategori = QLineEdit()

        self.form_layout.addRow("Ürün Adı:", self.urun_adi)
        self.form_layout.addRow("Birim Fiyat:", self.birim_fiyat)
        self.form_layout.addRow("Stok Miktarı:", self.stok_miktari)
        self.form_layout.addRow("Açıklama:", self.aciklama)
        self.form_layout.addRow("Marka:", self.marka)
        self.form_layout.addRow("Kategori:", self.kategori)

        # Butonlar
        butonlar_layout = QHBoxLayout()
        self.btn_sil = QPushButton("Sil")
        self.btn_sil.setStyleSheet("background-color: #e74c3c;")
        self.btn_guncelle = QPushButton("Güncelle")

        butonlar_layout.addWidget(self.btn_sil)
        butonlar_layout.addWidget(self.btn_guncelle)

        # Tüm ürünler tablosu
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(7)
        self.tablo.setHorizontalHeaderLabels(
            ["Kodu", "Adı", "Fiyat", "Stok", "Açıklama", "Marka", "Kategori"]
        )

        ana_layout.addLayout(ust_layout)
        ana_layout.addLayout(self.form_layout)
        ana_layout.addLayout(butonlar_layout)
        ana_layout.addWidget(QLabel("Tüm Ürünler:"))
        ana_layout.addWidget(self.tablo)

        self.setLayout(ana_layout)

        # Bağlantılar
        self.btn_ara.clicked.connect(self.urun_ara)
        self.btn_sil.clicked.connect(self.kayit_sil)
        self.btn_guncelle.clicked.connect(self.kayit_guncelle)
        self.tablo.cellDoubleClicked.connect(self.tablo_secim)

        # Tablo doldur
        self.tum_urunleri_listele()

    def tablo_secim(self, row, column):
        """Tabloda bir ürüne çift tıklandığında formu doldur"""
        urun_kodu = self.tablo.item(row, 0).text()
        self.kod_input.setText(urun_kodu)
        self.urun_ara()

    def tum_urunleri_listele(self):
        """Tüm ürünleri tabloda göster"""
        islem.execute("SELECT * FROM urun")
        veriler = islem.fetchall()
        self.tablo.setRowCount(len(veriler))

        for i, satir in enumerate(veriler):
            for j, deger in enumerate(satir):
                self.tablo.setItem(i, j, QTableWidgetItem(str(deger)))

        # Tablo sütunlarını içeriğe göre genişlet
        self.tablo.resizeColumnsToContents()

    def urun_ara(self):
        """Ürün koduna göre ürün bilgilerini form alanlarına doldur"""
        try:
            kod = int(self.kod_input.text())
        except:
            QMessageBox.warning(self, "Hata", "Geçerli bir ürün kodu giriniz!")
            return

        islem.execute("SELECT * FROM urun WHERE urunKodu = ?", (kod,))
        urun = islem.fetchone()

        if urun:
            self.urun_adi.setText(str(urun[1]))
            self.birim_fiyat.setText(str(urun[2]))
            self.stok_miktari.setText(str(urun[3]))
            self.aciklama.setText(str(urun[4]))
            self.marka.setText(str(urun[5]))
            self.kategori.setText(str(urun[6]))
        else:
            QMessageBox.warning(self, "Hata", f"Ürün kodu {kod} bulunamadı!")
            self.form_temizle()

    def form_temizle(self):
        """Form alanlarını temizle"""
        for field in [
            self.urun_adi,
            self.birim_fiyat,
            self.stok_miktari,
            self.aciklama,
            self.marka,
            self.kategori,
        ]:
            field.clear()

    def kayit_sil(self):
        try:
            kod = int(self.kod_input.text())
        except:
            QMessageBox.warning(self, "Hata", "Geçerli bir ürün kodu giriniz!")
            return

        cevap = QMessageBox.question(
            self,
            "Emin misiniz?",
            f"Ürün kodu {kod} olan ürünü silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if cevap == QMessageBox.Yes:
            islem.execute("DELETE FROM urun WHERE urunKodu = ?", (kod,))
            baglanti.commit()
            QMessageBox.information(self, "Başarılı", "Ürün silindi!")
            self.tum_urunleri_listele()
            self.form_temizle()
            self.kod_input.clear()

    def kayit_guncelle(self):
        try:
            kod = int(self.kod_input.text())
            fiyat = int(self.birim_fiyat.text())
            stok = int(self.stok_miktari.text())
        except:
            QMessageBox.warning(self, "Hata", "Geçerli değerler giriniz!")
            return

        try:
            islem.execute(
                """
                UPDATE urun SET 
                    urunAdi = ?, 
                    birimFiyat = ?, 
                    stokMiktari = ?, 
                    urunAciklamasi = ?, 
                    marka = ?, 
                    kategori = ? 
                WHERE urunKodu = ?
            """,
                (
                    self.urun_adi.text(),
                    fiyat,
                    stok,
                    self.aciklama.text(),
                    self.marka.text(),
                    self.kategori.text(),
                    kod,
                ),
            )
            baglanti.commit()
            QMessageBox.information(self, "Başarılı", "Ürün bilgileri güncellendi!")
            self.tum_urunleri_listele()
        except Exception as e:
            QMessageBox.warning(self, "Hata", str(e))

if __name__ == "__main__":
    uygulama = QApplication(sys.argv)
    giris = GirisPenceresi()
    giris.show()
    sys.exit(uygulama.exec_())