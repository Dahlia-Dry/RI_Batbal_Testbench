import yaml
import os

# Instrument summaries
INSTRUMENT_SUMMARIES = {
    "keysight_e36312": """
The Keysight E36312 is a triple-output programmable DC power supply capable of delivering up to 6V/5A, ±25V/1A, and ±25V/1A. 
It provides stable voltage and current outputs for powering electronic circuits and devices under test.

Connection via LAN is supported. Example configuration: 
``` rigol_dg1062z:
        ip: "<rigol_lan_ip>"
```

[Manual](manuals/keysight-e36312.md)
""",
    "keithley_2450": """
The Keithley 2450 is a Source Measure Unit (SMU) that combines precision voltage/current sourcing with high-accuracy measurement capabilities. 
It excels in I-V characterization, semiconductor testing, and materials research requiring both sourcing and sensing.

Connection via LAN is supported. Example configuration: 
``` keithley_2450:
        ip: "<keithley_lan_ip>"
```

[Manual](manuals/keithley-2450.md)
""",
    "rigol_dg1062z": """
The Rigol DG1062Z is a dual-channel function/arbitrary waveform generator with frequencies up to 60 MHz. 
It generates various waveforms including sine, square, ramp, and arbitrary shapes for signal generation and testing.

Connection via LAN is supported. Example configuration: 
``` rigol_dg1062z:
        ip: "<rigol_lan_ip>"
```

[Manual](manuals/rigol-dg1062z.md)
""",
    "tektronix_mso58": """
The Tektronix MSO58 is a 8-channel mixed signal oscilloscope with 1 GHz bandwidth and 6.25 GS/s sample rate. 
It captures and analyzes analog and digital signals simultaneously, with advanced triggering and measurement capabilities.

Connection via LAN is supported. Example configuration: 
``` tektronix_mso58:
        ip: "<tektronix_lan_ip>"
```

[Manual](manuals/tektronix-mso58.pdf)
""",
    "ni_virtualbench": """
The NI VirtualBench is a modular all-in-one instrument that combines oscilloscope, function generator, power supply, and digital I/O capabilities. 
It provides a compact solution for mixed-signal test and measurement applications.

Connection via LAN is supported. 
**Note**: The NI VirtualBench is configured using the hostname, not the LAN IP address.
Example configuration: 
``` ni_virtualbench:
        ip: "<ni_virtualbench_hostname>"
```

[Manual](manuals/ni-virtualbench.md)
"""
}

def format_schema(schema):
    """Recursively format a schema dict into a readable HTML string for markdown."""
    if not isinstance(schema, dict):
        return str(schema)
    
    if 'type' in schema:
        t = schema['type']
        if t == 'dict' and 'properties' in schema:
            props = []
            for k, v in schema['properties'].items():
                props.append(f"- {k}: {format_schema(v)}")
            return f"dict:<br>{'<br>'.join(props)}"
        elif t == 'list' and 'items' in schema:
            return f"list of:<br>{format_schema(schema['items'])}"
        else:
            s = t
            if 'enum' in schema:
                enum_vals = schema['enum']
                enum_str = ', '.join(f'`{v}`' for v in enum_vals)
                s += f"<br>allowed: {enum_str}"
            if 'description' in schema:
                s += f" ({schema['description']})"
            return s
    return str(schema)

# Load schema
with open("actions_schema.yaml") as f:
    schema = yaml.safe_load(f)

# Create docs directory
os.makedirs("docs/instruments", exist_ok=True)

actions_schema = schema.get("actions", {})

# Build supported actions per instrument from schema
supported_actions_per_instrument = {}
for action_name, action_data in actions_schema.items():
    instrument = action_data.get("instrument")
    if instrument:
        supported_actions_per_instrument.setdefault(instrument, []).append(action_name)

# Generate instrument docs with embedded actions
readme_sections = []
for instrument_name in supported_actions_per_instrument.keys():
    if instrument_name == "local":
        continue
    
    # Generate individual instrument doc
    path = f"docs/instruments/{instrument_name}.md"
    supported_actions = supported_actions_per_instrument.get(instrument_name, [])

    instrument_content = f"### {instrument_name}\n\n"
    
    # Add instrument summary
    summary = INSTRUMENT_SUMMARIES.get(instrument_name, "")
    if summary:
        instrument_content += summary.strip() + "\n\n"

    if not supported_actions:
        instrument_content += "_No supported actions defined._\n\n"
    else:
        for action in supported_actions:
            action_data = actions_schema.get(action)

            if not action_data:
                instrument_content += f"#### {action}\n\n"
                instrument_content += "! Action not found in schema._\n\n"
                continue

            instrument_content += f"#### {action}\n\n"
            instrument_content += f"{action_data.get('description', '')}\n\n"

            parameters = action_data.get("parameters", {})
            if parameters:
                instrument_content += "##### Parameters\n\n"
                instrument_content += "| Name | Type | Required | Default | Description |\n"
                instrument_content += "|------|------|----------|---------|-------------|\n"

                for param_name, info in parameters.items():
                    param_type = info.get("type", "-")
                    required = "yes" if info.get("required", False) else "no"
                    default = info.get("default", "-")
                    description = info.get("description", "")
                    
                    # Add enum info
                    enum_values = info.get("enum", [])
                    if enum_values:
                        enum_str = f"Allowed values: {', '.join(f'`{v}`' for v in enum_values)}"
                        if description:
                            description += f" {enum_str}"
                        else:
                            description = enum_str
                    
                    # Add nested schema info
                    if 'properties' in info or 'items' in info:
                        schema_str = format_schema(info)
                        if description:
                            description += f" ({schema_str})"
                        else:
                            description = schema_str
                    
                    instrument_content += f"| {param_name} | {param_type} | {required} | {default} | {description} |\n"

                instrument_content += "\n"

            returns = action_data.get("returns", {})
            if returns:
                instrument_content += "##### Returns\n\n"
                ret_type = returns.get("type", "-")
                ret_desc = returns.get("description", "")
                if ret_desc:
                    instrument_content += f"{ret_desc}\n\n"
                instrument_content += f"Type: {ret_type}\n\n"
                properties = returns.get("properties", {})
                if properties:
                    instrument_content += "Properties:\n\n"
                    instrument_content += "| Name | Type |\n"
                    instrument_content += "|------|------|\n"
                    for prop_name, prop_info in properties.items():
                        prop_type = prop_info.get("type", "-")
                        instrument_content += f"| {prop_name} | {prop_type} |\n"
                    instrument_content += "\n"

    readme_sections.append(instrument_content)

    # Write individual instrument file
    with open(path, "w") as f:
        f.write(f"# {instrument_name}\n\n")
        
        # Add instrument summary
        summary = INSTRUMENT_SUMMARIES.get(instrument_name, "")
        if summary:
            f.write(summary.strip() + "\n\n")

        if not supported_actions:
            f.write("_No supported actions defined._\n")
            continue

        for action in supported_actions:
            action_data = actions_schema.get(action)

            if not action_data:
                f.write(f"## {action}\n\n")
                f.write("! Action not found in schema._\n\n")
                continue

            f.write(f"## {action}\n\n")
            f.write(f"{action_data.get('description', '')}\n\n")

            parameters = action_data.get("parameters", {})
            if parameters:
                f.write("### Parameters\n\n")
                f.write("| Name | Type | Required | Default | Description |\n")
                f.write("|------|------|----------|---------|-------------|\n")

                for param_name, info in parameters.items():
                    param_type = info.get("type", "-")
                    required = "yes" if info.get("required", False) else "no"
                    default = info.get("default", "-")
                    description = info.get("description", "")
                    
                    # Add enum info
                    enum_values = info.get("enum", [])
                    if enum_values:
                        enum_str = f"Allowed values: {', '.join(f'`{v}`' for v in enum_values)}"
                        if description:
                            description += f" {enum_str}"
                        else:
                            description = enum_str
                    
                    # Add nested schema info
                    if 'properties' in info or 'items' in info:
                        schema_str = format_schema(info)
                        if description:
                            description += f" ({schema_str})"
                        else:
                            description = schema_str
                    
                    f.write(
                        f"| {param_name} | {param_type} | {required} | {default} | {description} |\n"
                    )

                f.write("\n")

            returns = action_data.get("returns", {})
            if returns:
                f.write("### Returns\n\n")
                ret_type = returns.get("type", "-")
                ret_desc = returns.get("description", "")
                if ret_desc:
                    f.write(f"{ret_desc}\n\n")
                f.write(f"Type: {ret_type}\n\n")
                properties = returns.get("properties", {})
                if properties:
                    f.write("Properties:\n\n")
                    f.write("| Name | Type |\n")
                    f.write("|------|------|\n")
                    for prop_name, prop_info in properties.items():
                        prop_type = prop_info.get("type", "-")
                        f.write(f"| {prop_name} | {prop_type} |\n")
                    f.write("\n")

    print(f"Generated: {path}")

# Update README.md with the Supported Instruments section
readme_content = "## Supported Instruments and Actions\n\n" + "\n".join(readme_sections)

# Read current README
with open("README.md", "r") as f:
    full_readme = f.read()

# Find and replace the Supported Instruments section
start_marker = "## Supported Instruments and Actions"
end_marker = "\n\n"  # Assuming it ends before the next section or EOF

start_idx = full_readme.find(start_marker)
if start_idx != -1:
    # Find the end of this section (next ## or end of file)
    next_section_idx = full_readme.find("\n## ", start_idx + len(start_marker))
    if next_section_idx == -1:
        next_section_idx = len(full_readme)
    
    # Replace the section
    new_readme = full_readme[:start_idx] + readme_content + full_readme[next_section_idx:]
    
    with open("README.md", "w") as f:
        f.write(new_readme)
    
    print("Updated README.md with Supported Instruments section")

print("Documentation generation complete.")

if __name__ == "__main__":
    # This allows the script to be run directly or imported
    pass
