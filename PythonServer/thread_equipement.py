import threading
from random import randint
from time import sleep
import pika

class ThreadedEquipement(threading.Thread):
    # This equipement queue
    connection = None
    channel = None

    def __init__(self, equipement):
        threading.Thread.__init__(self)
        self.equipement = equipement
        #self.staging_channel = staging_channel

    def init_connection(self):

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.equipement.ip)


        print("Init thread channel for: " + self.equipement.ip)

    def callback(self, channel, method, properties, body):
        print("Thread print: {}".format(body))
        if (body == "close"):
            self.channel.close()

    def run(self):
        #connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        #channel = connection.channel()
        #channel.queue_declare(queue=self.equipement.ip)
        self.init_connection()


        self.channel.basic_consume(self.callback, queue=self.equipement.ip, no_ack=True)

        self.channel.start_consuming()
        print("Thread closed")
