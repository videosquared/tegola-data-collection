import requests
import configparser


class Host:

    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.interfaces = []
        self.interface_dict = {}

    def __str__(self):

        output = f"#### Name: {self.name} ####\n"

        for i in self.interfaces:
            output += str(i) + "\n"

        return output


class Interface:

    def __init__(self, source, destination, description=""):
        self.description = description
        self.source = source
        self.destination = destination
        self.bits_sent = []
        self.bits_received = []

    def __str__(self):
        return f"Destination: {self.destination}\nBits Sent: {self.bits_sent}\nBits Received: {self.bits_received}"


class Demand:
    NUM_VALUES = 1  # Data is collected every 3 minutes
    API_URL = "https://phonebox.tegola.org.uk/api_jsonrpc.php"
    # ITEM_IDS = ["45645",  # SSH -> COR Bits Received
    #             "45813",  # SSH -> COR Bits Sent
    #
    #             "45646",  # SSH -> SMO Bits Received
    #             "45814",  # SSH -> SMO Bits Sent
    #             ####
    #             "47713",  # SMO -> SSH Bits Received
    #             "47857",  # SMO -> SSH Bits Sent
    #
    #             "47712",  # SMO -> COR Bits Received
    #             "47856",  # SMO -> COR Bits Sent
    #             ####
    #             "47065",  # MHI -> COR Bits Received
    #             "47116",  # MHI -> COR Bits Sent
    #             ####
    #             "48766",  # COR -> MHI Bits Received
    #             "48811",  # COR -> MHI Bits Sent
    #
    #             "48769",  # COR -> SSH Bits Received
    #             "48814",  # COR -> SSH Bits Sent
    #
    #             "48767",  # COR -> SMO Bits Received
    #             "48812"   # COR -> SMO Bits Sent
    #             ]

    ITEM_IDS = {
        "ssh": {
            "cor": {
                "sent": "45813",
                "received": "45645"
            },
            "smo": {
                "sent": "45814",
                "received": "45646"
            }
        },
        "smo": {
            "ssh": {
                "sent": "47857",
                "received": "47713"
            },
            "cor": {
                "sent": "47856",
                "received": "47712"
            }
        },
        "mhi": {
            "cor": {
                "sent": "47116",
                "received": "47065"
            }
        },
        "cor": {
            "ssh": {
                "sent": "48814",
                "received": "48769"
            },
            "mhi": {
                "sent": "48811",
                "received": "48766"
            },
            "SMO": {
                "sent": "48812",
                "received": "48767"
            }
        }
    }

    def __init__(self):
        config = configparser.ConfigParser()
        config.read_file(open(r'config.ini'))

        data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": config.get("credentials", "username"),
                "password": config.get("credentials", "password")
            },
            "id": 1,
            "auth": None
        }

        request = requests.post(self.API_URL, json=data)

        self.NUM_VALUES = config.get("config", "num_of_values")
        self.AUTH_TOKEN = request.json()["result"]
        self.hosts = []
        self.hosts_dict = {}

    def run(self):
        self.get_data()

        for host in self.hosts:
            print(host)

        self.cleanup()

    def get_data(self):
        for origin in self.ITEM_IDS:
            host = Host(origin)
            for destination in self.ITEM_IDS.get(origin):
                interface = Interface(origin, destination)
                sent_request = requests.post(self.API_URL, json=self.create_json(
                    self.ITEM_IDS.get(origin).get(destination).get("sent")))
                received_request = requests.post(self.API_URL, json=self.create_json(
                    self.ITEM_IDS.get(origin).get(destination).get("received")))

                sent_json = sent_request.json()
                received_json = received_request.json()

                print(sent_json)

                for sent_value, received_value in zip(sent_json["result"], received_json["result"]):
                    interface.bits_sent.append(sent_value["value"])
                    interface.bits_received.append(received_value["value"])

                host.interfaces.append(interface)
                host.interface_dict[interface.destination] = interface

            self.hosts.append(host)
            self.hosts_dict[host.name] = host

    def create_json(self, item_id):
        data = {
            "jsonrpc": "2.0",
            "method": "history.get",
            "params": {
                "output": "extend",
                "history": 3,
                "itemids": item_id,
                "sortfield": "clock",
                "sortorder": "DESC",
                "limit": self.NUM_VALUES
            },
            "auth": self.AUTH_TOKEN,
            "id": 1
        }

        return data

    def cleanup(self):
        data = {
            "jsonrpc": "2.0",
            "method": "user.logout",
            "params": [],
            "id": 1,
            "auth": self.AUTH_TOKEN
        }

        req = requests.post(self.API_URL, json=data)
        print(req.json()["result"])


if __name__ == "__main__":
    demand = Demand()
    demand.run()
