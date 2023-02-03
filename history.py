from Host import Host
from Interface import Interface
import configparser
import json
import matplotlib.pyplot as plt
import numpy as np
import random
import requests
import time


def main():
    print("Hello World!")
    np.set_printoptions(suppress=True)

    hist = History()
    hist.get_data()
    hist.logout()
    hist.generate_graphs()


class History:
    NUM_DAYS = 20

    MINUTE = 60
    HOUR = 3600
    DAY = 86400

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read_file(open(r"config.ini"))
        self.item_ids = json.load(open(r"hosts.json"))
        self.token = self.get_token()
        self.hosts = []
        self.hosts_dict = {}

    def get_token(self):
        return requests.post(self.config.get("config", "api_url"), json={
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": self.config.get("credentials", "username"),
                "password": self.config.get("credentials", "password")
            },
            "id": 1,
            "auth": None
        }).json()["result"]

    def get_data(self):
        print("Getting data...")
        time_orig = int(time.time())
        # time_orig = 1672531200

        for h in self.item_ids:
            orig = self.item_ids.get(h)
            host = Host(h, orig.get("id"))

            for d in orig:
                if d == "id":
                    continue
                time_ = time_orig

                dest = orig.get(d)
                interface = Interface(h, d, dest.get("id"))

                for i in range(1, self.NUM_DAYS+1):
                    time_from = time_ - self.DAY
                    time_till = time_

                    time_ = time_from - random.randint(1, self.MINUTE)

                    request = requests.post(self.config.get("config", "api_url"), json=self.create_trend_json(
                        dest.get("sent"), time_from, time_till))

                    for result in request.json()["result"]:
                        interface.add_trend_sent_data(result.get("clock"), result.get("value_avg"))

                    request = requests.post(self.config.get("config", "api_url"), json=self.create_trend_json(
                        dest.get("receive"), time_from, time_till))

                    for result in request.json()["result"]:
                        interface.add_trend_receive_data(result.get("clock"), result.get("value_avg"))

                host.add_interface(interface)

            self.add_host(host)

        self.get_whix_data()

        print("Finished getting data.")

    def generate_graphs(self):
        # Traffic received at exit points
        print("Generating graphs")
        print("Generating Line graph")
        f1 = plt.figure(1)
        self.graph_exit_nodes(f1)
        f2 = plt.figure(2)
        self.pie_exit_nodes(f2)
        plt.show()

    def pie_exit_nodes(self, fig):
        ax = fig.add_subplot(111)

        ssh = self.hosts_dict.get("ssh")
        cor = self.hosts_dict.get("cor")
        ssh_smo = ssh.interface_dict.get("smo").get_sent_trend_as_df()
        cor_smo = cor.interface_dict.get("smo").get_sent_trend_as_df()
        cor_mhi = cor.interface_dict.get("mhi").get_sent_trend_as_df()

        smo_val = sum(ssh_smo["value"].values.tolist()) + sum(cor_smo["value"].values.tolist())
        mhi_val = sum(cor_mhi["value"].values.tolist())

        pie_data = np.array([smo_val, mhi_val])
        pie_label = ["smo", "mhi"]

        ax.pie(pie_data, labels=pie_label)


    def graph_exit_nodes(self, fig):
        ax = fig.add_subplot(111)
        ssh = self.hosts_dict.get("ssh")
        cor = self.hosts_dict.get("cor")
        ssh_smo = ssh.interface_dict.get("smo").get_sent_trend_as_df()
        cor_smo = cor.interface_dict.get("smo").get_sent_trend_as_df()
        cor_mhi = cor.interface_dict.get("mhi").get_sent_trend_as_df()

        smo_data = []

        for ssh_smo_val, cor_smo_val in zip(ssh_smo["value"].values.tolist(), cor_smo["value"].values.tolist()):
            smo_data.append(ssh_smo_val + cor_smo_val)

        mhi_data = cor_mhi["value"].values.tolist()
        print("mhi data:")
        print(mhi_data)
        print("smo data:")
        print(smo_data)

        time_data = ssh_smo["timestamp"].values.tolist()

        ax.plot(time_data, mhi_data, label="mhi")
        ax.plot(time_data, smo_data, label="smo")
        ax.legend(loc="upper left")
        # ax.set_ylim(bottom=0)
        # ax.set_xlim(left=0)
        # ax.invert_yaxis()

    def add_host(self, host):
        self.hosts.append(host)
        self.hosts_dict[host.name] = host

    def get_whix_data(self):
        time_orig = int(time.time())

    def create_trend_json(self, i_id, time_from, time_till):
        return {
            "jsonrpc": "2.0",
            "method": "trend.get",
            "params": {
                "time_from": time_from,
                "time_till": time_till,
                "itemids": i_id,
                "sortfield": "clock",
                "sortorder": "DESC",
                "output": [
                    "itemid",
                    "clock",
                    "value_avg"
                ]
            },
            "auth": self.token,
            "id": 1
        }

    def logout(self):
        print(requests.post(self.config.get("config", "api_url"), json={
            "jsonrpc": "2.0",
            "method": "user.logout",
            "params": [],
            "id": 1,
            "auth": self.token
        }).json())


if __name__ == "__main__":
    main()
