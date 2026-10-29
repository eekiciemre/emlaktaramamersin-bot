
import os
import re
import imaplib
import email
import html
import requests

from email.header import decode_header
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# ==================================================
# AYARLAR: GitHub Secrets üzerinden alınır
# ==================================================

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

IMAP_HOST = os.environ.get("IMAP_HOST", "imap.gmail.com")
IMAP_USER = os.environ["IMAP_USER"]
IMAP_PASSWORD = os.environ["IMAP_PASSWORD"]
IMAP_FOLDER = os.environ.get("IMAP_FOLDER", "INBOX")

MIN_FIYAT = 3_000_000
MAX_FIYAT = 5_250_000

# Yalnızca bu ilan platformlarının bağlantıları kabul edilir.
ALLOWED_DOMAINS = (
    "sahibinden.com",
    "hepsiemlak.com",
    "emlakjet.com",
)

# ==================================================
# E-POSTA OKUMA
# ==================================================

def decode_text(value):
    if not value:
        return ""

    result = []

    for part, encoding in decode_header(value):
        if isinstance(part, bytes):
            result.append(
                part.decode(encoding or "utf-8", errors="replace")
            )
        else:
            result.append(part)

    return "".join(result)


def get_email_content(message):
    plain_parts = []
    html_parts = []

    parts = message.walk() if message.is_multipart() else [message]

    for part in parts:
        if part.get_content_disposition() == "attachment":
            continue

        content_type = part.get_content_type()

        if content_type not in ("text/plain", "text/html"):
            continue

        payload = part.get_payload(decode=True)
        if not payload:
            continue

        charset = part.get_content_charset() or "utf-8"
        content = payload.decode(charset, errors="replace")

        if content_type == "text/plain":
            plain_parts.append(content)
        else:
            html_parts.append(content)

    if plain_parts:
        return "\n".join(plain_parts)

    if html_parts:
        soup = BeautifulSoup("\n".join(html_parts), "html.parser")

        for tag in soup(["script", "style"]):
            tag.decompose()

        return str(soup)

    return ""


# ==================================================
# İLAN BİLGİLERİNİ AYIKLAMA
# ==================================================

def get_platform(url):
    host = (urlparse(url).hostname or "").lower()
    host = host.removeprefix("www.")

    for domain in ALLOWED_DOMAINS:
        if host == domain or host.endswith("." + domain):
            return domain

    return None


def extract_listing(content, subject):
    soup = BeautifulSoup(content, "html.parser")

    # E-posta HTML ise gerçek bağlantıları bul.
    links = []

    for tag in soup.find_all("a", href=True):
        url = html.unescape(tag["href"]).strip()
        platform = get_platform(url)

        if not platform:
            continue

        title = tag.get_text(" ", strip=True)

        # İzleme ve yönlendirme URL'lerini otomatik çözmeye çalışmıyoruz.
        # Doğrudan platform bağlantısı olmalı.
        if platform not in urlparse(url).hostname.lower():
            continue

        if title and url not in [item[1] for item in links]:
            links.append((title, url, platform))

    # Düz metin e-postalarda da platform bağlantılarını bul.
    if not links:
        for url in re.findall(r'https?://[^\s<>"\']+', content):
            url = html.unescape(url).rstrip(".,);]")
            platform = get_platform(url)

            if platform and platform in urlparse(url).hostname.lower():
                links.append(("", url, platform))

    if not links:
        return []

    text = soup.get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)

    if not text:
        text = re.sub(r"<[^>]+>", " ", content)
        text = re.sub(r"\s+", " ", text)

    combined = f"{subject} {text}"

    # Fiyat: ör. 4.250.000 TL veya 4.250.000 ₺
    price_matches = re.findall(
        r'(\d[\d.]*(?:,\d{1,2})?)\s*(?:TL|₺)',
        combined,
        flags=re.IGNORECASE
    )

    fiyat = None

    for value in price_matches:
        normalized = value.replace(".", "").replace(",", ".")
        try:
            number = int(float(normalized))
            if MIN_FIYAT <= number <= MAX_FIYAT:
                fiyat = number
                break
        except ValueError:
            continue

    # Oda sayısı başlıkta veya e-posta metninde bulunmalı.
    room_matches = re.findall(
        r'(?<!\d)([23])\s*\+\s*1(?!\d)',
        combined
    )

    if not fiyat or not room_matches:
        return []

    rooms = sorted(set(room_matches))

    # E-posta başlığı veya bağlantı metninden ilan başlığını al.
    results = []

    for link_title, url, platform in links:
        baslik = link_title or subject.strip()

        # Konum bilgisi e-postada geçmiyorsa Mezitli olduğunu varsayma.
        if "mezitli" not in combined.lower():
            continue

        results.append({
            "title": baslik[:250],
            "url": url,
            "platform": platform,
            "price": fiyat,
            "rooms": rooms,
        })

    return results


# ==================================================
# TELEGRAM
# ==================================================

def send_telegram(listing):
    room_text = " / ".join(f"{room}+1" for room in listing["rooms"])

    message = (
        f"🏠 YENİ İLAN BİLDİRİMİ\n\n"
        f"📌 {listing['title']}\n"
        f"📍 Mersin / Mezitli\n"
        f"🛏 Oda: {room_text}\n"
        f"💰 Fiyat: {listing['price']:,} TL\n"
        f"🌐 Kaynak: {listing['platform']}\n\n"
        f"🔗 {listing['url']}"
    )

    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "disable_web_page_preview": False,
        },
        timeout=20,
    )

    response.raise_for_status()

    result = response.json()

    if not result.get("ok"):
        raise RuntimeError(result.get("description", "Telegram gönderim hatası"))


# ==================================================
# E-POSTALARI TARA
# ==================================================

def main():
    print("Mezitli ilan bildirimi kontrolü başladı.")

    mailbox = imaplib.IMAP4_SSL(IMAP_HOST)

    try:
        mailbox.login(IMAP_USER, IMAP_PASSWORD)

        status, _ = mailbox.select(IMAP_FOLDER)

        if status != "OK":
            raise RuntimeError("E-posta klasörü açılamadı.")

        status, data = mailbox.search(None, "UNSEEN")

        if status != "OK":
            raise RuntimeError("Okunmamış e-postalar alınamadı.")

        message_ids = data[0].split()
        print(f"Okunmamış e-posta sayısı: {len(message_ids)}")

        for message_id in message_ids:
            status, fetched = mailbox.fetch(
                message_id,
                "(BODY.PEEK[])"
            )

            if status != "OK":
                print("E-posta okunamadı:", message_id)
                continue

            raw_email = next(
                (item[1] for item in fetched if isinstance(item, tuple)),
                None
            )

            if not raw_email:
                continue

            message = email.message_from_bytes(raw_email)
            subject = decode_text(message.get("Subject", ""))
            content = get_email_content(message)

            print("İşleniyor:", subject[:120])

            try:
                listings = extract_listing(content, subject)

                if not listings:
                    print(
                        "Eşleşme bulunamadı. "
                        "E-posta okunmamış olarak bırakıldı."
                    )
                    continue

                for listing in listings:
                    send_telegram(listing)
                    print("Telegram'a gönderildi:", listing["url"])

                # Yalnızca başarılı gönderimden sonra okundu işaretle.
                mailbox.store(message_id, "+FLAGS", "\\Seen")

            except Exception as error:
                print("E-posta işleme hatası:", error)

    finally:
        try:
            mailbox.logout()
        except Exception:
            pass

    print("Kontrol tamamlandı.")


if __name__ == "__main__":
    main()
