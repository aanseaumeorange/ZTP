import netmiko


# This class purpose is to handle the connection to any type of equipement
# using the library Netmiko herself based upon Paramiko
# More infos at "https://github.com/ktbyers/netmiko"
# All the error returned by the methods of this class are of type
# EquipementError if you want to catch them specifically
class Equipement(object):
    """docstring for Equipement."""

    hostname = ""
    enable_str = ""
    connection = None

    # Except for IP the other arguments are those by default in the initial
    # config given by the DHCP
    # IP is one of the IP in the range of the DHCP
    def __init__(self, ip=None, device_type=None, username=None, password=None, secret=None):
        self.ip = ip or ""
        self.device_type = device_type or ""
        self.username = username or ""
        self.password = password or ""
        self.secret = secret or ""
        self.ready = False

    # Try to establish an SSH connection, return an error message if not possible
    def ssh_connect(self):

        self.connection = netmiko.ConnectHandler(ip=self.ip,
                                                 device_type=self.device_type,
                                                 username=self.username,
                                                 password=self.password,
                                                 secret=self.secret)

        print ("Connection to: " + self.ip)

    # Close the SSH conneciton if there is one
    def ssh_close(self):
        if (self.connection is None or not self.connection.is_alive()):
            print ("There wasn't any connection to:" + self.ip)
        else:
            self.connection.disconnect()
            print ("Connection is closed: " + self.ip)


    def check_ssh(self):
        return self.connection is not None and self.connection.is_alive()

    # Enter enable mode
    # If no connection or connection has been lost, return an error
    # If already in enable mode do nothing
    def enable_mode(self):
        if (not self.enable_str):
            if ("cisco" in self.device_type):
                self.enable_str = "enable"
            elif ("hp" in self.device_type):
                self.enable_str = "system view"
            else:
                self.enable_str = ""

        if (self.connection is None):
            raise EquipementError("Trying to enter enable mode without being connected to: " + self.ip)

        if (self.connection.check_enable_mode()):
            print(self.ip + " is already in enable mode")
            return

        self.connection.enable(self.enable_str)
        print ("Enable mode for: " + self.ip)

    # Execute a command and return the cli output without the promt by default
    # If there is a problem with the conneciton, return an error whithout
    # executing anything
    def execute(self, line, prompt=False):
        if (self.connection is None or not self.connection.is_alive()):
            raise EquipementError("Trying to execute without having a connection to: " + self.ip)

        result = ""
        if (prompt):
            result += self.connection.find_prompt()
        result += self.connection.send_command(line)

        return result
