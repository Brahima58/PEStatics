import pyodbc
import math



conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'SERVER=server_adi;'
                      'DATABASE=db_adi;'
                      'Trusted_Connection=yes;') #Veritabanı bağlantısını kurun
cursor = conn.cursor()

cursor.execute("SELECT * FROM Players")
all_players_data = cursor.fetchall()

columns = ['OverallRating', 'OffensiveAwareness', 'BallControl', 'Dribbling',
           'TightPossession', 'LowPass', 'LoftedPass', 'Finishing', 'Header',
           'SetPieceTaking', 'Curve', 'DefensiveAwareness', 'Tackling',
           'Aggression', 'DefensiveEngagement', 'GKAwareness', 'GKCatch',
           'GKClearance', 'GKReflexes', 'GKReach', 'Speed', 'Acceleration',
           'KickingPower', 'Jumping', 'PhysicalContact', 'Balance', 'Stamina', 'Height']


for player_data in all_players_data:
    player_id = player_data[0]
    position = player_data[34]
    playstyle = player_data[36]

    averages = {}

    for column in columns:
        cursor.execute(f"""
            SELECT 
                AVG({column}) AS average,
                STDEV({column}) AS stdev
            FROM Players
            WHERE Position = ?;
        """, position)
        sonuc_position = cursor.fetchone()
        average_position, stdev_position = sonuc_position

        cursor.execute(f"""
            SELECT 
                AVG({column}) AS average,
                STDEV({column}) AS stdev
            FROM Players
            WHERE PlayingStyle = ?;
        """, playstyle)
        if playstyle == "---" :
            average_playstyle, stdev_playstyle = 0, 0
        else:
            sonuc_playstyle = cursor.fetchone()
            average_playstyle, stdev_playstyle = sonuc_playstyle

        if column == 'Height':
            column_index = 31
        else:
            column_index = columns.index(column) + 2

        sayi_player = player_data[column_index]

        #Veriler arasındaki benzerliği bulmak için kosinüs benzerliği işlemi yap

        if average_playstyle > average_position and stdev_position != 0:
            normalized_value = (sayi_player - average_position) / stdev_playstyle #oyuncu verisini olduğu gibi almak yerine (veriler çok yüksek oranda 100 ve 70 arasında olduğu için) normalize et ve bunu pozisyonuna göre yap
        else:
            normalized_value = 0
        averages[column] = normalized_value

    noktasal_carpim = 0 
    a = 0
    b = 0
    for column in columns:
        if column == 'Height':
            column_index = 31
        else:
            column_index = columns.index(column) + 2

        sayi_player = player_data[column_index]
        sayi_average = averages[column]

        noktasal_carpim += sayi_average * sayi_player #Kosinüs benzerliği işlemi için öncelikle noktasal çarpım hesaplanmalı
        a += sayi_player ** 2
        b += sayi_average ** 2

    a_player = math.sqrt(a)
    b_average = math.sqrt(b)

    if a_player == 0 or b_average == 0:
        cosine_similarity = 0
    else:
        cosine_similarity = noktasal_carpim / (a_player * b_average)  #Kosinüs benzerliği formülü 

    #matematiksel işlem yapılacağı için index ile çağırmak yerine isimlendirildi, ileride farklı işlemler eklenince kolayca ulaşılabilir

    overall_rating = player_data.OverallRating or 0
    offensive_awareness = player_data.OffensiveAwareness or 0
    ball_control = player_data.BallControl or 0
    dribbling = player_data.Dribbling or 0
    tight_possession = player_data.TightPossession or 0
    low_pass = player_data.LowPass or 0
    lofted_pass = player_data.LoftedPass or 0
    finishing = player_data.Finishing or 0
    header = player_data.Header or 0
    set_piece_taking = player_data.SetPieceTaking or 0
    curve = player_data.Curve or 0
    defensive_awareness = player_data.DefensiveAwareness or 0
    tackling = player_data.Tackling or 0
    aggression = player_data.Aggression or 0
    defensive_engagement = player_data.DefensiveEngagement or 0
    gk_awareness = player_data.GKAwareness or 0
    gk_catch = player_data.GKCatch or 0
    gk_clearance = player_data.GKClearance or 0
    gk_reflexes = player_data.GKReflexes or 0
    gk_reach = player_data.GKReach or 0
    speed = player_data.Speed or 0
    acceleration = player_data.Acceleration or 0
    kicking_power = player_data.KickingPower or 0
    jumping = player_data.Jumping or 0
    physical_contact = player_data.PhysicalContact or 0
    balance = player_data.Balance or 0
    stamina = player_data.Stamina or 0
    height = player_data.Height or 0
    skills = player_data.PlayerSkills

    vizyon = 0
    thizi = 0
    ceviklik = 0
    inatcilik = 0
    caliskanlik = 0
    usut = 0
    hava = 0
    kalecilik = 0

    lrc = 'Long-Range Curler' in skills
    lrc += usut * 0.1
    lrs = 'Long Range Shooting' in skills
    lrs += usut * 0.1
    fs = 'Fighting Spirit' in skills
    fs += inatcilik * 0.1 or caliskanlik * 0.1
    otp = 'One-touch Pass' in skills
    otp += vizyon * 0.1
    tp = 'Through Passing' in skills
    tp += vizyon * 0.2
    wp = 'Weighted Pass' in skills
    wp += vizyon * 0.01
    llp = 'Low Lofted Pass' in skills
    llp += vizyon * 0.01
    tb = 'Track Back' in skills
    tb += caliskanlik * 0.1
    md = 'Momentum Dribbling' in skills
    md += ceviklik * 0.1
    ks = 'Knuckle Shot' in skills
    ks += usut * 0.01
    bc = 'Blitz Curler' in skills
    bc += usut * 0.1
    ds = 'Dipping Shot' in skills
    ds += usut * 0.01
    rs = 'Rising Shot' in skills
    rs += usut * 0.01
    fts = 'First-time Shot' in skills
    fts += usut * 0.01
    pc = 'Pinpoint Crossing' in skills
    pc += vizyon * 0.1
    gcp = 'Game-changing Pass' in skills
    gcp += vizyon * 0.1
    vp = 'Visionary Pass' in skills
    vp += vizyon * 0.05
    gps = 'GK Penalty Saver' in skills
    gps += kalecilik * 0.05
    
    delicilik = int((speed * 0.30) + (acceleration * 0.30) + (physical_contact * 0.30) + (offensive_awareness * 0.10))
    usut = int((lrs + lrc) * 0.1 + (kicking_power * 0.8) + (finishing * 0.2) + ks + bc + ds + rs + fts)
    caliskanlik = int((stamina * 0.55) + (aggression * 0.28) + (speed * 0.1) + (acceleration * 0.07) + fs + tb)
    thizi = int((speed * 0.60) + (dribbling * 0.30) + (ball_control * 0.10))
    ceviklik = int((dribbling * 0.40) + (acceleration * 0.15) + (balance * 0.15) + (ball_control * 0.15) + (tight_possession * 0.15) + md)
    vizyon = int((low_pass * 0.45) + (lofted_pass * 0.45) + (curve * 0.1) + otp  + tp  + llp  + wp  + pc + gcp  + vp )
    inatcilik = int((speed * 0.30) + (physical_contact * 0.30) + (aggression * 0.20) + (stamina * 0.20) + fs )
    kalecilik = int((gk_clearance * 0.20) + (gk_reflexes * 0.20) + (gk_awareness * 0.20) + (gk_catch * 0.20) + (gk_reach * 0.20) +
                    ((height - 185) / (210 - 185) * 10) + gps )

    cursor.execute("""
            UPDATE Players
            SET Precision = ?, LongRangeShooting = ?, Diligence = ?, DribbleSpeed = ?, Agility = ?, Vision = ?, Obstinacy = ?, GoalKeeping = ?, CosineSimilarity = ?
            WHERE PlayerID = ?
        """,
                   delicilik, usut, caliskanlik, thizi, ceviklik, vizyon, inatcilik, kalecilik,cosine_similarity,player_id)

    print(player_id)

conn.commit()
conn.close()
