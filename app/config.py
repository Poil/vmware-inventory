import yaml

def get_vcenters():
    """ get config """
    with open('config.yaml', 'r') as stream:
        try:
            cfg = yaml.load(stream)
            return cfg.keys()
        except yaml.YAMLError as exc:
            print(exc)
            return False


def get_config(vcenter_name, key):
    """ get config """
    with open('config.yaml', 'r') as stream:
        try:
            cfg = yaml.load(stream)
            return cfg[vcenter_name][key]
        except yaml.YAMLError as exc:
            print(exc)
            return False
