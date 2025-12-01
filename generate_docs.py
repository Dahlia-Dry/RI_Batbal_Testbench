import yaml
import os
from instruments.instrument_registry import INSTRUMENT_CLASSES

schema = yaml.safe_load(open("actions_schema.yaml"))

os.makedirs("docs/actions", exist_ok=True)
os.makedirs("docs/instruments", exist_ok=True)


# Generate action docs
for action, data in schema["actions"].items():
    path = f"docs/actions/{action}.md"
    with open(path, "w") as f:
        f.write(f"# {action}\n\n")
        f.write(f"{data['description']}\n\n")

        f.write("## Parameters\n\n")
        f.write("| Name | Type | Required | Default |\n")
        f.write("|------|------|----------|---------|\n")

        for p, info in data["parameters"].items():
            t = info.get("type", "-")
            req = "yes" if info.get("required", False) else "no"
            default = info.get("default", "-")
            f.write(f"| {p} | {t} | {req} | {default} |\n")

    print(f"Generated: {path}")


# Generate instrument docs
for name, cls in INSTRUMENT_CLASSES.items():
    path = f"docs/instruments/{name}.md"
    actions = getattr(cls, "supported_actions", [])

    with open(path, "w") as f:
        f.write(f"# {name}\n\n")
        f.write("## Supported Actions\n\n")
        for a in actions:
            f.write(f"- {a}\n")

    print(f"Generated: {path}")


# Generate overall reference
with open("docs/reference.md", "w") as f:
    f.write("# Test Framework Reference\n\n")
    f.write("## Actions\n")
    for a in schema["actions"]:
        f.write(f"- [{a}](actions/{a}.md)\n")
    f.write("\n## Instruments\n")
    for name in INSTRUMENT_CLASSES:
        f.write(f"- [{name}](instruments/{name}.md)\n")

print("Documentation generation complete.")
