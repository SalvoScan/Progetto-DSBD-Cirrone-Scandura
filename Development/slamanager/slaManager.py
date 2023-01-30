from flask import Flask, request
import os
from prometheus_api_client import PrometheusConnect 
from arimaPredictor import *
import arimaPredictor as arima

time_prediction = 10
set_metriche = {}
prom = PrometheusConnect(url="http://15.160.61.227:29090", disable_ssl=True)

app = Flask(__name__)

@app.route("/create", methods=['POST'])
def create():
    global set_metriche

    content = request.json

    for k, v in content.items():
        value_list = []
        for _, v1 in v.items():
           value_list.append(v1)
        set_metriche[k] = value_list

    return "Set di metriche creato"

@app.route("/violazioni")
def violazioni():
    global set_metriche, prom

    outer_list = []
    for k, v in set_metriche.items():
        inner_list = []
        inner_list.append(k)

        time_list = ["1h", "3h", "12h"]
        for t in time_list:
            inner_list.append(t)
            start_time = parse_datetime(t)
            end_time = parse_datetime("now")
            chunk_size = dt.timedelta(minutes=10)
            label_config = {'job':v[0]}
            metric_data = prom.get_metric_range_data(metric_name=k, label_config=label_config, start_time=start_time,
                end_time=end_time, chunk_size=chunk_size,)
            metric_object_list = MetricsList(metric_data)
            my_metric_object = metric_object_list[0]
            metric_df = MetricRangeDataFrame(metric_data)
            
            count = 0
            for val in (metric_df['value']):
                if val < v[1] or val > v[2]:
                    count += 1
            inner_list.append(count)
            
        outer_list.append(inner_list)
    
    title = "Numero di violazioni nelle ultime 1h, 3h, 12h<br><br>"
    text = ""
    for o in outer_list:
        text = text + "<br>" + o[0] + " -> " + o[1] + ": " + str(o[2]) + " " + o[3] + ": " + str(o[4]) \
            + " " + o[5] + ": " + str(o[6])

    return title + text

@app.route("/violazioni_future")
def violazioni_future():
    global set_metriche, prom

    outer_list=[] 
    for k, v in set_metriche.items():
        inner_list=[]
        inner_list.append(k)
        _, fcast = arima.calcola_predizioni(prom, k , v[0], time_prediction)  
    
        count = 0
        for val in fcast:
            if val < v[1] or val > v[2]:
                count += 1 
     
        inner_list.append(count)
        outer_list.append(inner_list)

    title = "Predizione violazioni future SLA<br><br>"
    text = ""
    for o in outer_list:
        text = text + "<br>" + o[0] + " -> " + str(o[1])

    return title + text

@app.route("/state")
def state():
    global set_metriche

    return set_metriche

@app.route("/update", methods=['POST'])
def update():
    global set_metriche

    content = request.json

    metriche = []
    count = 0
    for k, v in content.items():
        value_list = []
        value_list.append(k)
        for _, v1 in v.items():
           value_list.append(v1)
        metriche.append(value_list)

    if bool(set_metriche):
        for k, v in set_metriche.items():
            for m in metriche:
                if k == m[0]:
                    set_metriche[k] = [m[1], m[2], m[3]]
                    count += 1
        if count != len(metriche) and count != 0:
            return "Non tutte le metriche inserite sono state aggiornate"
        elif count == 0:
            return "Metriche non valide"
        else:
            return "Metriche aggiornate"
    else:
        return "Non ci sono metriche da aggiornare. Procedi con CREATE"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=port)