import pika
import uuid
import json

class RPC_client(object):
    def __init__(self):
        credentials = pika.PlainCredentials('ztp', 'admin_ztp')
        parameters = pika.ConnectionParameters("172.20.93.97", 5672, '/', credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='', routing_key='rpc_queue',
            properties=pika.BasicProperties(reply_to = self.callback_queue,
            correlation_id = self.corr_id), body=json.dumps(n))
        while self.response is None:
            self.connection.process_data_events()
        return (json.loads(self.response))

    def request_dhcp(self):
        dico = {}
        dico["type"] = "request"
        dico["information"] = "DHCP"
        dhcp_response = rpc_client.call(dico)
        return dhcp_response

    def request_switch(self, sn):
        dico = {}
        dico["type"] = "request"
        dico["information"] = "switch"
        dico["serial_number"] = sn
        switch_response = rpc_client.call(dico)
        return switch_response


rpc_client = RPC_client()

print(" [x] Requesting for DHCP")
dhcp_response = rpc_client.request_dhcp()
print(" [.] Got {0} switch, Range: {1} to {2}, Constructor: {3}, Method: {4}".format(
    dhcp_response["nb_switch"], dhcp_response["range_start"], dhcp_response["range_end"],
    dhcp_response["constructor"], dhcp_response["method"]))

print(" [x] Requesting for SN : 1234567NGH")
switch_response = rpc_client.request_switch("1234567NGH")

print(" [.] Got {0} switch, Hostname {1}, Configuration File {2}, Firmware {3}".format(
    switch_response["serial_number"], switch_response["hostname"], switch_response["config_file"],
    switch_response["firmware"]))
