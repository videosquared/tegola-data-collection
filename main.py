from Host import Host
from Interface import Interface
import configparser
import json
import numpy as np
import requests


def main():
    demand = Demand()
    demand.run()


class Demand:
    def __init__(self):
        np.set_printoptions(suppress=True)
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

        request = requests.post(config.get("config", "api_url"), json=data)

        self.NUM_VALUES = config.get("config", "num_of_values")
        self.ITEM_IDS = json.load(open(r"hosts.json"))
        self.AUTH_TOKEN = request.json()["result"]
        self.API_URL = config.get("config", "api_url")
        self.hosts = []
        self.hosts_dict = {}

    def run(self):
        self.get_data()

        for host in self.hosts:
            print(host)

        self.generate_demand_matrix()

        self.cleanup()

    def get_data(self):
        for origin in self.ITEM_IDS:
            host = Host(origin, self.ITEM_IDS.get(origin).get("id"))

            for destination in self.ITEM_IDS.get(origin):
                if destination == "id":
                    continue

                interface = Interface(origin, destination, self.ITEM_IDS.get(origin).get(destination).get("id"))
                sent_request = requests.post(self.API_URL, json=self.create_json(
                    self.ITEM_IDS.get(origin).get(destination).get("sent")))
                received_request = requests.post(self.API_URL, json=self.create_json(
                    self.ITEM_IDS.get(origin).get(destination).get("received")))

                sent_json = sent_request.json()
                received_json = received_request.json()

                print(sent_json)

                for sent_value, received_value in zip(sent_json["result"], received_json["result"]):
                    interface.bits_sent.append(int(sent_value["value"]))
                    interface.bits_received.append(int(received_value["value"]))

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

    # IDs are as follows:
    # SSH: 0
    # COR: 1
    # SMO: 2
    # MHI: 3
    def generate_demand_matrix(self):
        demand_matrix = np.zeros(shape=(len(self.hosts_dict), len(self.hosts_dict)))
        interface_matrix = [["", ""], ["", ""]]

        for host in self.hosts:
            for interface in host.interfaces:
                if interface.destination_id != 1:
                    demand_matrix[interface.destination_id-2, host.host_id] = interface.get_average_bits_sent()
                    interface_matrix[interface.destination_id-2][host.host_id] = f"{host.name} -> {interface.destination}"

        print(demand_matrix)
        print(interface_matrix)

    def cleanup(self):
        data = {
            "jsonrpc": "2.0",
            "method": "user.logout",
            "params": [],
            "id": 1,
            "auth": self.AUTH_TOKEN
        }

        req = requests.post(self.API_URL, json=data)
        print(f"Logout: {req.json()['result']}")


if __name__ == "__main__":
    main()
