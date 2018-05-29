import threading
from random import randint
from time import sleep
import pika

class ThreadedEquipement(threading.Thread):
    # This equipement queue
    connection = None
    channel = None
    callback_queue = None

    def __init__(self, equipement):
        threading.Thread.__init__(self)
        self.equipement = equipement
        #self.staging_channel = staging_channel

    #TODO remake connection with good credidential
    #TODO connect to single queue for site
    def init_connection(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.equipement.ip)
        self.channel.basic_consume(self.callback, queue=self.equipement.ip, no_ack=True)

        print("Init thread channel for: " + self.equipement.ip)

    def handle_ssh(self, action):
        if (action == "connect" and not self.equipement.check_ssh()):
            self.equipement.ssh_connect()
            self.equipement.enable_mode()
        elif (action == "close" and self.equipement.check_ssh()):
            self.equipement.ssh_close()

    def callback(self, channel, method, properties, body):
        print("Thread msg body: " + body)
        if (body == "close"):
            self.handle_ssh("close")
            self.channel.close()
            return

        result = self.equipement.execute(body)
        print(result)

    def run(self):
        self.init_connection()

        self.handle_ssh("connect")

        self.channel.start_consuming()
        print("Thread closed")
