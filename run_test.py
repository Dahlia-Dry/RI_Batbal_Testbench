import argparse
import sys
import yaml

from instruments.instrument_registry import *
from instruments.step_dispatcher import execute_step


def init_instruments(cfg):
    instruments = {}
    for name, info in cfg["instruments"].items():
        cls = INSTRUMENT_CLASSES[name]
        inst = cls(info["ip"])
        idn = inst.connect()
        print(f"[IDN] {name}: {idn}")
        instruments[name] = inst
    return instruments


def run_test(config_path):
    try:
        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: Cannot open config file: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML in {config_path}:\n{e}")
        sys.exit(1)

    # initialize instruments
    instruments = init_instruments(cfg)

    print("\n=== Starting test sequence ===")
    for i, step in enumerate(cfg["sequence"]):
        inst = instruments[step["instrument"]]
        print(f"\nStep {i+1}: {step['action']} on {step['instrument']}")
        execute_step(step, inst)

    print("\n=== Test complete ===")

    # close instruments
    for inst in instruments.values():
        inst.close()


def main():
    parser = argparse.ArgumentParser(
        description="Run a lab test from a YAML configuration file."
    )
    parser.add_argument(
        "yaml_file",
        type=str,
        help="Path to the YAML configuration file",
    )

    args = parser.parse_args()
    run_test(args.yaml_file)


if __name__ == "__main__":
    main()
