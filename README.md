# 🛍️ Zara Stock Checker Bot for Girlies (Telegram Mesajı + Bildirim Sesi)

Bu Python kodu ürünlerin stoklarını kontrol edip istediğiniz beden stoğa gelince size telegram mesajı ve bildirim sesi yollar.

---

## Özellikler

- Headless Selenium Chrome scraping
- Telegram alerting (optional)
- Sound notifications using `pygame`
- Configurable per-item sizes and sleep delay
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
            "url": "https://www.zara.com/tr/tr/godeli-halter-yaka-kisa-elbise-p02858777.html?v1=459502627&v2=2420896",
            "sizes": ["XS"]
        },
        {
            "store": "bershka",
            "url": "https://www.bershka.com/tr/keten-halter-mini-elbise-c0p181385566.html?colorId=700",
            "sizes": ["36"]
        },
        {
            "store": "mango",
            "url": "https://shop.mango.com/tr/tr/p/kadin/aksesuarlar/canta/suni-deri-canta_17000000",
            "sizes": ["-"]
        }
    ],
    "sleep_min_seconds": 12,  
    "sleep_max_seconds": 22
}
```
Her ürün için `sizes` alanını ayrı ayrı yazın. Kıyafet için `"XS"`, ayakkabı için `"36"` gibi değerler kullanabilirsiniz. Bedensiz ürünlerde `"-"` kullanın. Eski `sizes_to_check` alanı hala fallback olarak desteklenir ama yeni formatta gerekli değildir.

## 4. Botu çalıştırın!
`python main.py` yazmanız yeterli

## GUI
Basit bir arayüz ile çalıştırmak için:
`python gui.py`

## Desktop App Build (macOS)
Masaüstü uygulaması oluşturmak için:
`./build_desktop.sh`

Build tamamlanınca uygulama burada oluşur:
`dist/ZaraStockChecker.app`

## 5. Opsiyonel: Telegram Mesaj Botu Kurulumu
+ Telegram'a girin -> BotFather'ı seçip /newbot komutunu kullanın.
+ Botunuza isim verin. İsim verdikten sonra HTTP API ve chat id'nizi size yollayacak.
+ .env isimli bir dosya kurun ve bu iki variable'ı şu formatta yazın:
```env
BOT_API=your_telegram_bot_api_key
CHAT_ID=your_chat_id
``` 

+ İşte bu kadar ^_^

## Disclaimer!
Bu repository sadece eğitim ve eğlence amaçlı yapılmıştır. Asla ama asla herhangi bir kar amacı gütme amacı yoktur!
