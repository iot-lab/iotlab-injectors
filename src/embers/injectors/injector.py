import config

import threading
import time

from stats import stats
from datasets import get_dataset


def run(devices, gateway, dataset, protocol, ev_per_hour, duration, stats):
    EventSender.protocol = import_client(protocol)
    data_source = get_dataset(dataset, event_type=gateway["event_type"])
    senders = [ EventSender(gateway, device) for device in devices ]
    _run(senders, data_source, duration, ev_per_hour, stats)


def _run(senders, data_source, duration, ev_per_hour, stats):
    start_time = time.time()
    end_time = start_time + duration * 60
    stats.start_time = start_time
    stats.nb_devices = len(senders)
    while end_time > time.time():
        t1 = time.time()
        send_next_events(senders, data_source)
        t2 = time.time()
        sleep_time = 3600./ev_per_hour - t2 + t1
        if sleep_time < 0:
            stats.time_overflow.append(-sleep_time)
            sleep_time = 0
        stats.nb_loops += 1
        stats.end_time = t2
        time.sleep(sleep_time)


def send_next_events(senders, data_source):
    for i, sender in enumerate(senders):
        event = data_source.get_source(i).next()
        sender.send(event)
    for sender in senders:
        sender.join()


class EventSender:

    def __init__(self, gateway, device):
        assert self.protocol
        broker = config.get_config().broker_address
        self.client = self.protocol(broker)
        self.client.auth = (device["uuid"], device["token"])
        self.gateway = gateway["uuid"]

    def send(self, event):
        def run():
            self.client.publish(self.gateway, event)
        self.thread = threading.Thread(target=run)
        self.thread.start()

    def join(self):
        self.thread.join()


def import_client(protocol):
    return __import__("embers.meshblu." + protocol,
                      fromlist=["Client"]).Client
