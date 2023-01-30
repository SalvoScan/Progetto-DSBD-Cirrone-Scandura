from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
import sys

class Produttore:
    def __init__(self):

        broker = "kafka:9092"
        self.topic = "prometheusdata"

        conf = {'bootstrap.servers': broker}

        # Create Producer instance
        self.p = Producer(**conf)
        
        self.admin_client = AdminClient({
            "bootstrap.servers": "kafka:9092"
        })    
     
    def delivery_callback(self, err, msg):
        if err:
            sys.stderr.write('%% Message failed delivery: %s\n' % err)           
        else:
            sys.stderr.write('%% Message delivered to %s [%d] @ %d\n' %
                             (msg.topic(), msg.partition(), msg.offset()))