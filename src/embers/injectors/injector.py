import config

import threading
import time


def run(devices, gateway, dataset, protocol, ev_per_hour, duration):
    EventSender.protocol = import_client(protocol)
    data_source = DataSource(dataset)
    devices = reset_devices(devices)
    start_time = time.time()
    end_time = start_time + duration * 60
    while end_time > time.time():
        senders = [ EventSender(gateway, device) for device in devices ]
        send_next_events(senders, data_source)
        time.sleep(3600./ev_per_hour)


def reset_devices(devices):
    api = config.get_broker_api()
    return [ api.reset_token(device["uuid"]) for device in devices ]


def send_next_events(senders, data_source):
    for i, sender in enumerate(senders):
        event = data_source.get_source(i).next()
        sender.send(event)
    for sender in senders:
        sender.join()


class EventSender(threading.Thread):

    def __init__(self, gateway, device):
        super(self.__class__, self).__init__()
        assert self.protocol
        broker = config.get_config().broker_address
        self.client = self.protocol(broker)
        self.client.auth = (device["uuid"], device["token"])
        self.gateway = gateway["uuid"]

    def send(self, event):
        self.event = event
        self.start()

    def run(self):
        self.client.publish(self.gateway, self.event)


class DataSource:

    def __init__(self, dataset):
        pass

    def get_source(self, i):
        class it:
            def next(self): pass

        return it()


def import_client(protocol):
    return __import__("embers.meshblu." + protocol,
                      fromlist=["Client"]).Client
