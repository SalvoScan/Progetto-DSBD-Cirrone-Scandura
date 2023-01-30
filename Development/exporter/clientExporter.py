import requests
import time
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client import start_http_server

class DatiCollection(object):
   
    def __init__(self):
        pass
          
    def collect(self):
        resp = requests.get(url=f"http://monitoring:8500/getDati")
        status_data = resp.json()
        for key, value in status_data.items():
            gauge = GaugeMetricFamily(key, "tempo esecuzione ", labels=[key])
            gauge.add_metric([key], value[0] )
            yield gauge     

if __name__ == "__main__":
    start_http_server(9000)
    REGISTRY.register(DatiCollection())
    while True: 
        time.sleep(1)
    
