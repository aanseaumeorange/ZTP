#!/usr/bin/env python
# -*- coding: UTF-8 -*
import telnetlib, sys, time, socket, os, subprocess
from dhcp_service import *

## some variables
line_break = "\r\n"
timeout_for_reply = 1
ios_cli_length = " terminal length 0"
hp_cli_length = "screen-length disbale"
junos_cli_length = " set cli screen-length 0"
iosxr_cli_length = " terminal length 0"
vrp_cli_length = " screen-length 0 temporary"
exclude_start = ("#", "$") #to identify the lines in txt file that starts with these characters
login_phrase = ["sername:", "ogin:"]
password_phrase = ["assword:"]
ztp_phrase = ["\?"]
login = "ztp"
cisco = False
hp = False
huawei = False

dhcp_subnet = "192.168.56.0"
dhcp_subnetmask = "255.255.255.0"
range_start = "192.168.56.10"
range_end = ""
filename = ""
dhcp_folder_path = "/etc/dhcp/dhcpd.conf"
tftp_server_addr = "192.168.56.3"

class TELNET(object):
	"""connect to hosts"""
	def __init__(self):
		self.connections = []
		self.device_names = []
		self.result_dictionary = {}

	def connect (self, router):
		try:
			print (router)
			connection = telnetlib.Telnet(router, 23)
		except IOError:
			print ("IOError, could not open a connection to %s" % router)
			return
		"""send username"""
		#try:
		#	connection.expect(login_phrase)
		#	connection.write(login + line_break)
		#except IOError:
		#	#Send failed
		#	print ("sending username %s failed" % router)
		#	return
		#"""send password"""
		try:
			connection.expect(password_phrase)
			connection.write(login + line_break)
		except IOError:
			#Send failed
			print ("sending username %s failed" % router)
			return
		"""set terminal length and take device name"""
		try :
			if hp:
				time.sleep(timeout_for_reply)
				connection.write(hp_cli_length + line_break)
				device_name = connection.read_until(hp_cli_length).split()[-len(hp_cli_length.split(' '))]
			# elif router[1] == "junos":
			# 	time.sleep(timeout_for_reply)
			# 	connection.write(junos_cli_length + line_break)
			# 	device_name = connection.read_until(">").split()[-1]
			elif huawei:
				time.sleep(timeout_for_reply)
				connection.write(vrp_cli_length + line_break)
				device_name = connection.read_until(vrp_cli_length).split()[-len(vrp_cli_length.split(' '))]
			elif cisco:
				time.sleep(timeout_for_reply)
				connection.write(ios_cli_length + line_break)
				device_name = connection.read_until(ios_cli_length).split()[-len(ios_cli_length.split(' '))]
			else:
				print (router + " is not an appropriate connection type")
				sys.exit(1)
		except IOError:
			#Send failed
			print ("setting terminal length failed")
			return
		self.connections.append(connection)
		self.device_names.append(device_name)

	def get_serial(self, conn):
		if cisco:
			# pipe the serial number displayed in the show version
			version_vendor = "show version | i System serial number\n"
		elif hp:
			# display device manuinfo give some infos on the device and we pipe only the serial number
			version_vendor = "display device manuinfo | include SERIAL"
		elif huawei:
			version_vendor = ""
		else:
			version_vendor = ""
			print("No constructor specified, fix it")

		conn.write(version_vendor)
		conn.write("!!!end version!!!\n")
		system_serial = conn.read_until("!!!end version!!!")
		#Split the
		serial_split = system_serial.split(": ")[1]
		serial = serial_split.split("\r\n")[0]
		return serial

	def privileged_mode(self, conn):
		if cisco:
			privileged = ("enable")
		elif hp:
			privileged =  ("system-view")
		elif huawei:
			privileged =  ("super")
		else:
			privileged =  "enable"

		conn.write("%s%s" % privileged, line_break)
		conn.expect(password_phrase)
		conn.write(login + line_break)

	def install_config(self, conn, serial):
		if (cisco):
			running_config = ("copy tftp://%s/ %s.cfg running-config%s" %
			tftp_server_addr, serial, line_break)
			startup_config = "copy running-config startup-config%s" % line_break
		elif (hp):
			running_config = ("copy running-config tftp %s %s.cfg%s" %
				tftp_server_addr, serial, line_break)
			startup_config = "copy running-config startup-config%s" % line_break
		else:
			running_config = ""
			startup_config = ""

		conn.write(running_config)
		conn.expect(ztp_phrase)
		conn.write(line_break)
		#
		conn.write(startup_config)
		conn.expect(ztp_phrase)
		conn.write(line_break)

	def execute (self, router):
		for conn in self.connections:
			for device in self.device_names:
				conn.write(line_break) #if executing more than one, line break will push device name again and next read_until wont get stuck
				conn.read_until(device)
				#conn.write("%s%s" % privileged_mode(), line_break)
				#conn.expect(password_phrase)
				#conn.write(login + line_break)
				#time.sleep(1)
				privileged_mode(conn)

				serial = self.get_serial(conn)
				print ("Serial number : %s" % serial)
				install_config(conn, ser)
				#conn.write("copy tftp://%s/ %s.cfg running-config%s" %
				#	tftp_server_addr, serial, line_break)
				#conn.expect(ztp_phrase)
				#conn.write(line_break)
				#
				#conn.write("copy running-config startup-config%s" % line_break)
				#conn.expect(ztp_phrase)
				#conn.write(line_break)
				#
				time.sleep(10)
				#catch_end_of_output = [device+" "+line_break, device+line_break]
				#self.result_dictionary[router] = conn.expect(catch_end_of_output)[-1]
	def close(self):
		for conn in self.connections:
			conn.close

# Determine the vendor
vendor = input ("Which constructor?\n 1 - Cisco\n 2 - HP\n 3 - Huawei\n")
if (vendor == 1):
	cisco = True
	filename = "cisco.cfg"
if (vendor == 2):
	hp = True
	filename = "hp.cfg"
if (vendor == 3):
	huawei == True
	filename = "huawei.cfg"

# Determine number of equipment and the IP range
total_connections = input("How many equipment?\n")
end = 10 + 	int(total_connections)
if (end < 255):
	range_end = "192.168.56." + str(end)
else:
	print("Too much equipment")
	sys.exit(1)

# Create the dhcp class with the infos we want
# dhcp_service(path, subnet, netmask, range_start=, range_end, tftp, bootfile)
dhcp = dhcp_service(dhcp_folder_path, dhcp_subnet, dhcp_subnetmask,
					range_start, range_end, tftp_server_addr,
					filename)
dhcp.creat_conf_file()
dhcp.restart_server()

##connect, execute command and print
for x in range(0, int(total_connections)):
	telnet = TELNET()
	telnet.connect("192.168.56." + str(10 + x))
	telnet.execute("192.168.56." + str(10 + x))
	#result= telnet.result_dictionary["192.168.56." + str(10 + x)].split("\r\n")
	#for lines in result:
	#	print (lines)
	telnet.close
