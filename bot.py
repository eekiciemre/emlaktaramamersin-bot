import requests

TOKEN = "9222419466:AAF65zfqe89xnHDSMcxpGEV2nabmhPbz0e4"
CHAT_ID = "8242316628"

mesaj = "🚀 *GitHub Actions Botu Başarıyla Çalıştı!* \n\nSistem artık 10 dakikada bir otomatik çalışacak ve Telegram bağlantısı aktif."
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}

response = requests.post(url, data=payload)
print("Telegram Yanıt Kodu:", response.status_code)
