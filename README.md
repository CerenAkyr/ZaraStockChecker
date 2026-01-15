# 🛍️ Zara Stock Checker Bot for Girlies (Telegram + E-posta + Bildirim Sesi)

Bu Python kodu ürünlerin stoklarını kontrol edip istediğiniz beden stoğa gelince size **Telegram mesajı**, **E-posta bildirimi** ve **sesli uyarı** yollar.

## Özellikler

* **Headless Selenium Chrome scraping:** Arka planda sessizce çalışır.
* **Telegram alerting (optional):** Anlık mesaj bildirimi.
* **E-posta Bildirimleri (Yeni!):** Gmail üzerinden stok güncellemelerini mail olarak alın.
* **VDS/VPS Uyumluluğu:** `pygame` artık opsiyoneldir. Sunucu ortamlarında (ses kartı olmayan yerlerde) bot hata vermeden çalışmaya devam eder ve sesi atlar.
* **Sound notifications:** Bilgisayar başında olduğunuzda `pygame` ile sesli uyarı.
* **Configurable URL list:** İstediğiniz kadar ürün ve beden ekleme seçeneği.
* **Foolproof .env handling:** Hassas verileriniz (API key, mail şifresi) güvende kalır.

## Gereklilikler

* Python 3.8+
* Google Chrome

### 1. Repository'i klonlayın veya zip olarak indirin

### 2. Gerekli paketleri indirin
`pip install -r requirements.txt` terminale yazarak indirebilirsiniz

### 3. VDS / Linux Kullanıcıları İçin Google Chrome Kurulumu

Eğer botu bir Linux VDS üzerinde çalıştıracaksanız, Google Chrome'un kurulu olması gerekir. Aşağıdaki komutları sırasıyla terminale yapıştırarak kurulumu yapabilirsiniz:

```bash
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt update
sudo apt install -y google-chrome-stable

```


### 4. Config dosyasına istediğiniz linkleri kurun
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

## 5. Botu çalıştırın!
`python main.py` yazmanız yeterli

## 6. Opsiyonel: Bildirim Ayarları (.env Kurulumu)

Bildirimleri alabilmek için proje klasöründe `.env` isimli bir dosya oluşturun ve ihtiyacınıza göre aşağıdaki bilgileri ekleyin:

### Telegram Kurulumu

* Telegram'da **BotFather** aracılığıyla bir bot oluşturun.
* `BOT_API` ve `CHAT_ID` bilgilerinizi alın.

### E-posta Kurulumu

* Gmail hesabınızdan bir **"Uygulama Şifresi" (App Password)** oluşturun.
* Gönderici ve alıcı mail adreslerini ekleyin.

**Örnek `.env` içeriği:**

```env
# Telegram Ayarları
BOT_API=your_telegram_bot_api_key
CHAT_ID=your_chat_id

# E-posta Ayarları
SENDER_EMAIL=gonderici_mail@gmail.com
RECEIVER_EMAIL=alici_mail@gmail.com
GMAIL_APP_PASSWORD=olusturdugunuz_16_haneli_sifre

```

## VDS / VPS Kullanıcıları İçin Not

Eğer bu botu bir sunucuda (VDS) çalıştırıyorsanız, ses çıkışı olmadığı için bot otomatik olarak ses çalma adımını atlayacaktır. `pygame` kütüphanesinin yüklü olmasına gerek yoktur; bot sadece Telegram ve E-posta bildirimlerini göndermeye devam edecektir.

## Disclaimer!

Bu repository sadece eğitim ve eğlence amaçlı yapılmıştır. Asla ama asla herhangi bir kar amacı gütme amacı yoktur!

+ İşte bu kadar ^_^
---
