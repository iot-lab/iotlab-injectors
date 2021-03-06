import embers.meshblu.http as http

CONFIG_FILE = "config.py"


class config: pass  # namespace


def get_config(force_reload=False):
    if force_reload or not is_loaded():
        load_config_exit_on_fail()
    return config()


def get_broker_api(auth=None):
    config = get_config()
    api = http.Client(config.broker_address)
    api.auth = config.root_auth if auth is None else auth
    return api


def load_config_exit_on_fail():
    try:
        load_config()
    except Exception as e:
        import sys
        print("failed to load {}: {}".format(CONFIG_FILE, e))
        sys.exit(1)


def init_config(broker_address):
    api = http.Client(broker_address)
    reg = api.register_device({"type":"root_auth"})

    root_auth = ( reg['uuid'], reg['token'] )

    conf = "root_auth = {}\nbroker_address = '{}'\n"
    open(CONFIG_FILE, 'w') \
         .write(conf.format(root_auth, broker_address))


def load_config():
    execfile(CONFIG_FILE, config.__dict__)
    assert config.broker_address
    assert config.root_auth
    load_config.config_loaded = True


def is_loaded():
    return hasattr(load_config, "config_loaded")
