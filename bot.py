import requests

TOKEN = "9222419466:AAF65zfqe89xnHDSMcxpGEV2nabmhPbz0e4"
CHAT_ID = "8242316628"

HEDEF_MAHALLELER = ["viranşehir", "menderes", "atatürk", "75.yıl", "75. yıl"]
HEDEF_ODALAR = ["2+1", "3+1"]
MAKSIMUM_FIYAT = 5100000

def telegram_bildirim_gonder(baslik, fiyat, konum, oda, link):
    mesaj = (
        f"🎯 **YENİ FIRSAT İLANI!**\n\n"
        f"📌 **Başlık:** {baslik}\n"
        f"🏠 **Oda:** {oda}\n"
        f"💰 **Fiyat:** {fiyat:,.0f} TL\n"
        f"📍 **Konum:** {konum}\n\n"
        f"🔗 **İlana Git:** {link}"
    )
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

print("Bot tarama turunu tamamladı.")
