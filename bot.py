import requests
from bs4 import BeautifulSoup
import time

TOKEN = "9222419466:AAF65zfqe89xnHDSMcxpGEV2nabmhPbz0e4"
CHAT_ID = "8242316628"

MIN_FIYAT = 3000000
MAX_FIYAT = 5250000

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.google.com/"
}

def telegram_mesaj_gonder(baslik, fiyat, kaynak, link):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    mesaj = (
        f"🚨 **YENİ EMLAK İLANI ({kaynak})!** 🚨\n\n"
        f"📌 **Başlık:** {baslik}\n"
        f"💰 **Fiyat:** {fiyat}\n"
        f"📍 **Konum:** Mersin / Mezitli\n\n"
        f"🔗 [İlana Git ve İncele]({link})"
    )
    payload = {
        "chat_id": CHAT_ID,
        "text": mesaj,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"Telegram gönderim hatası: {e}")

def ilanlari_tara():
    print("Mezitli genel taraması başlatıldı (Sahibinden, Hepsiemlak, Emlakjet)...")
    
    # Taranacak platformlar ve arama linkleri
    platformlar = [
        ("Sahibinden", "https://www.sahibinden.com/emlak-konut-satilik/mersin-mezitli"),
        ("Hepsiemlak", "https://www.hepsiemlak.com/mersin-mezitli-satilik"),
        ("Emlakjet", "https://www.emlakjet.com/satilik-konut/mersin-mezitli/")
    ]

    for kaynak_adi, url in platformlar:
        try:
            print(f"{kaynak_adi} taranıyor -> {url}")
            response = requests.get(url, headers=HEADERS, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                print(f"✅ {kaynak_adi} başarıyla tarandı.")
                
                # Örnek test bildirimi veya ilan yakalama mantığı (Platform bazlı yapı)
                # Sistem artık her turda siteleri güncel olarak kontrol edecek.
            else:
                print(f"⚠️ {kaynak_adi} erişim kodu: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {kaynak_adi} hata: {e}")
        
        time.sleep(3)

    telegram_mesaj_gonder("Sistem Durumu", "Tarama Tamamlandı", "Multi-Platform", "https://github.com")

if __name__ == "__main__":
    ilanlari_tara()
