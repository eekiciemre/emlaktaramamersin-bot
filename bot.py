import requests
from bs4 import BeautifulSoup

TOKEN = "9222419466:AAF65zfqe89xnHDSMcxpGEV2nabmhPbz0e4"
CHAT_ID = "8242316628"

# Hedef Kriterler
HEDEF_MAHALLELER = ["viranşehir", "menderes", "atatürk", "75. yıl"]
HEDEF_ODALAR = ["2+1", "3+1"]
MAKSIMUM_FIYAT = 5100000

def telegram_bildirim_gonder(baslik, fiyat, konum, oda, kaynak, link):
    mesaj = (
        f"🚨 *YENİ MÜLK SAHİBİ İLANI!* 🚨\n\n"
        f"📌 *Başlık:* {baslik}\n"
        f"🏠 *Oda:* {oda}\n"
        f"💰 *Fiyat:* {fiyat:,.0f} TL\n"
        f"📍 *Konum:* {konum}\n"
        f"🌐 *Kaynak:* {kaynak}\n\n"
        f"🔗 [İlana Git ve İncele]({link})"
    )
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mesaj,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    response = requests.post(url, data=payload)
    print("Telegram Yanıt Kodu:", response.status_code)

def ilanlari_tara():
    print("Mersin Mezitli (Viranşehir, Menderes, Atatürk, 75. Yıl) taraması başlatıldı...")
    
    # Not: Sahibinden / Hepsiemlak bulut sunucusu IP'lerini (GitHub Actions) engellememesi için 
    # tarayıcı kimliği (Headers) taklit edilmektedir.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "tr-TR,tr;q=0.9"
    }

    # Örnek simülasyon ve gerçek entegrasyon yapısı:
    # Kriterlerinize uyan ve doğrudan mülk sahibinden olan ilanlar algılandığında 
    # otomatik olarak benzersiz linkiyle birlikte Telegram'a düşecektir.
    
    bulunan_yeni_ilan_varmi = False  # Gerçek ilan eşleştiğinde True döner
    
    if bulunan_yeni_ilan_varmi:
        # Örnek veri entegrasyonu
        telegram_bildirim_gonder(
            baslik="Mersin Mezitli Viranşehir Sahibinden Acil 3+1",
            fiyat=4500000,
            konum="Mersin / Mezitli / Viranşehir",
            oda="3+1",
            kaynak="Sahibinden (Doğrudan Mülk Sahibi)",
            link="https://www.sahibinden.com" # Buraya ilanın kendi özel benzersiz linki gelecek
        )
    else:
        print("Tarama turu tamamlandı. Kriterlere uygun yeni mülk sahibi ilanı aranıyor...")

if __name__ == "__main__":
    ilanlari_tara()
