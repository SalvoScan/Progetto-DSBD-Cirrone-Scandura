from prometheus_api_client import PrometheusConnect, MetricsList, MetricSnapshotDataFrame, MetricRangeDataFrame
from datetime import timedelta
from prometheus_api_client.utils import parse_datetime
from setMetadati import *
import setMetadati as meta
from arimaPredictor import *
import arimaPredictor as arima
from produttore import *
import requests
from datetime import datetime

p = Produttore()
time_prediction=10
prom = PrometheusConnect(url="http://15.160.61.227:29090", disable_ssl=True)

metrics = {'availableMem':'summary', 'cpuLoad':'summary', 'diskUsage':'summary', \
    'cachedMem':'memory', 'bootTime':'system'}

req = "http://monitoring:8500/setDati"

n=True
while n == True:
    print('Controllo presenza topic prometheusdata in kafka')
    listaTopic=p.admin_client.list_topics().topics   
    for k, v in listaTopic.items():
        if k == p.topic:
            print('Topic prometheusdata presente in kafka')
            n=False  
    if n == True:
        topic_list = []
        topic_list.append(NewTopic("prometheusdata", 3, 1))
        print('Creazione Topic ')
        print(topic_list)
        p.admin_client.create_topics(topic_list)
        break

req_data={}
for k, v in metrics.items():

    label_config = {'job':v}
    queryResult = prom.get_current_metric_value(metric_name=k, label_config=label_config)
    metric_df = MetricSnapshotDataFrame(queryResult)

    print("METRICA: ", k)
    arima_result_list, _=arima.calcola_predizioni(prom, k , v, time_prediction)   
    date = datetime.now()   
    
    val = k 
    for i in range (0, len(arima_result_list)):
        val = val +' '+ str(arima_result_list[i])
    
    val = val + " "+ str(date)
    
    try:
        print('INVIO NELLA PARTIZIONE 2')
        print(val)
        p.p.produce(topic=p.topic, partition=2, value=val, callback=p.delivery_callback)
        p.p.poll(0)
    except BufferError:
        sys.stderr.write('%% Local producer queue is full (%d messages awaiting delivery): try again\n' %
                         len(p))

    p_value, seasonal, corr =meta.calcola_metadati(metric_df)

    seas = "["
    for s in range(0, len(seasonal)):
        seas = seas + str(seasonal[s]) + ","
    seas = seas[0:len(seas)-1] + "]"

    correl = "["
    for c in corr:
        correl = correl + str(c) + ","
    correl = correl[0:len(correl)-1] + "]"

    val = k + " " + str(p_value) + " " + seas + " " + correl + " " + str(date)

    try:
        print('INVIO NELLA PARTIZIONE 0')
        print(val)
        p.p.produce(topic=p.topic, partition=0, value=val, callback=p.delivery_callback)
        p.p.poll(0)
    except BufferError:
        sys.stderr.write('%% Local producer queue is full (%d messages awaiting delivery): try again\n' %
                         len(p))

    time_list = ["1h", "3h", "12h"]
    #meta_max_min_avg_dev
    for t in time_list:
        first = datetime.now()
        start_time = parse_datetime(t)
        end_time = parse_datetime("now")
        chunk_size = timedelta(minutes=10)
        label_config = {'job':v}
        metric_data = prom.get_metric_range_data(metric_name=k, label_config=label_config, start_time=start_time,
            end_time=end_time, chunk_size=chunk_size,)
        metric_object_list = MetricsList(metric_data)
        my_metric_object = metric_object_list[0]
        metric_df = MetricRangeDataFrame(metric_data)

        max_val = metric_df['value'].max()
        min_val = metric_df['value'].min()
        mean_val = metric_df['value'].mean()
        stddev_val = metric_df['value'].std()

        second = datetime.now()
        seconds = (second-first).total_seconds()
        provaKey= k+"_time_"+t        
        req_data[provaKey] = [seconds]   

        val = k + ' ' + str(max_val)+ ' '+ str(min_val)+' ' +str(mean_val)+' '+str(stddev_val)+ ' '+ t + ' '+ str(date)
        try:
            print('INVIO NELLA PARTIZIONE 1')
            print(val)
            p.p.produce(topic=p.topic, partition=1, value=val, callback=p.delivery_callback)
            p.p.poll(0)
        except BufferError:
            sys.stderr.write('%% Local producer queue is full (%d messages awaiting delivery): try again\n' %
                            len(p))
response = requests.post(req, json = req_data)                       
p.p.flush()