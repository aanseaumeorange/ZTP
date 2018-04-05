
#!/usr/bin/env python
# -*- coding: UTF-8 -*

# To avoid problem, on a debian open 'sudo visudo' and add
# ALL ALL=(ALL) NOPASSWD: ALL after ALL ALL=(ALL) NOPASSWD: ALL
# It allow anyuser inside the sudo group to run sudo without asking for a
# password, in short we bypass the problem we have while calling sudo from
# the script

import subprocess

class dhcp_service(object):
    """Clean dhcp creation and running"""
    def __init__(self, path=None, subnet=None, netmask=None, range_start=None,
                    range_end=None, tftp=None, bootfile=None):
        self.path = path or "/etc/dhcp/dhcpd.conf"
        self.subnet = subnet or ""
        self.netmask = netmask or ""
        self.range_start = range_start or ""
        self.range_end = range_end or ""
        self.tftp = tftp or ""
        self.bootfile = bootfile or ""


    def creat_conf_file(self):
        dhcp = None
        # Check that we have the rights to work on the conf
        try:
            dhcp = open(self.path, "w+")
        except IOError as e:
            print("Error while creating the dhcpd.conf file inside /etc/dhcp/ \n Try running the script whith sudo or su mode")
            print(e)
            return 1

        # Line per line what we want
        dhcp.write("authoritative;\n\n")
        dhcp.write("option ip-tftp-server code 150 = {ip-address};\n\n")

        dhcp.write("subnet " + self.subnet + " netmask " + self.netmask + " {\n")
        dhcp.write("	range " + self.range_start + " " + self.range_end + ";\n")
        dhcp.write("	filename \"" + self.bootfile +  "\";\n")
        dhcp.write("	next-server " + self.tftp + ";\n")
        dhcp.write("	option ip-tftp-server " + self.tftp + ";\n")
        dhcp.write("	option bootfile-name \"" + self.bootfile +  "\";\n")

        dhcp.write("	option dhcp-parameter-request-list 67, 150;\n")
        dhcp.write("}\n")
        dhcp.close()

    # For isc-dhcp-server only
    # The command invocked use the service management of a debian
    def restart_server(self):
        path = "/etc/init.d/isc-dhcp-server "
        service_command = ['service', 'isc-dhcp-server']

        restart_command = service_command[:]
        restart_command.append('restart')

        # shell=False to allow call with sudo sudo
        subprocess.call(restart_command, shell=False)

        status_command = service_command[:]
        status_command.append('status')

        print(subprocess.check_output(status_command))

    # For debug purpose
    def print_infos(self):
        print("DHCP conf file: " + self.path)
        print("Subnet " + self.subnet + " " + self.netmask)
        print("Range from " + self.range_start + " to " + self.range_end)
        print("TFTP ip: " + self.tftp)
        print("bootfile on the tftp: " + self.bootfile)

dhcp = dhcp_service("/etc/dhcp/dhcpd.conf", "192.168.56.0", "255.255.255.0",
                    "192.168.56.10", "192.168.56.15", "192.168.56.3", "cisco.cfg")
