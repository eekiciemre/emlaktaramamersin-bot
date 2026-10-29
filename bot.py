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
    print("Mersin Mezitli taraması başlatıldı...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "tr-TR,tr;q=0.9"
    }

    # Test amaçlı tıklanabilir örnek ilan (Linke bastığınızda doğrudan test sayfasına gidecek)
    bulunan_yeni_ilan_varmi = True  # Şimdilik test için True yaptık
    
    if bulunan_yeni_ilan_varmi:
        telegram_bildirim_gonder(
            baslik="Mezitli Viranşehir Sahibinden Temiz 3+1 (TEST İLANI)",
            fiyat=4250000,
            konum="Mersin / Mezitli / Viranşehir",
            oda="3+1",
            kaynak="Sahibinden (Doğrudan Mülk Sahibi)",
            link="https://www.sahibinden.com" # Buraya tıklayınca site açılacak
        )
    else:
        print("Kriterlere uygun yeni ilan aranıyor...")

if __name__ == "__main__":
    ilanlari_tara()
