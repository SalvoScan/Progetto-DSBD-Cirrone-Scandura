from confluent_kafka import Consumer
import threading
from conndb import *

TOPIC = "prometheusdata"
c0 = Consumer({
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'mygroup',
    'auto.offset.reset': 'earliest'
})
c1 = Consumer({
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'mygroup',
    'auto.offset.reset': 'earliest'
})
c2 = Consumer({
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'mygroup',
    'auto.offset.reset': 'earliest'
})

def init_function():
    i = True
    while i:
        # Connessione al Database
        database = Conndb()
        db = database.db
        cursor = database.cursor

        if cursor != 0:
            i = False

    create_table = "create table metadati(\
        id INT AUTO_INCREMENT, \
        metrica VARCHAR(30), \
        p_value DOUBLE, time VARCHAR(22), \
        primary key (id)\
    );"

    try:
        cursor.execute(create_table)
        print("Table METADATI created successfully")
    except mysql.connector.ProgrammingError as err:
        print("Error: {}".format(err))

    create_table = "create table stagionalita(\
        id INT AUTO_INCREMENT, \
        metrica VARCHAR(30), \
        seasonal DOUBLE, time VARCHAR(22), \
        primary key (id)\
    );"

    try:
        cursor.execute(create_table)
        print("Table SEASONAL created successfully")
    except mysql.connector.ProgrammingError as err:
        print("Error: {}".format(err))

    create_table = "create table correlazione(\
        id INT AUTO_INCREMENT, \
        metrica VARCHAR(30), \
        corr DOUBLE, time VARCHAR(22), \
        primary key (id)\
    );"

    try:
        cursor.execute(create_table)
        print("Table CORRELAZIONE created successfully")
    except mysql.connector.ProgrammingError as err:
        print("Error: {}".format(err))

    create_table = "create table dataStatistics(\
        id INT AUTO_INCREMENT, \
        metrica VARCHAR(30), \
        max DOUBLE, min DOUBLE, avg DOUBLE, devstd DOUBLE, durata VARCHAR(5), time VARCHAR(22), \
        primary key (id)\
    );"

    try:
        cursor.execute(create_table)
        print("Table DATASTATISTICS created successfully")
    except mysql.connector.ProgrammingError as err:
        print("Error: {}".format(err))

    create_table = "create table dataPredictions(\
        id INT AUTO_INCREMENT, \
        metrica VARCHAR(30), \
        max DOUBLE, min DOUBLE, avg DOUBLE, time VARCHAR(22), \
        primary key (id)\
    );"

    try:
        cursor.execute(create_table)
        print("Table DATAPREDICTIONS created successfully")
    except mysql.connector.ProgrammingError as err:
        print("Error: {}".format(err))

    # Disconnessione al Database
    cursor.close()
    db.close()

def thread_function(consumer):
    i = True
    while i:
        # Connessione al Database
        database = Conndb()
        db = database.db
        cursor = database.cursor

        if cursor != 0:
            i = False

    count02 = 5
    count1 = 15
    i = 0
    j = 0
    k = 0
    consumer.subscribe([TOPIC])
    while True:                
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue     
        
        argument = msg.partition()         
        if argument == 0:
            print("Partizione: ", argument) 
            msg = msg.value().decode('utf-8')
            print("Received message: ", msg)
            msg = msg.split(" ")
            msg[1] = round(float(msg[1]), 4)
            seasonal = msg[2]
            corr = msg[3]
            tempo = msg[4]+" "+msg[5][0:11]
            q1 = "insert into metadati(metrica, p_value, time) values('" \
                + msg[0] + "', " + str(msg[1]) + ", '" + tempo + "');"
            try:
                cursor.execute(q1)
                db.commit()
            except mysql.connector.ProgrammingError as err:
                print("Error: {}".format(err))
            
            seasonal = seasonal[1:len(seasonal)-1]
            seasonal = seasonal.split(",")
            for j in range(0, len(seasonal)):
                seasonal[j] = round(float(seasonal[j]), 2)
                q = "insert into stagionalita(metrica, seasonal, time) values('" \
                    + msg[0] + "', " + str(seasonal[j]) + ", '" + tempo + "');"
                try:
                    cursor.execute(q)
                    db.commit()
                except mysql.connector.ProgrammingError as err:
                    print("Error: {}".format(err))

            corr = corr[1:len(corr)-1]
            corr = corr.split(",")
            for j in range(0, len(corr)):
                corr[j] = round(float(corr[j]), 2)
                q = "insert into correlazione(metrica, corr, time) values('" \
                    + msg[0] + "', " + str(corr[j]) + ", '" + tempo + "');"
                try:
                    cursor.execute(q)
                    db.commit()
                except mysql.connector.ProgrammingError as err:
                    print("Error: {}".format(err))
            i += 1            
            if i == count02:
                consumer.commit()
                consumer.close()
                cursor.close()
                db.close()
                return
        
        elif argument == 1:
            print("Partizione: ", argument)
            msg = msg.value().decode('utf-8')
            print("Received message: ", msg)
            
            msg = msg.split(" ")
            for i in range(1, 5):
                msg[i] = round(float(msg[i]), 2)
            query = "insert into dataStatistics(metrica, max, min, avg, devstd, durata, time) values ('" \
                + msg[0] + "', " + str(msg[1]) + ", " + str(msg[2]) + ", " + str(msg[3]) + ", " + str(msg[4]) \
                    + ", '" + msg[5] + "', '" + msg[6]+" "+msg[7][0:11] + "');"
            try:
                cursor.execute(query)
                db.commit()
            except mysql.connector.ProgrammingError as err:
                print("Error: {}".format(err))
            j += 1
            if j == count1:
                consumer.commit()
                consumer.close()
                cursor.close()
                db.close()
                return
        
        elif argument == 2:
            print("Partizione: ", argument)
            msg = msg.value().decode('utf-8')
            print("Received message: ", msg)
            
            msg = msg.split(" ")
            for i in range(1, 4):
                msg[i] = round(float(msg[i]), 2)
            query = "insert into dataPredictions(metrica, max, min, avg, time) values ('" \
                + msg[0] + "', " + str(msg[1]) + ", " + str(msg[2]) + ", " + str(msg[3]) \
                    + ", '" + msg[4]+" "+msg[5][0:11] + "');"
            try:
                cursor.execute(query)
                db.commit()
            except mysql.connector.ProgrammingError as err:
                print("Error: {}".format(err))
            
            k += 1
            if k == count02:
                consumer.commit()
                consumer.close()
                cursor.close()
                db.close()
                return

        else:
            print("Errore partizione")
        
if __name__ == "__main__":
    print("Starting")
    th_init = threading.Thread(target=init_function)
    th0 = threading.Thread(target=thread_function, args=(c0,))
    th1 = threading.Thread(target=thread_function, args=(c1,))
    th2 = threading.Thread(target=thread_function, args=(c2,))

    th_init.start()
    th_init.join()
    
    th0.start()
    th1.start()
    th2.start()

    th0.join()
    th1.join()
    th2.join()

    print("Ending")