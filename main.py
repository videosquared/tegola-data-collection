import requests
import configparser


class Host:

    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.interfaces = []


class Interface:

    def __init__(self, name, source, destination, description=""):
        self.name = name
        self.description = description
        self.source = source
        self.destination = destination
        self.bits_sent = []
        self.bits_received = []


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

        self.NUM_VALUES = config.get("credentials", "num_of_values")
        self.AUTH_TOKEN = request.json()["result"]

    def run(self):
        print(self.AUTH_TOKEN)
        self.cleanup()

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
