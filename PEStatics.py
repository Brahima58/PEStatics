import random
import os
import psycopg2 
from psycopg2.extras import DictCursor
from unidecode import unidecode
from flask import Flask, redirect, render_template, request

app = Flask(__name__)


#Global değişkenler
conn = None 
cursor = None
DB_HOST = os.getenv("DB_HOST")  
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

@app.before_request #Ön bağlantı kur
def before_request():
    global conn, cursor
    if conn is None:
        conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
                sslmode="require"
    )
        cursor = conn.cursor(cursor_factory=DictCursor)


@app.route('/') #Bilgi sayfası
def home():
    return render_template('index.html')

def position_calculate(player_data, player_position): #parametreleri döngü dışından al
    global cursor
    columns = ['overallrating', 'offensiveawareness', 'ballcontrol', 'dribbling', 
               'tightpossession', 'lowpass', 'loftedpass', 'finishing', 'header', 
               'setpiecetaking', 'curve', 'defensiveawareness', 'tackling', 
               'aggression', 'defensiveengagement', 'gkawareness', 'gkcatch', 
               'gkclearance', 'gkreflexes', 'gkreach', 'speed', 'acceleration', 
               'kickingpower', 'jumping', 'physicalcontact', 'balance', 'stamina','height']
    print("Player Data:", player_data)
    player_data_dict = {column: player_data.get(column, None) for column in columns} #Her bir columndaki veriyi player_data sözlüğünde tut
    print("Player Data Dict:", player_data_dict)
    sonuclar = {} #dereceleri bu sözlükte tut

    for column in columns: #her bir sütundaki verilerin sapmasını al
        cursor.execute (f"""
            SELECT 
                AVG({column}) AS average,
                STDDEV({column}) AS stdev,
                MIN({column}) AS min,
                MAX({column}) AS max
            FROM players
            WHERE position = %s;
        """, (player_position,))

        sonuc = cursor.fetchone() #her bir column için işlem yap
        print(f"Query Result for {column}: {sonuc}")
        
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
    player_data_dict = {'CosineSimilarity': player_data.get('CosineSimilarity', None)}


    cursor.execute(f"""
        SELECT 
            MIN({column}) AS min,
            MAX({column}) AS max
        FROM Players
        WHERE Position = %s;
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

    columns = ['precision', 'longrangeshooting', 'diligence', 'dribblespeed', 
                'agility', 'vision','obstinacy', 'goalkeeping']
    player_data_dict = {column: player_data.get(column, None) for column in columns}  #Her bir columndaki veriyi player_data sözlüğünde tut
    sonuclar1 = {} 

    player_position = player_data["position"]
    for column in columns: #her bir sütundaki verilerin sapmasını al
        cursor.execute(f"""
            SELECT 
                AVG({column}) AS average,
                STDDEV({column}) AS stdev,
                MIN({column}) AS min,
                MAX({column}) AS max
            FROM players
            WHERE position = %s;
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

    cursor.execute("SELECT * FROM players WHERE package = %s ORDER BY playername", (package,))  
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


    cursor.execute("""SELECT playerid, PlayerName, overallrating, Position, Package 
                   FROM Players WHERE PlayerName ILIKE %s;""", ['%' + oyuncu_adi + '%'])
                  #Türkçe vb. karakterler için standartlaştır

    players = cursor.fetchall()
    
    return render_template('players.html', Players=players)

@app.route('/advanced_search', methods=['POST'])
def advanced_search():
    global cursor
    asd = "SELECT * FROM players WHERE 1=1"
    params = []
    
    filters = {
         "offensiveawareness": (request.form.get("offensiveawareness_min"), request.form.get("offensiveawareness_max")),
         "ballcontrol": (request.form.get("ballcontrol_min"), request.form.get("ballcontrol_max")),
         "dribbling": (request.form.get("dribbling_min"), request.form.get("dribbling_max")),
         "tightpossession": (request.form.get("tightpossession_min"), request.form.get("tightpossession_max")),
         "lowpass": (request.form.get("lowpass_min"), request.form.get("lowpass_max")),
         "loftedpass": (request.form.get("loftedpass_min"), request.form.get("loftedpass_max")),
         "finishing": (request.form.get("finishing_min"), request.form.get("finishing_max")),
         "header": (request.form.get("header_min"), request.form.get("header_max")),
         "setpiecetaking": (request.form.get("setpiecetaking_min"), request.form.get("setpiecetaking_max")),
         "curve": (request.form.get("curve_min"), request.form.get("curve_max")),
         "defensiveawareness": (request.form.get("defensiveawareness_min"), request.form.get("defensiveawareness_max")),
         "tackling": (request.form.get("tackling_min"), request.form.get("tackling_max")),
         "aggression": (request.form.get("aggression_min"), request.form.get("aggression_max")),
         "defensiveengagement": (request.form.get("defensiveengagement_min"), request.form.get("defensiveengagement_max")),
         "gkawareness": (request.form.get("gkawareness_min"), request.form.get("gkawareness_max")),
         "gkcatch": (request.form.get("gkcatch_min"), request.form.get("gkcatch_max")),
         "gkclearance": (request.form.get("gkclearance_min"), request.form.get("gkclearance_max")),
         "gkreflexes": (request.form.get("gkreflexes_min"), request.form.get("gkreflexes_max")),
         "gkreach": (request.form.get("gkreach_min"), request.form.get("gkreach_max")),
         "speed": (request.form.get("speed_min"), request.form.get("speed_max")),
         "acceleration": (request.form.get("acceleration_min"), request.form.get("acceleration_max")),    
         "kickingpower": (request.form.get("kickingpower_min"), request.form.get("kickingpower_max")),
         "jumping": (request.form.get("jumping_min"), request.form.get("jumping_max")),
         "physicalcontact": (request.form.get("physicalcontact_min"), request.form.get("physicalcontact_max")),   
         "balance": (request.form.get("balance_min"), request.form.get("balance_max")),  
         "stamina": (request.form.get("stamina_min"), request.form.get("stamina_max")),
         "precision": (request.form.get("precision_min"), request.form.get("precision_max")),
         "longrangeshooting": (request.form.get("longrangeshooting_min"), request.form.get("longrangeshooting_max")),
         "diligence": (request.form.get("diligence_min"), request.form.get("diligence_max")),
         "dribblespeed": (request.form.get("dribblespeed_min"), request.form.get("dribblespeed_max")),         
         "agility": (request.form.get("agility_min"), request.form.get("agility_max")),     
         "vision": (request.form.get("vision_min"), request.form.get("vision_max")),             
         "obstinacy": (request.form.get("obstinacy_min"), request.form.get("obstinacy_max")),
         "goalkeeping": (request.form.get("goalkeeping_min"), request.form.get("goalkeeping_max")),
    }


    for column, (min_val, max_val) in filters.items():
        min_val = int(min_val) if min_val else 0
        max_val = int(max_val) if max_val else 100


        if min_val != 0 or max_val != 100:
            asd += f" AND {column} BETWEEN %s AND %s"
            params.extend([min_val, max_val])

    print("Parameters:", params)


    cursor.execute(asd,(params))
    results = cursor.fetchall()

    return render_template('results.html', Players=results)



@app.route('/random_player')  #rastgele oyuncuya gitme fonksiyonu  
def random_player():
    global cursor
    cursor.execute("SELECT playerid FROM players")  
    player_ids = cursor.fetchall()  

    if not player_ids:
        return "Oyuncu bulunamadı", 404 

    random_player_id = random.choice(player_ids)[0]  
    return players_detail(random_player_id)

@app.route('/player/<int:player_id>/similar') #benzer oyuncuları bulma fonksiyonu
def similar_players(player_id):
    global cursor

    cursor.execute("""
        SELECT position, playingstyle, height, cosinesimilarity
        FROM players 
        WHERE playerid = %s;
    """, (player_id,))
    player_info = cursor.fetchone()
    
    if not player_info:
        return "Oyuncu bulunamadı", 404


    playing_style = player_info["playingstyle"]
    height = player_info["height"]
    cosine_value = player_info["cosinesimilarity"]
    cursor.execute("""
        SELECT playerid, playerName,overallrating, package, CosineSimilarity, Height 
        FROM players 
        WHERE playingStyle = %s
          AND ABS(Height - %s) <= %s
          AND ABS(CosineSimilarity - %s) <= %s
          AND playerid != %s
        ORDER BY ABS(CosineSimilarity - %s), ABS(Height - %s)
        LIMIT 10
    """, (playing_style, height, height * 0.015, cosine_value, 0.01, player_id, cosine_value, height * 0.015)) #Belirtilen özelliklere göre benzer profilleri bul, benzerlik daraltıtlıp genişletilebilir.
    
    benzer_oyuncular = cursor.fetchall()

    return benzer_oyuncular


@app.route('/player/<int:player_id>')  #oyuncu detay sayfası
def players_detail(player_id):
    global cursor

    benzer_oyuncular = similar_players(player_id)

    stat_groups = {
        "Offense": ["offensiveawareness", "finishing", "header", "kickingpower"],
        "Defense": ["defensiveawareness", "defensiveengagement", "tackling", "aggression"],
        "Dribbling": ["ballcontrol", "dribbling", "tightpossession", "balance"],
        "Passing": ["lowpass", "loftedpass", "curve", "setpiecetaking"],
        "Physical": ["height", "physicalcontact", "stamina", "speed", "acceleration", "jumping"],
        "Goalkeeping": ["gkawareness", "gkreflexes", "gkreach", "gkcatch", "gkclearance"],
    }

    cursor.execute("SELECT * FROM players WHERE playerid = %s", (player_id,)) #player_id içine ata
    player_data = cursor.fetchone()  #player_data içine sonuçları at

    if not player_data:
        return "Player Not Found", 404 

    cursor.execute("SELECT package, position, playingstyle, age,foot,weakfootaccuracy,weakfootusage,playerskills FROM players WHERE playerid = %s", (player_id,))
    info_data = cursor.fetchone() #player_data sayısal değerler tuttuğundan info_data oluştur
    
    cursor.execute("SELECT precision, longrangeshooting, diligence, dribblespeed,agility, vision,obstinacy, goalkeeping FROM players WHERE playerid = %s", (player_id,))
    combine_data = cursor.fetchone()

    cursor.execute("SELECT cosinesimilarity FROM players WHERE playerid = %s", (player_id,))
    cosine_data = cursor.fetchone()
    cosine_value = cosine_data[0]

    weak_foot_accuracy_class = accuracy_class(info_data["weakfootaccuracy"]) #zayıf ayak bilgisini bu sınıfta tut

    player_position = player_data[34]   #pozisyonu al
    player_data_dict_position, sonuclar = position_calculate(player_data, player_position) #pozisyon için calculate fonksiyonu işlemini yap hem dict hem sonuclara aktar
    
    player_data_dict, a_cosinesim_class = cosinesim_class(player_data, player_position, cosine_value)


    player_data_dict_combine, sonuclar1 = combined_abilities(player_data)

    likes = player_data.get('likes', 0)

    player_data_dict = {**player_data_dict_position, **player_data_dict_combine}

    return render_template('players_detail.html', player_name=player_data['playername'], player_data=player_data_dict, stat_groups=stat_groups, 
                           sonuclar=sonuclar,info_data=info_data, weak_foot_accuracy_class=weak_foot_accuracy_class,
                           combine_data=combine_data,sonuclar1=sonuclar1,cosine_data=cosine_data,cosine_value=cosine_value,
                           a_cosinesim_class=a_cosinesim_class,benzer_oyuncular=benzer_oyuncular,likes=likes) #html'de görüntülenecek veriler

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
