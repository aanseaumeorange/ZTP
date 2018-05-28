class Switch:
    def __init__(self, constructor, model, serial_number, firmware_to, hostname_to, status):
        self.constructor = constructor
        self.serial_number = serial_number
        self.model = model
        self.firmware_to = firmware_to
        self.hostname_to = hostname_to
        self.status = status

    def __str__(self):
        return " Constructeur {0}, \n Modèle : {1},\n Numéro de Série: {2},\n Firmware: {3}".format(self.constructor, self.model, self.serial_number, self.firmware_to)

    def sendMessage(self):
        """ Fonction qui permet d'envoyer un message au serveur relais via RabbitMQ """


class Cisco(Switch):
    def __init__(self, model, serial_number, firmware_to, hostname_to, status):
        self.constructor = "Cisco"
        Switch.__init__(self, self.constructor, model, serial_number, firmware_to, hostname_to, status)

    def change_hostname(self):
        """ Fonction qui permet d'envoyer le message pour changer l'hostname au serveur relais """
        messqge = "192.168.56.69 | switch_objet | byts....."
        message = "192.168.56.69 | update_host"

    def upgrade_firmware(self):
        """ Fonction qui permet d'envoyer le message upgrade de firmware au serveur relais """

    def upgrade_configuration(self):
        """ Fonction qui permet d'envoyer le message upgrade de configuration au serveur relais """
