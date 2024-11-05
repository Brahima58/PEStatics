import requests
from bs4 import BeautifulSoup
import pyodbc
import time


conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'SERVER=server_adi;'  
                      'DATABASE=db_adi;'  
                      'Trusted_Connection=yes;') #Database bilgilerini giriniz
cursor = conn.cursor()



headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0" #kendi user agentinizi girin, bunu tarayıcınza yazarak öğrenebilirsiniz
}
url = f"https://pesdb.net/efootball/?mode=max_level&all=1&featured=1046" #oyuna sürekli farklı oyuncular eklendiği için diğer sayfadaki tüm oyuncuları çektikten sonra münferit bir sayfadaki oyuncuları çekmek için el ile url kısmını değişilmesi gerekir. (sitede yeni oyuncular sekmesi olmadığı için url'yi kendiniz girmelisiniz.)
sayfa = requests.get(url, headers=headers)
icerik = BeautifulSoup(sayfa.content, 'html.parser')
table = icerik.find('table', class_='players')
oyuncu_urls = []
if table:
    rows = table.find_all('tr')
    for row in rows:
        satir = row.find_all('td')
        if len(satir) > 1:
            link = satir[1].find('a')
            if link:
                oyuncu_url = "https://pesdb.net/efootball/" + link['href']
                oyuncu_urls.append(oyuncu_url)
    for oyuncu_url in oyuncu_urls: #url içindeki tüm verileri al ve SQL tablosuna doldur
        oyuncu_sayfasi = requests.get(oyuncu_url, headers=headers)
        oyuncu_icerik = BeautifulSoup(oyuncu_sayfasi.content, 'html.parser')
        oyuncuAdi_row = oyuncu_icerik.find('th', string='Player Name:')
        oyuncuAdi_deger = oyuncuAdi_row.find_next_sibling('td').find('span').text
        genelDerece = int(oyuncu_icerik.find(id='a0').text)
        ofns = int(oyuncu_icerik.find(id='a1').text)
        tpkn = int(oyuncu_icerik.find(id='a2').text)
        tpsr = int(oyuncu_icerik.find(id='a3').text)
        sktp = int(oyuncu_icerik.find(id='a4').text)
        alck = int(oyuncu_icerik.find(id='a5').text)
        yksk = int(oyuncu_icerik.find(id='a6').text)
        btrc = int(oyuncu_icerik.find(id='a7').text)
        kafa = int(oyuncu_icerik.find(id='a8').text)
        drnt = int(oyuncu_icerik.find(id='a9').text)
        flso = int(oyuncu_icerik.find(id='a10').text)
        df_fr = int(oyuncu_icerik.find(id='a11').text)
        tckl = int(oyuncu_icerik.find(id='a12').text)
        agr = int(oyuncu_icerik.find(id='a13').text)
        df_kt = int(oyuncu_icerik.find(id='a14').text)
        kl_fr = int(oyuncu_icerik.find(id='a15').text)
        kl_yk = int(oyuncu_icerik.find(id='a16').text)
        kl_sv = int(oyuncu_icerik.find(id='a17').text)
        kl_rf = int(oyuncu_icerik.find(id='a18').text)
        kl_uz = int(oyuncu_icerik.find(id='a19').text)
        hiz = int(oyuncu_icerik.find(id='a20').text)
        hzln = int(oyuncu_icerik.find(id='a21').text)
        stgc = int(oyuncu_icerik.find(id='a22').text)
        zplm = int(oyuncu_icerik.find(id='a23').text)
        fzk = int(oyuncu_icerik.find(id='a24').text)
        dng = int(oyuncu_icerik.find(id='a25').text)
        dynk = int(oyuncu_icerik.find(id='a26').text)
        zayif_ayak_kullanimi = oyuncu_icerik.find('th', string='Weak Foot Usage:').find_next('td').get_text()
        zayif_ayak_isabeti = oyuncu_icerik.find('th', string='Weak Foot Accuracy:').find_next('td').get_text()
        boy = int(oyuncu_icerik.find('th', string='Height:').find_next_sibling('td').find('span').text)
        yas = int(oyuncu_icerik.find('th', string='Age:').find_next_sibling('td').find('span').text)
        oyuncuAyak_deger = oyuncu_icerik.find('th', string='Foot:').find_next_sibling('td').find('span').text
        oyuncuPozisyon_deger = oyuncu_icerik.find('th', string='Position:').find_next_sibling('td').find('span').text
        oyuncuPozisyonlar = oyuncu_icerik.find('div', class_='pitch')
        diger_pozisyonlar = [pozisyon.get('title', 'No title') for pozisyon in oyuncuPozisyonlar.find_all('div')]
        oyuncuSkill = oyuncu_icerik.find('table', class_='playing_styles')
        skiller = oyuncuSkill.find('th', string='Player Skills')
        oyuncuS = []
        skill = skiller.find_next('td')
        while skill and skill.find_previous('th').get_text() != 'AI Playing Styles':
            oyuncuS.append(skill.get_text())
            skill = skill.find_next('td')
        oyunTarzlari = oyuncu_icerik.find('table', {'class': 'playing_styles'})
        row1 = oyunTarzlari.find('td')
        oyuntarz = row1.text.strip() if row1 else ''
        oyuncuTur_div = oyuncu_icerik.find('div', attrs={'style': 'text-align: center; margin-top: 4px;'})
        oyuncuTur = oyuncuTur_div.text.strip() if oyuncuTur_div and oyuncuTur_div.text else "Default"
        cursor.execute("""
            INSERT INTO Players (PlayerName, OverallRating, OffensiveAwareness, BallControl, Dribbling, TightPossession, 
                                 LowPass, LoftedPass, Finishing, Header, SetPieceTaking, Curve, DefensiveAwareness, Tackling, 
                                 Aggression, DefensiveEngagement, GKAwareness, GKCatch, GKClearance, GKReflexes, GKReach, 
                                 Speed, Acceleration, KickingPower, Jumping, PhysicalContact, Balance, Stamina, 
                                 WeakFootUsage, WeakFootAccuracy, Height, Age, Foot, Position, PlayerSkills, PlayingStyle, 
                                 Package, OtherPositions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)""",
                       oyuncuAdi_deger, genelDerece, ofns, tpkn, tpsr, sktp, alck, yksk, btrc, kafa, drnt, flso,
                       df_fr, tckl, agr, df_kt,
                       kl_fr, kl_yk, kl_sv, kl_rf, kl_uz, hiz, hzln, stgc, zplm, fzk, dng, dynk,
                       zayif_ayak_kullanimi, zayif_ayak_isabeti,
                       boy, yas, oyuncuAyak_deger, oyuncuPozisyon_deger, ','.join(oyuncuS), oyuntarz, oyuncuTur,
                       ','.join(diger_pozisyonlar))
        conn.commit()
        print(f"Veritabanına kaydedildi: {oyuncuAdi_deger} - Genel Derece: {genelDerece}") #hangi oyuncuların eklendiğini takip etmek için
        time.sleep(3.8) #verileri scrap ederken sitenin bloklamaması için cooldown ekleyin, genelde 3.75 saniye üzerisi kabul edilir.
cursor.close()