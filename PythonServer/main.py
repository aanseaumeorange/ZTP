import netmiko
import pika
import time
from equipement import *
from thread_equipement import *
import os

#Equipement
#ip=None, device_type=None, username=None, password=None, secret=None)

# In clear for now, no need for secrecy, those are just for the staging phase
default_login    = "admin"
default_password = "admin"
default_secret   = "admin"

r1 = Equipement("192.168.57.11", "cisco_ios", default_login, default_password, default_secret)
r2 = Equipement("192.168.57.12", "cisco_ios", default_login, default_password, default_secret)

show_int_br = "sh ip int br"

def test_sh_version():
    equipement_list = [r1, r2]

    for equipement in equipement_list :
        equipement.ssh_connect()
        equipement.enable_mode()
        version = equipement.execute("sh ip int br")
        print (version)
        equipement.ssh_close()

def test_thread_rabbit():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        #channel.queue_declare(queue=r1.ip)
        #channel.queue_declare(queue=r1.ip)

        thread1 = ThreadedEquipement(r1)
        thread2 = ThreadedEquipement(r2)
        thread2.start()
        thread1.start()

        time.sleep(1)

        channel.basic_publish(exchange='', routing_key=r2.ip, body=show_int_br)
        channel.basic_publish(exchange='', routing_key=r1.ip, body=show_int_br)
        print("Send sh ip int br r2 & r1")

        time.sleep(1)

        channel.basic_publish(exchange='', routing_key=r2.ip, body='close')
        channel.basic_publish(exchange='', routing_key=r1.ip, body='close')
        print("Send close r2 & r1")

        thread1.join()
        thread2.join()

        connection.close()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        channel.close()

def test_rabbit():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.basic_publish(exchange='', routing_key=r2.ip, body=show_int_br)
    channel.basic_publish(exchange='', routing_key=r1.ip, body=show_int_br)
    print("Send sh ip int br r2 & r1")

    time.sleep(1)

    channel.basic_publish(exchange='', routing_key=r2.ip, body='close')
    channel.basic_publish(exchange='', routing_key=r1.ip, body='close')
    print("Send close r2 & r1")

    sleep(1)

    connection.close()

def stager(message_dhcp):
    # Get the first address and iterate until the last, use same variable
    equipent_address = list(map(int, message_dhcp["range_start"].split(".")))
    range_end = equipent_address[3] + (int(message_dhcp["nb_switch"]))
    equipement_list = []

    print(equipent_address)
    print(range_end)

    while (equipent_address[3] < range_end):
        equipement_list.append(Equipement(".".join(map(str, equipent_address)),
            message_dhcp["constructor"], default_login, default_password, default_secret))
        equipent_address[3] += 1

    thread_pool = []

    for eq in equipement_list:
        thread_pool.append(ThreadedEquipement(eq))
        thread_pool[len(thread_pool) - 1].start()

    return thread_pool
    print("end stager")

test_rabbit()
message = {
  "type": "response",
  "information": "DHCP",
  "nb_switch": 2,
  "range_start": "192.168.57.11",
  "range_end": "192.168.57.12",
  "constructor": "cisco_ios",
  "method": "..."
}
pool = stager(message)

for t in pool:
    t.join()
#test_sh_version()
#test_thread_rabbit()

print ("!!!END!!!")
