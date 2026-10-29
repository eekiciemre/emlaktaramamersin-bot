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
        f"🚨 **YENİ İLAN YAKALANDI ({kaynak})!** 🚨\n\n"
        f"📌 **Başlık:** {baslik}\n"
        f"💰 **Fiyat:** {fiyat:,} TL\n"
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
    print("Mezitli ilanları taranıyor...")
    
    url = "https://www.sahibinden.com/emlak-konut-satilik/mersin-mezitli"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        print(f"Bağlantı Durum Kodu: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Sahibinden arama sonuçlarındaki ilan satırları
            ilan_satirlari = soup.find_all('tr', {'class': 'searchResultsItem'})
            print(f"Sayfada tespit edilen ilan satırı: {len(ilan_satirlari)}")
            
            for ilan in ilan_satirlari:
                try:
                    baslik_tag = ilan.find('a', {'class': 'classifiedTitle'})
                    fiyat_tag = ilan.find('td', {'class': 'searchResultsPriceValue'})
                    
                    if baslik_tag and fiyat_tag:
                        baslik = baslik_tag.text.strip()
                        link = "https://www.sahibinden.com" + baslik_tag['href']
                        
                        # Fiyatı sayıya çevirme
                        fiyat_metin = fiyat_tag.text.strip().replace(" TL", "").replace(".", "").replace(",", "")
                        fiyat = int(fiyat_metin)
                        
                        # Bütçe aralığı kontrolü (3M - 5.25M) ve 2+1 / 3+1 kontrolü
                        if MIN_FIYAT <= fiyat <= MAX_FIYAT:
                            if "2+1" in baslik or "3+1" in baslik:
                                print(f"Eşleşen ilan bulundu: {baslik} - {fiyat} TL")
                                telegram_mesaj_gonder(baslik, fiyat, "Sahibinden", link)
                except Exception as ex:
                    print(f"İlan çözümlenirken hata: {ex}")
        else:
            print("Siteye erişimde bot korumasına takıldı.")
            
    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    ilanlari_tara()
