from flask import Flask, request
import os
from conndb import *

app = Flask(__name__)

@app.route("/metrics/predictions")
def getPredictions():
    database = 0
    db = 0
    cursor = 0
    i = True
    while i:
        # Connessione al Database
        database = Conndb()
        db = database.db
        cursor = database.cursor

        if cursor != 0:
            i = False
    
    query = "select * from dataPredictions"

    try:
        cursor.execute(query)
        results = cursor.fetchall()

        res_list = []
        for result in results:
            res = result[1] + " -> Max: " + str(result[2]) + " Min: " + str(result[3]) + " Avg: " + str(result[4]) \
            + " Time: " + result[5]
            res_list.append(res)
    except mysql.connector.ProgrammingError as err:
        print("Error: {}".format(err))

    title = "Predizione dei valori nei successivi 10 minuti<br><br>" 
    text = ""
    for t in res_list:
        text = text + "<br>" + t
    
    cursor.close()
    db.close()
    return title + text

@app.route("/metrics/statistics")
def getStatistics():
    database = 0
    db = 0
    cursor = 0
    i = True
    while i:
        # Connessione al Database
        database = Conndb()
        db = database.db
        cursor = database.cursor

        if cursor != 0:
            i = False
    
    query = "select * from dataStatistics"

    try:
        cursor.execute(query)
        results = cursor.fetchall()

        res_list = []
        for result in results:
            res = result[1] + " -> Max: " + str(result[2]) + " Min: " + str(result[3]) + " Avg: " + str(result[4]) \
            + " DevStd: " + str(result[5]) + " Durata: " + result[6] + " Time: " + result[7]
            res_list.append(res)
    except mysql.connector.ProgrammingError as err:
        print("Error: {}".format(err))

    title = "Valori statistici delle metriche calcolati per 1h, 3h, 12h<br><br>"
    text = ""
    for t in res_list:
        text = text + "<br>" + t
    
    cursor.close()
    db.close()
    return title + text

@app.route("/metrics/metadati")
def getMetadati():
    database = 0
    db = 0
    cursor = 0
    i = True
    while i:
        # Connessione al Database
        database = Conndb()
        db = database.db
        cursor = database.cursor

        if cursor != 0:
            i = False
    

    query = "select * from metadati"

    try:
        cursor.execute(query)
        results = cursor.fetchall()

        outer_list = []
        for result in results:
            inner_list = []
            inner_list.append(result[1])
            inner_list.append(result[2])
            inner_list.append(result[3])
            metric = result[1]
            time = result[3]
            
            q1 = "select (seasonal) from stagionalita where metrica='" + metric + "' and time='" + time + "';"
            try:
                cursor.execute(q1)
                res1 = cursor.fetchall()
                res1_list = []
                for r1 in res1:
                    v1 = r1[0]
                    res1_list.append(v1)
                inner_list.append(res1_list)
            except mysql.connector.ProgrammingError as err:
                print("Error: {}".format(err))

            q2 = "select (corr) from correlazione where metrica='" + metric + "' and time='" + time + "';"
            try:
                cursor.execute(q2)
                res2 = cursor.fetchall()
                res2_list = []
                for r2 in res2:
                    v2 = r2[0]
                    res2_list.append(v2)
                inner_list.append(res2_list)
            except mysql.connector.ProgrammingError as err:
                print("Error: {}".format(err))

            outer_list.append(inner_list)
    except mysql.connector.ProgrammingError as err:
        print("Error: {}".format(err))

    title = "Valori metadati: Stazionarieta' - Stagionalita' - Autocorrelazione<br><br>"
    text = ""
    for t in outer_list:
        season = "["
        for s in t[3]:
            season = season + str(s) + ","
        season = season[0:len(season)-1] + "]"
        correl = "["
        for c in t[4]:
            correl = correl + str(c) + ","
        correl = correl[0:len(correl)-1] + "]"
        text = text + "<br>" + t[0] + " -> P_Value: " + str(t[1]) + " Seasonal: " + season \
        + " Autocorrelation: " + correl + " Time: " + t[2]
    
    cursor.close()
    db.close()
    return title + text

@app.route("/metrics/all")
def getMetrics():
    database = 0
    db = 0
    cursor = 0
    i = True
    while i:
        # Connessione al Database
        database = Conndb()
        db = database.db
        cursor = database.cursor

        if cursor != 0:
            i = False
    
    query = "select distinct (metrica) from metadati"

    try:
        cursor.execute(query)
        results = cursor.fetchall()
    except mysql.connector.ProgrammingError as err:
                print("Error: {}".format(err))

    cursor.close()
    db.close()
    return results

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=port)