
import os
import re
import json
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# ==========================================
# AYARLAR
# ==========================================

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

MIN_FIYAT = 3_000_000
MAX_FIYAT = 5_250_000

STATE_FILE = Path("seen.json")

SOURCES = {
    "Sahibinden": (
        "https://www.sahibinden.com/emlak-konut-satilik/"
        "mersin-mezitli"
    ),
    "Hepsiemlak": (
        "https://www.hepsiemlak.com/mezitli-satilik/daire"
    ),
    "Emlakjet": (
        "https://www.emlakjet.com/satilik-daire/mersin-mezitli"
    ),
}

ALLOWED_DOMAINS = {
    "sahibinden.com",
    "hepsiemlak.com",
    "emlakjet.com",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
}

session = requests.Session()
session.headers.update(HEADERS)


# ==========================================
# TELEGRAM
# ==========================================

def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    response = session.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": mesaj,
            "disable_web_page_preview": False,
        },
        timeout=20,
    )

    response.raise_for_status()
    result = response.json()

    if not result.get("ok"):
        raise RuntimeError(
            f"Telegram hatası: {result.get('description')}"
        )


# ==========================================
# DAHA ÖNCE GÖNDERİLEN İLANLAR
# ==========================================

def state_yukle():
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def state_kaydet(seen):
    STATE_FILE.write_text(
        json.dumps(sorted(seen), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ==========================================
# FİYAT VE ODA SAYISI
# ==========================================

def fiyat_bul(text):
    # 4.250.000 TL, 4.250.000 ₺ veya 4250000 TL
    matches = re.findall(
        r"(?<!\d)(\d{1,3}(?:\.\d{3})+|\d{7})\s*(?:TL|₺)",
        text,
        flags=re.IGNORECASE,
    )

    for value in matches:
        try:
            price = int(value.replace(".", ""))
            if MIN_FIYAT <= price <= MAX_FIYAT:
                return price
        except ValueError:
            continue

    return None


def oda_bul(text):
    # Başlıkta veya ilan kartında 2+1 ya da 3+1 aranır.
    matches = re.findall(
        r"(?<!\d)([23])\s*\+\s*1(?!\d)",
        text,
    )

    return sorted({f"{room}+1" for room in matches})


def alan_adina_izinli(url):
    host = (urlparse(url).hostname or "").lower()

    return any(
        host == domain or host.endswith("." + domain)
        for domain in ALLOWED_DOMAINS
    )


# ==========================================
# İLAN SAYFASINI TARA
# ==========================================

def ilanlari_bul(kaynak, search_url):
    print(f"\n[{kaynak}] Sayfa kontrol ediliyor: {search_url}")

    try:
        response = session.get(search_url, timeout=25)
        print(f"[{kaynak}] HTTP durum kodu: {response.status_code}")
        response.raise_for_status()

    except requests.RequestException as exc:
        print(f"[{kaynak}] Sayfaya erişilemedi: {exc}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    bulunan = {}

    for link_tag in soup.find_all("a", href=True):
        link = urljoin(search_url, link_tag["href"].strip())

        if not alan_adina_izinli(link):
            continue

        if link.rstrip("/") == search_url.rstrip("/"):
            continue

        # İlan bağlantısının metnini ve yakınındaki kartı incele.
        title = link_tag.get_text(" ", strip=True)
        card_text = ""

        parent = link_tag

        for _ in range(5):
            if parent.parent is None:
                break

            parent = parent.parent
            candidate = parent.get_text(" ", strip=True)

            if (
                len(candidate) >= 20
                and fiyat_bul(candidate)
                and oda_bul(candidate)
            ):
                card_text = candidate
                break

        combined = f"{title} {card_text}"

        if "mezitli" not in (
            combined + " " + urlparse(link).path
        ).lower():
            continue

        fiyat = fiyat_bul(combined)
        odalar = oda_bul(combined)

        if not fiyat or not odalar:
            continue

        if not title:
            title = combined[:180]

        if not title:
            continue

        # URL, aynı ilanın tekrarını önlemek için kullanılır.
        link = link.split("#")[0]

        bulunan[link] = {
            "kaynak": kaynak,
            "baslik": title[:250],
            "fiyat": fiyat,
            "odalar": odalar,
            "link": link,
        }

    print(f"[{kaynak}] Filtreye uyan ilan sayısı: {len(bulunan)}")
    return list(bulunan.values())


# ==========================================
# ANA PROGRAM
# ==========================================

def main():
    print("Mezitli emlak takip botu başladı.")

    seen = set(state_yukle())
    yeni_ilanlar = []

    for kaynak, url in SOURCES.items():
        try:
            ilanlar = ilanlari_bul(kaynak, url)

            for ilan in ilanlar:
                if ilan["link"] in seen:
                    continue

                mesaj = (
                    f"🏠 YENİ İLAN\n\n"
                    f"📌 {ilan['baslik']}\n"
                    f"📍 Mersin / Mezitli\n"
                    f"🛏 Oda: {', '.join(ilan['odalar'])}\n"
                    f"💰 Fiyat: {ilan['fiyat']:,} TL\n"
                    f"🌐 Kaynak: {ilan['kaynak']}\n\n"
                    f"🔗 {ilan['link']}"
                )

                try:
                    telegram_gonder(mesaj)
                    seen.add(ilan["link"])
                    yeni_ilanlar.append(ilan["link"])

                    print(
                        f"[{kaynak}] Telegram'a gönderildi: "
                        f"{ilan['link']}"
                    )

                    time.sleep(1)

                except Exception as exc:
                    print(
                        f"[{kaynak}] Telegram gönderim hatası: {exc}"
                    )

        except Exception as exc:
            print(f"[{kaynak}] Tarama hatası: {exc}")

    state_kaydet(seen)

    print(f"\nYeni gönderilen ilan sayısı: {len(yeni_ilanlar)}")
    print("İşlem tamamlandı.")


if __name__ == "__main__":
    main()
