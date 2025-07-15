import requests
from bs4 import BeautifulSoup

def transfermarkt_verisi_getir(oyuncu_id):
    # İlgili oyuncunun Transfermarkt profil URL'si
    url = f"https://www.transfermarkt.com.tr/a/profil/spieler/{oyuncu_id}"
    
    # HTTP isteği için gerekli başlıklar
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    }

    # Sayfayı çek
    response = requests.get(url, headers=headers)

    # HTML içeriğini çözümle
    soup = BeautifulSoup(response.content, 'html.parser')

    # Oyuncunun adı ve forma numarasını çıkar
    def isim_ve_forma_noyu_al(soup):
        isim_etiketi = soup.select_one('.data-header__headline-wrapper')
        if not isim_etiketi:
            return None, None

        forma_no_etiketi = isim_etiketi.select_one('.data-header__shirt-number')
        forma_no = forma_no_etiketi.text.strip().lstrip('#') if forma_no_etiketi else None

        # Forma numarasını kaldır
        if forma_no_etiketi:
            forma_no_etiketi.decompose()

        # Kalan tüm metni birleştirerek ismi oluştur
        tam_ad = " ".join(parca.strip() for parca in isim_etiketi.stripped_strings)
        return tam_ad, forma_no
    
    tam_ad, forma_no = isim_ve_forma_noyu_al(soup)
    
    # Profil fotoğrafı URL'sini al
    def profil_fotografi_url(soup):
        img_tag = soup.select_one('.data-header__profile-container img')
        if not img_tag:
            return None
        
        return img_tag.get('src', '').strip()
    
    profil_foto_url = profil_fotografi_url(soup)

    # Mevcut kulüp bilgisi
    kulup_etiketi = soup.select_one('.data-header__club-info .data-header__club a')
    kulup_adi = kulup_etiketi.text.strip() if kulup_etiketi else None

    # Lig bilgisi
    lig_etiketi = soup.select_one('.data-header__league-link')
    lig_adi = lig_etiketi.text.strip() if lig_etiketi else None

    # Doğum tarihi ve yaş bilgisi
    dogum_bilgisi = soup.select_one('[itemprop="birthDate"]')
    dogum_tarihi = dogum_bilgisi.text.strip().split('(')[0].strip() if dogum_bilgisi else None
    yas = dogum_bilgisi.text.strip().split('(')[-1].replace(')', '').strip() if dogum_bilgisi else None

    # Doğum yeri
    dogum_yeri_etiketi = soup.select_one('[itemprop="birthPlace"]')
    dogum_yeri = dogum_yeri_etiketi.text.strip() if dogum_yeri_etiketi else None

    # Boy bilgisi
    boy_etiketi = soup.select_one('[itemprop="height"]')
    boy = boy_etiketi.text.strip() if boy_etiketi else None

    # Mevki bilgisi
    def mevkiyi_al(soup):
        for li in soup.select('ul.data-header__items li'):
            metin = li.get_text(strip=True)
            if metin.startswith("Mevki:"):
                span = li.select_one('.data-header__content')
                if span:
                    return span.text.strip()
        return "Bilinmiyor"
    
    mevki = mevkiyi_al(soup)

    # Milli takım bilgisini al
    def milli_takim_bilgisi_al(soup):
        for li in soup.select('ul.data-header__items li'):
            metin = li.get_text(strip=True)
            if ("Eski Milli" in metin) or ("Güncel Milli" in metin):
                span = li.select_one('.data-header__content')
                if span:
                    return span.text.strip()

        return None
    
    milli_takim = milli_takim_bilgisi_al(soup)

    # Sözleşme başlangıç tarihi
    sozlesme_baslangic = soup.select_one('span:-soup-contains("Sözleşme tarihi:")')
    sozlesme_baslangic_tarihi = sozlesme_baslangic.find_next('span').text.strip() if sozlesme_baslangic else None

    # Sözleşme bitiş tarihi
    sozlesme_bitis = soup.select_one('span:-soup-contains("Sözleşme sonu")')
    sozlesme_bitis_tarihi = sozlesme_bitis.find_next('span').text.strip() if sozlesme_bitis else None

    # Piyasa değeri
    piyasa_degeri_etiketi = soup.select_one('.data-header__market-value-wrapper')
    piyasa_degeri = piyasa_degeri_etiketi.text.strip().split('Son güncelleme:')[0].strip() if piyasa_degeri_etiketi else None

    # Kulüp logosunun URL’sini çıkar
    def kulup_logosu_url_al(soup):
        img = soup.select_one('.data-header__box__club-link img')
        if not img:
            return None

        srcset = img.get("srcset", "")
        parcalar = [p.strip() for p in srcset.split(",")]
        for parca in parcalar:
            if "1x" in parca:
                url = parca.split(" ")[0]
                if 'wappen/normquad/' in url:
                    url = url.replace('wappen/normquad/', 'wappen/big/')
                return url
        return None

    kulup_logo_url = kulup_logosu_url_al(soup)

    # Milli takım logosunun URL’sini çıkar
    def milli_takim_logo_url_al(soup):
        li = soup.select_one('li:-soup-contains("Güncel Milli oyuncu:")')
        if not li:
            return None

        img = li.select_one('img')
        if not img:
            return None

        src = img.get('src', '').strip()
        if 'flagge/tiny/' in src:
            src = src.replace('flagge/tiny/', 'flagge/head/')
        return src

    milli_takim_logo_url = milli_takim_logo_url_al(soup)

    # Çoklu uyruk ve bayrakları liste olarak al
    def uyruklar_ve_bayraklar(soup):
        etiket = soup.find('span', string=lambda x: x and "Uyruk:" in x)
        if not etiket:
            return []

        icerik_span = etiket.find_next_sibling()
        if not icerik_span:
            return []

        uyruklar = []
        girdiler = icerik_span.decode_contents().split("<br/>")

        for girdi in girdiler:
            girdi_soup = BeautifulSoup(girdi, 'html.parser')
            img = girdi_soup.find('img')
            ulke_adi = girdi_soup.get_text(strip=True)

            if img and ulke_adi:
                bayrak_url = img.get('src')
                if 'flagge/tiny/' in bayrak_url:
                    bayrak_url = bayrak_url.replace('flagge/tiny/', 'flagge/head/')
                uyruklar.append({
                    'country': ulke_adi,
                    'flag_url': bayrak_url
                })

        return uyruklar

    uyruk_listesi = uyruklar_ve_bayraklar(soup)

    # Tüm verileri sözlük olarak döndür
    return {
        "ad_soyad": tam_ad,
        "forma_numarasi": forma_no,
        "profil_foto_url": profil_foto_url,
        "kulup": kulup_adi,
        "lig": lig_adi,
        "dogum_tarihi": dogum_tarihi,
        "yas": yas,
        "dogum_yeri": dogum_yeri,
        "uyruklar": uyruk_listesi,
        "boy": boy,
        "mevki": mevki,
        "milli_takim": milli_takim,
        "sozlesme_baslangic": sozlesme_baslangic_tarihi,
        "sozlesme_bitis": sozlesme_bitis_tarihi,
        "piyasa_degeri": piyasa_degeri,
        "kulup_logosu": kulup_logo_url,
        "milli_takim_logosu": milli_takim_logo_url,
    }

# Örnek oyuncu ID'si (örneğin Lionel Messi'nin ID'si olabilir)
oyuncu_id = "28003"  # Transfermarkt'ta herhangi bir oyuncu profiline girildiğinde oyuncu ID, URL'de görülür

# Fonksiyonu çağır ve sonucu 'veri' isimli değişkende tut
veri = transfermarkt_verisi_getir(oyuncu_id)

print(veri)

# Sözlükten istenilen herhangi bir veriyi bir değişkende tut
oyuncu_ismi = veri['ad_soyad']

print(oyuncu_ismi)