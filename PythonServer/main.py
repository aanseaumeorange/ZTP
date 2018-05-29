import netmiko
import pika
import time
from equipement import *
from thread_equipement import *

#Equipement
#ip=None, device_type=None, username=None, password=None, secret=None)

# In clear for now, no need for secrecy, those are just for the staging phase
default_login    = "admin"
default_password = "admin"
default_secret   = "admin"

r1 = Equipement("192.168.57.11", "cisco_ios", default_login, default_password, default_secret)
r2 = Equipement("192.168.58.15", "cisco_ios", default_login, default_password, default_secret)

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
        #time.sleep(2)
        #channel.queue_delete(queue=r1.ip)
        #channel.queue_delete(queue=r2.ip)


        thread1.join()
        thread2.join()

        connection.close()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        channel.close()

#test_sh_version()
test_thread_rabbit()
print ("!!!END!!!")
