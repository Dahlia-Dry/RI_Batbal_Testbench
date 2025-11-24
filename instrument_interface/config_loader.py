import yaml

def load_config(path="instrument_interface/config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)