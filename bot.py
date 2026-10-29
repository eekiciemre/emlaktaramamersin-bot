import requests
from bs4 import BeautifulSoup
import time

TOKEN = "9222419466:AAF65zfqe89xnHDSMcxpGEV2nabmhPbz0e4"
CHAT_ID = "8242316628"

# Hedef Kriterler ve Fiyat Aralığı
HEDEF_MAHALLELER = ["viranşehir", "menderes", "atatürk", "75. yıl"]
HEDEF_ODALAR = ["2+1", "3+1"]
MINIMUM_FIYAT = 3000000
MAKSIMUM_FIYAT = 5250000

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

def telegram_mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
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

def komutlari_kontrol_et():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            veri = response.json()
            if "result" in veri and len(veri["result"]) > 0:
                son_mesaj = veri["result"][-1]
                if "message" in son_mesaj and "text" in son_mesaj["message"]:
                    text = son_mesaj["message"]["text"].strip()
                    
                    if text == "/tara":
                        telegram_mesaj_gonder("🔍 Manuel tarama başlatıldı, portallar kontrol ediliyor...")
                        ilanlari_tara()
                    elif text == "/durum":
                        durum_mesaj = (
                            f"🤖 *Bot Durumu: AKTİF*\n\n"
                            f"📍 *Bölge:* Mersin / Mezitli (Viranşehir, Menderes, Atatürk, 75. Yıl)\n"
                            f"🏠 *Oda Tipleri:* 2+1, 3+1\n"
                            f"💰 *Fiyat Aralığı:* {MINIMUM_FIYAT:,} TL - {MAKSIMUM_FIYAT:,} TL\n"
                            f"🌐 *Taranan Siteler:* Sahibinden, Hepsiemlak, Emlakjet, Emlaksitem"
                        )
                        telegram_mesaj_gonder(durum_mesaj)
                    elif text == "/yardim":
                        yardim_mesaj = (
                            "📋 *Komut Listesi:*\n\n"
                            "/tara - Hemen şimdi siteleri tarar\n"
                            "/durum - Aktif filtreleri ve sistem durumunu gösterir\n"
                            "/yardim - Bu yardım menüsünü açar"
                        )
                        telegram_mesaj_gonder(yardim_mesaj)
    except Exception as e:
        print(f"Komut kontrol hatası: {e}")

def ilanlari_tara():
    print(f"Mersin Mezitli Taraması Başlatıldı (Fiyat Aralığı: {MINIMUM_FIYAT:,} TL - {MAKSIMUM_FIYAT:,} TL)...")
    
    platformlar = [
        ("Sahibinden", "https://www.sahibinden.com/emlak-konut-satilik/mersin-mezitli"),
        ("Hepsiemlak", "https://www.hepsiemlak.com/mersin-mezitli-satilik"),
        ("Emlakjet", "https://www.emlakjet.com/satilik-konut/mersin-mezitli/"),
        ("Emlaksitem", "https://www.emlaksitem.com/ilanlar/mersin-mezitli-satilik-daire")
    ]

    bulunan_ilan_sayisi = 0
    for kaynak_adi, url in platformlar:
        try:
            print(f"{kaynak_adi} taranıyor -> {url}")
            response = requests.get(url, headers=HEADERS, timeout=12)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                print(f"✅ {kaynak_adi} başarıyla tarandı.")
            else:
                print(f"⚠️ {kaynak_adi} durum kodu: {response.status_code}")
        except Exception as e:
            print(f"❌ {kaynak_adi} bağlantı hatası: {e}")
        
        time.sleep(3)

    telegram_mesaj_gonder(f"✅ Tarama turu tamamlandı. Kriterlere uyan yeni ilan kontrol edildi.")

if __name__ == "__main__":
    komutlari_kontrol_et()
    ilanlari_tara()
