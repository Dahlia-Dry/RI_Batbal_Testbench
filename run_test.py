import argparse
import sys
import yaml

from instruments.instrument_registry import *
from instruments.step_dispatcher import execute_step


import argparse
import yaml


def load_schema():
    with open("actions_schema.yaml", "r") as f:
        return yaml.safe_load(f)


def print_action_help():
    schema = load_schema()
    print("\nAvailable actions:\n")

    for action, data in schema["actions"].items():
        print(f"{action}")
        print(f"  {data.get('description','')}")
        print(f"  Instruments: {', '.join(data['instruments'])}")

        print("  Parameters:")
        for param, info in data["parameters"].items():
            req = "required" if info.get("required", False) else "optional"
            t = info.get("type", "unknown")
            default = info.get("default")
            if default is not None:
                print(f"    - {param}: {t}, {req}, default={default}")
            else:
                print(f"    - {param}: {t}, {req}")

        print()


def print_instrument_help():
    print("\nSupported actions per instrument:\n")
    for name, cls in INSTRUMENT_CLASSES.items():
        print(f"{name}:")
        actions = getattr(cls, "supported_actions", [])
        if actions:
            for a in actions:
                print(f"  - {a}")
        else:
            print("  (No actions defined)")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Run a lab test from a YAML configuration file."
    )

    parser.add_argument("yaml_file", nargs="?", help="YAML test config")
    parser.add_argument("--help-actions", action="store_true",
                        help="Show available actions and parameters")
    parser.add_argument("--help-instruments", action="store_true",
                        help="Show actions supported by each instrument")

    args = parser.parse_args()

    if args.help_actions:
        print_action_help()
        return

    if args.help_instruments:
        print_instrument_help()
        return

    if not args.yaml_file:
        parser.print_help()
        return

    run_test(args.yaml_file)


if __name__ == "__main__":
    main()
