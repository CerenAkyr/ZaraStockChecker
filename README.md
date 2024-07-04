# Zara Stock Checker
Zara Stock Checker for Girlies 

## Gereksiminler

+ Python: Version 3.6 veya daha yüksek 
+ Google Chrome: Chrome Driver kullanıldığı için Chrome da lazım :)
+ ChromeDriver: Asıl olayımız bu olacak

### ChromeDriver Nasıl İndiririm?
[Buraya tıklayarak indirme sayfasına gidebilirsiniz](https://googlechromelabs.github.io/chrome-for-testing/)
![image](https://github.com/CerenAkyr/ZaraStockChecker/assets/77779913/bb4606b3-d7e6-4902-8acd-279f1eedea6d)
Örneğin ben bu üstteki linki tarayıcıya yapıştırarak indirdim. 
Sonrasında, indirdiğiniz zip dosyasını hatırlayacağınız ve kolay bir yere extract edin.
İşte bu kadar :)

## Kodu Çalıştırmak
Github repository klonladıktan sonra, gereken kütüphaneleri indirmek için terminale alttaki yazıyı kopyalayın:
```
pip install -r requirements.txt
```
Sonrasında, config dosyasına girin vee:
Buraya istediğiniz linkleri formatı bozmadan girin:
```
 "urls": [
        "https://www.zara.com/tr/tr/dugumlu-ajurlu-triko-elbise-p02756024.html?v1=367462396",
        "https://www.zara.com/tr/tr/parlak-tasli-kisa-elbise-p04764302.html?v1=363971227"
    ],
```
Buraya stoğunu istediğiniz bedenleri yazın:
```
"sizes_to_check": ["XS", "S"],
```
Kontroller arasında ne kadar süre beklemeli onu yazın (bende şu anda 10-12 dk arası)
Not: Saniye cinsinden yazmayı unutmayın!
```
"sleep_min_seconds": 600,  
"sleep_max_seconds": 720,
```
Son olarak, ChromeDriver indirdiğiniz yeri hatırlıyor musunuz? Onun konumunu buraya yazın (kodun olduğu lokasyona göreceli olarak):
```
"chrome_driver_path": "../../DesktopHolder/chromedriver-win64/chromedriver.exe"
```
Artık kodu çalıştırabilirsiniz.


İyi alışverişler!!





