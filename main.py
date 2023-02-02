import json

import requests
import configparser
import numpy as np


class Host:

    def __init__(self, name, host_id, description=""):
        self.host_id = host_id
        self.name = name
        self.description = description
        self.interfaces = []
        self.interface_dict = {}

    def __str__(self):

        output = f"#### Name: {self.name} ({self.host_id}) ####\n"

        for i in self.interfaces:
            output += str(i) + "\n"

        return output


class Interface:

    def __init__(self, source, destination, dest_id, description=""):
        self.destination_id = dest_id
        self.description = description
        self.source = source
        self.destination = destination
        self.bits_sent = []
        self.bits_received = []

    def __str__(self):
        return f"Destination: {self.destination}\nDestination ID: {self.destination_id}\nBits Sent: {self.bits_sent}\nBits Received: {self.bits_received}"

    def get_average_bits_sent(self):
        return sum(self.bits_sent) / len(self.bits_sent)

    def get_average_bits_received(self):
        return sum(self.bits_received) / len(self.bits_received)


class Demand:
    def __init__(self):
        np.set_printoptions(suppress=True)
        config = configparser.ConfigParser()
        config.read_file(open(r'config.ini'))

        id_file = open("hosts.json")

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
        self.ITEM_IDS = json.load(id_file)
        self.AUTH_TOKEN = request.json()["result"]
        self.API_URL = config.get("config", "api_url")
        self.hosts = []
        self.hosts_dict = {}

        id_file.close()

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

        for host in self.hosts:
            for interface in host.interfaces:
                demand_matrix[host.host_id, interface.destination_id] = interface.get_average_bits_sent()

        print(demand_matrix)

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
    demand = Demand()
    demand.run()
