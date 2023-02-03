import pandas as pd


class Interface:

    def __init__(self, source, destination, dest_id, description=""):
        self.destination_id = dest_id
        self.description = description
        self.source = source
        self.destination = destination
        self.bits_sent = []
        self.bits_received = []
        self.trend_sent_data = []
        self.trend_receive_data = []

    def add_trend_sent_data(self, timestamp, value):
        self.trend_sent_data.append({
            "timestamp": int(timestamp),
            "value": int(float(value))
        })

    def add_trend_receive_data(self, timestamp, value):
        self.trend_receive_data.append({
            "timestamp": int(timestamp),
            "value": int(float(value))
        })

    def get_sent_trend_as_df(self):
        return pd.DataFrame.from_records(self.trend_sent_data).sort_values(by=["timestamp"], ascending=False)

    def get_received_trend_as_df(self):
        return pd.DataFrame.from_records(self.trend_sent_data).sort_values(by=["timestamp"], ascending=False)

    def get_average_bits_sent(self):
        return sum(self.bits_sent) / len(self.bits_sent)

    def get_average_bits_received(self):
        return sum(self.bits_received) / len(self.bits_received)

    def __str__(self):
        return f"Destination: {self.destination}\nDestination ID: {self.destination_id}\nBits Sent: {self.bits_sent}\nBits Received: {self.bits_received}"
