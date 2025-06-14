# 🛍️ Zara Stock Checker Bot for Girlies (Telegram Mesajı + Bildirim Sesi)

Bu Python kodu ürünlerin stoklarını kontrol edip istediğiniz beden stoğa gelince size telegram mesajı ve bildirim sesi yollar.

---

## Özellikler

- Headless Selenium Chrome scraping
- Telegram alerting (optional)
- Sound notifications using `pygame`
- Configurable URL list, sizes, and sleep delay
- Foolproof `.env` handling

---

## Gereklilikler

- Python 3.8+
- Google Chrome

---

## Nasıl Kullanılır?

### 1. Repository'i klonlayın veya zip olarak indirin

### 2. Gerekli paketleri indirin
`pip install -r requirements.txt` terminale yazarak indirebilirsiniz

### 3. Config dosyasına istediğiniz linkleri kurun
 ```json
{
    "urls": [
        {
            "store": "zara",
            "url": "https://www.zara.com/tr/tr/godeli-halter-yaka-kisa-elbise-p02858777.html?v1=459502627&v2=2420896"
        },
        {
            "store": "zara",
            "url": "https://www.zara.com/tr/tr/godeli-halter-yaka-kisa-elbise-p02858777.html?v1=459502627&v2=2420896"
        }
    ],
    "sizes_to_check": [ "XS"],
    "sleep_min_seconds": 12,  
    "sleep_max_seconds": 22
}
```
url kısmına istediğiniz linki, sizes_to_check kısmına istediğiniz bedenleri yazabilirsiniz. İstediğiniz kadar store ve url ekleyebilirsiniz. 

## 4. Botu çalıştırın!
`python main.py` yazmanız yeterli

## 5. Opsiyonel: Telegram Mesaj Botu Kurulumu
+ Telegram'a girin -> BotFather'ı seçip /newbot komutunu kullanın.
+ Botunuza isim verin. İsim verdikten sonra HTTP API ve chat id'nizi size yollayacak.
+ .env isimli bir dosya kurun ve bu iki variable'ı şu formatta yazın:
```env
BOT_API=your_telegram_bot_api_key
CHAT_ID=your_chat_id
``` 

+ İşte bu kadar ^_^
