import argparse
import sys
import yaml
import os
import re
from datetime import datetime

from instruments.instrument_registry import INSTRUMENT_CLASSES
from instruments.step_dispatcher import execute_step


# ─────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROUTINES_DIR = os.path.join(BASE_DIR, "routines")

DOCS_DIR = os.path.join(BASE_DIR, "docs")
INSTRUMENT_DOCS_DIR = os.path.join(DOCS_DIR, "instruments")
REFERENCE_DOC = os.path.join(BASE_DIR, "README.md")


# ─────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────

class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)
            s.flush()

    def flush(self):
        for s in self.streams:
            s.flush()


def print_file(path):
    try:
        with open(path, "r") as f:
            print(f.read())
    except FileNotFoundError:
        print(f"ERROR: Documentation file not found: {path}")
        sys.exit(1)


def extract_section(content, section_title):
    """Extract a markdown section by title."""
    lines = content.split('\n')
    start = None
    for i, line in enumerate(lines):
        if line.startswith(f'## {section_title}'):
            start = i
            break
    if start is None:
        return f"Section '{section_title}' not found."
    
    section_lines = []
    for line in lines[start:]:
        if line.startswith('## ') and line != f'## {section_title}':
            break
        section_lines.append(line)
    return '\n'.join(section_lines)


def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_path = os.path.join(BASE_DIR, ".env")
    if os.path.isfile(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, _, value = line.partition("=")
                    if key and value:
                        os.environ[key.strip()] = value.strip()


def substitute_env_vars(content):
    """Substitute ${VAR_NAME} with environment variable values."""
    missing_vars = []
    def replace_var(match):
        var_name = match.group(1)
        value = os.environ.get(var_name)
        if value is None:
            missing_vars.append(var_name)
            return match.group(0)  # Keep unsubstituted for now
        return value
    
    # Replace ${VAR_NAME} patterns
    pattern = re.compile(r'\$\{([^}]+)\}')
    result = pattern.sub(replace_var, content)
    
    if missing_vars:
        print(f"ERROR: Missing environment variables: {', '.join(set(missing_vars))}")
        print("Please set these variables or add them to your .env file.")
        sys.exit(1)
    
    return result


def print_help(instrument_name=None):
    """
    --help                -> prints Usage section from README.md
    --help <instrument>   -> prints docs/instruments/<instrument>.md
    """
    if instrument_name is None:
        try:
            with open(REFERENCE_DOC, "r") as f:
                content = f.read()
            usage_section = extract_section(content, "Usage")
            print(usage_section)
        except FileNotFoundError:
            print(f"ERROR: README file not found: {REFERENCE_DOC}")
            sys.exit(1)
        return

    if instrument_name not in INSTRUMENT_CLASSES:
        print(f"ERROR: Unknown instrument '{instrument_name}'")
        print("\nAvailable instruments:")
        for name in INSTRUMENT_CLASSES:
            print(f"  - {name}")
        sys.exit(1)

    doc_path = os.path.join(INSTRUMENT_DOCS_DIR, f"{instrument_name}.md")
    print_file(doc_path)


# ─────────────────────────────────────────────────────────────
# Core logic
# ─────────────────────────────────────────────────────────────

def resolve_yaml_path(yaml_name: str) -> str:
    """
    Resolve a YAML file name to routines/<yaml_name>.
    """
    path = os.path.join(ROUTINES_DIR, yaml_name)

    if not os.path.isfile(path):
        print(f"ERROR: YAML file not found: {path}")
        print("\nAvailable routines:")
        if os.path.isdir(ROUTINES_DIR):
            for f in sorted(os.listdir(ROUTINES_DIR)):
                if f.endswith(".yaml"):
                    print(f"  - {f}")
        sys.exit(1)

    return path


def init_instruments(cfg):
    instruments = {}
    for name, info in cfg["instruments"].items():
        if name == "local":
            continue
        cls = INSTRUMENT_CLASSES[name]
        inst = cls(info["ip"])
        idn = inst.connect()
        print(f"[IDN] {name}: {idn}")
        instruments[name] = inst
    return instruments


def run_test(yaml_name):
    config_path = resolve_yaml_path(yaml_name)

    print(f"Test file: {config_path}")
    print(f"Start time: {datetime.now().isoformat()}")

    try:
        with open(config_path, "r") as f:
            yaml_content = f.read()
        # Substitute environment variables
        yaml_content = substitute_env_vars(yaml_content)
        cfg = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML in {config_path}:\n{e}")
        sys.exit(1)

    instruments = init_instruments(cfg)

    print("\n=== Starting test sequence ===")
    last_result = None

    for i, step in enumerate(cfg["sequence"], start=1):
        try:
            inst = instruments[step["instrument"]]
            print(f"\nStep {i}: {step['action']} on {step['instrument']}")
        except:
            inst= None
        result = execute_step(step, inst, last_result)
        last_result = result

        if result is not None:
            print(f"  Result: {result}")

    print("\n=== Test complete ===")
    print(f"End time: {datetime.now().isoformat()}")

    for inst in instruments.values():
        inst.close()


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────

def main():
    # Load environment variables from .env file if present
    load_env_file()
    
    parser = argparse.ArgumentParser(
        description="Run a lab test from a YAML configuration file.",
        add_help=False,
    )

    parser.add_argument(
        "yaml_file",
        nargs="?",
        help="YAML test file (looked up in routines/)"
    )

    parser.add_argument(
        "--save_log",
        action="store_true",
        help="Save console output to a log file"
    )

    parser.add_argument(
        "--help",
        nargs="?",
        const=True,
        metavar="INSTRUMENT",
        help="Show documentation (optionally for a specific instrument)"
    )

    args = parser.parse_args()

    if args.help is not None:
        print_help(None if args.help is True else args.help)
        return

    if not args.yaml_file:
        print_help()
        return

    if args.save_log:
        os.makedirs("testbench_logs", exist_ok=True)

        yaml_name = os.path.splitext(args.yaml_file)[0]
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_path = os.path.join("testbench_logs", f"{timestamp}-{yaml_name}.log")

        with open(log_path, "w") as log_file:
            original_stdout = sys.stdout
            original_stderr = sys.stderr

            sys.stdout = Tee(sys.stdout, log_file)
            sys.stderr = Tee(sys.stderr, log_file)

            try:
                print(f"[LOG] Saving output to {log_path}")
                run_test(args.yaml_file)
            finally:
                sys.stdout = original_stdout
                sys.stderr = original_stderr

        print(f"[LOG] Test log saved to {log_path}")
    else:
        run_test(args.yaml_file)


if __name__ == "__main__":
    main()
