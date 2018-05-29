import ThreadedEquipement from thread_equipement
import Equipement from equipement
import os
#{
#  "type": "response",
#  "information": "DHCP",
#  "nb_switch": "...",
#  "range_start": "...",
#  "range_end": "...",
#  "constructor": "...",
#  "method": "..."
#}

default_login    = "admin"
default_password = "admin"
default_secret   = "admin"

class Stager(object):
    connection = None
    channel = None

    def __init__(self, ip_dc, stock_name):
      self.ip_dc = ip_dc
      self.stock_name = stock_name

    def generate_equipement(self, message):
        # Get the first address and iterate until the last, use same variable
        equipent_address = list(map(int, message["range_start"].split(".")))
        range_end = range_start + (int(message[nb_switch]) - 1)
        equipement_list = []

        while (equipent_address[3] < range_end):
            equipement_list.append(Equipement(ip: ".".join(map(str, equipent_address))),
                message[constructor], default_login, default_password, default_secret)
            equipent_address[3] += 1

        not_all_started = True

        while (not_all_started):
            not_all_started = False

            for eq in equipement_list:
                if (eq.ready):
                    continue

                ping = os.system("ping -c 4 " + eq.ip)
                if (ping == 0):
                    eq.ready = True

                else:
                    not_all_started = True
                    print(eq.ip + "hasn't started yet")
        print("end stager")
        print(equipement_list)
