import pyodbc
import random
import math
from unidecode import unidecode
from flask import Flask, render_template, request

app = Flask(__name__)


#Global değişkenler
conn = None 
cursor = None

@app.before_request #Ön bağlantı kur
def before_request():
    global conn, cursor
    if conn is None:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=DESKTOP-9SRF0UM\\SQLEXPRESS;'
            'DATABASE=OyuncuDB;'
            'UID=Brahima58;'
            'PWD=jhvc/327u_S;'
        )
        cursor = conn.cursor()

@app.teardown_request #Optimize et
def teardown_request(exception):
    global conn, cursor
    if cursor:
        cursor.close()
    if conn:
        conn.close()
        conn = None  

@app.route('/') #Bilgi sayfası
def home():
    return render_template('index.html')

def position_calculate(player_data, player_position): #parametreleri döngü dışından al
    global cursor

    columns = ['OverallRating', 'OffensiveAwareness', 'BallControl', 'Dribbling', 
               'TightPossession', 'LowPass', 'LoftedPass', 'Finishing', 'Header', 
               'SetPieceTaking', 'Curve', 'DefensiveAwareness', 'Tackling', 
               'Aggression', 'DefensiveEngagement', 'GKAwareness', 'GKCatch', 
               'GKClearance', 'GKReflexes', 'GKReach', 'Speed', 'Acceleration', 
               'KickingPower', 'Jumping', 'PhysicalContact', 'Balance', 'Stamina','Height']
    player_data_dict = {column: getattr(player_data, column, None) for column in columns} #Her bir columndaki veriyi player_data sözlüğünde tut
    sonuclar = {} #dereceleri bu sözlükte tut

    for column in columns: #her bir sütundaki verilerin sapmasını al
        cursor.execute(f"""
            SELECT 
                AVG({column}) AS average,
                STDEV({column}) AS stdev,
                MIN({column}) AS min,
                MAX({column}) AS max
            FROM Players
            WHERE Position = ?;
        """, player_position)

        sonuc = cursor.fetchone() #her bir column için işlem yap
        average, stdev, min_val, max_val = sonuc #verileri bu isimlerde tut

        if None in (average, stdev, min_val, max_val) or stdev <= 0: #aykırı değerde ortalama döndür
            sonuclar[column] = 'ortalama'
            continue

     
        n = int((max_val - min_val) / stdev)  #dinamik sayıda dizi oluştur
        puanlar = {} #puanları sözlükte tut

        for i in range(n + 1):  
            yeni_deger = min_val + (i * stdev)

            if yeni_deger < average - 2 * stdev:
                puan = "cokkotu"
            elif yeni_deger < average - stdev:
                puan = "kotu"
            elif yeni_deger < average + stdev:
                puan = "ortalama"
            elif yeni_deger < average + 2 * stdev:
                puan = "iyi"
            elif yeni_deger < average + 3 * stdev:
                puan = "cokiyi"
            else:
                puan = "mukemmel"

            puanlar[yeni_deger] = puan #hesaplanan yeni değeri puanlar içine al
        mevcut_deger = player_data_dict[column] #her bir columnu mevcut_deger içine al
       
        mevcut_puan = None
        for key, value in puanlar.items(): #uygun puan bulana kadar kıyasla
            if mevcut_deger <= key:
                mevcut_puan = value
                break
        if mevcut_puan is None:  #aykırı değeri mükemmel ayarla
            mevcut_puan = "mukemmel"

        sonuclar[column] = mevcut_puan #her bir column için mevcut_degeri ata

    return player_data_dict, sonuclar #sonucu döndür


def accuracy_class(accuracy): #zayıf ayak için fonksiyon
    if accuracy == "Low":
        return "cokkotu" 
    elif accuracy == "Medium":
        return "ortalama" 
    elif accuracy == "High":
        return "iyi"  
    elif accuracy == "Very High":
        return "mukemmel"
    return ""

def cosinesim_class(player_data, player_position, cosine_value): #benzerlik skoruna göre renklendirmek için
    global cursor 
    
    column = 'CosineSimilarity'
    player_data_dict = {'CosineSimilarity': getattr(player_data, 'CosineSimilarity', None)} #sözlükte tut

    cursor.execute(f"""
        SELECT 
            MIN({column}) AS min,
            MAX({column}) AS max
        FROM Players
        WHERE Position = ?;
    """, (player_position,))
    
    sonuc = cursor.fetchone()
    min_val, max_val = sonuc

    percentage = ((cosine_value - min_val) / (max_val - min_val)) #yüzdelik dilim hesaplamak için formülize et

    if percentage <= 0.1:
        sonuc = "cokkotu"
    elif percentage <= 0.3:
        sonuc = "kotu"
    elif percentage <= 0.5:
        sonuc = "ortalama"
    elif percentage <= 0.7:
        sonuc = "iyi"
    elif percentage <= 0.8:
        sonuc = "cokiyi"
    else:
        sonuc = "mukemmel"

    return player_data_dict, sonuc

    
def combined_abilities(player_data):
    global cursor

    columns = ['Precision', 'LongRangeShooting', 'Diligence', 'DribbleSpeed', 
                'Agility', 'Vision','Obstinacy', 'GoalKeeping']
    player_data_dict = {column: getattr(player_data, column, None) for column in columns} #Her bir columndaki veriyi player_data sözlüğünde tut
    sonuclar1 = {} 

    player_position = player_data.Position
    for column in columns: #her bir sütundaki verilerin sapmasını al
        cursor.execute(f"""
            SELECT 
                AVG({column}) AS average,
                STDEV({column}) AS stdev,
                MIN({column}) AS min,
                MAX({column}) AS max
            FROM Players
            WHERE Position = ?;
        """, (player_position,))

        sonuc = cursor.fetchone() #her bir column için işlem yap
        average, stdev, min_val, max_val = sonuc #verileri bu isimlerde tut

        if None in (average, stdev, min_val, max_val) or stdev <= 0: #aykırı değerde ortalama döndür
            sonuclar1[column] = 'ortalama'
            continue

     
        n = int((max_val - min_val) / stdev)  #dinamik sayıda dizi oluştur
        puanlar = {} #puanları sözlükte tut

        for i in range(n + 1):  
            yeni_deger = min_val + (i * stdev)

            if yeni_deger < average - 2 * stdev:
                puan = "cokkotu"
            elif yeni_deger < average - stdev:
                puan = "kotu"
            elif yeni_deger < average + stdev:
                puan = "ortalama"
            elif yeni_deger < average + 2 * stdev:
                puan = "iyi"
            elif yeni_deger < average + 3 * stdev:
                puan = "cokiyi"
            else:
                puan = "mukemmel"

            puanlar[yeni_deger] = puan #hesaplanan yeni değeri puanlar içine al
        mevcut_deger = player_data_dict[column] #her bir columnu mevcut_deger içine al
       
        mevcut_puan = None
        for key, value in puanlar.items(): #uygun puan bulana kadar kıyasla
            if mevcut_deger <= key:
                mevcut_puan = value
                break
        if mevcut_puan is None:  #aykırı değeri mükemmel ayarla
            mevcut_puan = "mukemmel"

        sonuclar1[column] = mevcut_puan

    return player_data_dict,sonuclar1

@app.route('/player/package/<string:package>') #oyuncunun hangi pakette bulundğunu belirtmek için
def packages(package):
    global cursor

    cursor.execute("SELECT * FROM Players WHERE Package = ? ORDER BY PlayerName", package)  
    player_data = cursor.fetchall()  #tüm paketleri incele

    if not player_data:  
        return "Player Not Found", 404  

    return render_template('packages.html', players=player_data, package=package)

@app.route('/search', methods=['POST']) #oyuncu arama fonksiyonu
def search():
    global cursor
    oyuncu_adi = request.form.get('oyuncu_adi')

    if not oyuncu_adi:
        return "Oyuncu adı girmediniz, lütfen bir oyuncu adı girin.", 400


    cursor.execute("""
        SELECT PlayerID, PlayerName, OverallRating, Position, Package FROM Players 
        WHERE PlayerName COLLATE Latin1_General_CI_AI LIKE ?; 
    """, ['%' + oyuncu_adi + '%']) #Türkçe vb. karakterler için standartlaştır

    players = cursor.fetchall()
    
    return render_template('players.html', Players=players)

@app.route('/random_player')  #rastgele oyuncuya gitme fonksiyonu  
def random_player():
    global cursor
    cursor.execute("SELECT PlayerID FROM Players")  
    player_ids = cursor.fetchall()  

    if not player_ids:
        return "Oyuncu bulunamadı", 404 

    random_player_id = random.choice(player_ids)[0]  
    return players_detail(random_player_id)

@app.route('/player/<int:player_id>/similar') #benzer oyuncuları bulma fonksiyonu
def similar_players(player_id):
    global cursor

    cursor.execute("""
        SELECT Position, PlayingStyle, Height, CosineSimilarity
        FROM Players 
        WHERE PlayerID = ?;
    """, (player_id,))
    player_info = cursor.fetchone()
    
    if not player_info:
        return "Oyuncu bulunamadı", 404


    playing_style = player_info.PlayingStyle
    height = player_info.Height
    cosine_value = player_info.CosineSimilarity
    cursor.execute("""
        SELECT TOP 10 PlayerID, PlayerName,OverallRating, Package, CosineSimilarity, Height 
        FROM Players 
        WHERE PlayingStyle = ? 
          AND ABS(Height - ?) <= ? 
          AND ABS(CosineSimilarity - ?) <= ?
          AND PlayerID != ? 
        ORDER BY ABS(CosineSimilarity - ?), ABS(Height - ?)
    """, (playing_style, height, height * 0.015, cosine_value, 0.01, player_id, cosine_value, height * 0.015)) #Belirtilen özelliklere göre benzer profilleri bul, benzerlik daraltıtlıp genişletilebilir.
    
    benzer_oyuncular = cursor.fetchall()

    return benzer_oyuncular

@app.route('/player/<int:player_id>')  #oyuncu detay sayfası
def players_detail(player_id):
    global cursor

    benzer_oyuncular = similar_players(player_id)

    stat_groups = {
        "Offense": ["OffensiveAwareness", "Finishing", "Header", "KickingPower"],
        "Defense": ["DefensiveAwareness", "DefensiveEngagement", "Tackling", "Aggression"],
        "Dribbling": ["BallControl", "Dribbling", "TightPossession", "Balance"],
        "Passing": ["LowPass", "LoftedPass", "Curve", "SetPieceTaking"],
        "Physical": ["Height", "PhysicalContact", "Stamina", "Speed", "Acceleration", "Jumping"],
        "Goalkeeping": ["GKAwareness", "GKReflexes", "GKReach", "GKCatch", "GKClearance"],
    }

    cursor.execute("SELECT * FROM Players WHERE PlayerID = ?", player_id) #player_id içine ata
    player_data = cursor.fetchone()  #player_data içine sonuçları at

    if not player_data:
        return "Player Not Found", 404 

    cursor.execute("SELECT Package, Position, PlayingStyle, Age,Foot,WeakFootAccuracy,WeakFootUsage,PlayerSkills FROM Players WHERE PlayerID = ?", player_id)
    info_data = cursor.fetchone() #player_data sayısal değerler tuttuğundan info_data oluştur
    
    cursor.execute("SELECT Precision, LongRangeShooting, Diligence, DribbleSpeed,Agility, Vision,Obstinacy, GoalKeeping FROM Players WHERE PlayerID = ?", player_id)
    combine_data = cursor.fetchone()

    cursor.execute("SELECT CosineSimilarity FROM Players WHERE PlayerID = ?", player_id)
    cosine_data = cursor.fetchone()
    cosine_value = cosine_data[0]

    weak_foot_accuracy_class = accuracy_class(info_data.WeakFootAccuracy) #zayıf ayak bilgisini bu sınıfta tut



    player_position = player_data.Position  #pozisyonu al
    player_data_dict_position, sonuclar = position_calculate(player_data, player_position) #pozisyon için calculate fonksiyonu işlemini yap hem dict hem sonuclara aktar
    
    player_data_dict, a_cosinesim_class = cosinesim_class(player_data, player_position, cosine_value)


    player_data_dict_combine, sonuclar1 = combined_abilities(player_data)

    cosine_value = player_data.CosineSimilarity 

    player_data_dict = {**player_data_dict_position, **player_data_dict_combine}

    return render_template('players_detail.html', player_name=player_data.PlayerName, player_data=player_data_dict, stat_groups=stat_groups, 
                           sonuclar=sonuclar,info_data=info_data, weak_foot_accuracy_class=weak_foot_accuracy_class,
                           combine_data=combine_data,sonuclar1=sonuclar1,cosine_data=cosine_data,cosine_value=cosine_value,
                           a_cosinesim_class=a_cosinesim_class,benzer_oyuncular=benzer_oyuncular) #html'de görüntülenecek veriler

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

