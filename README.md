# DTU Research Immersion Fall 2025: Automated Lab Test Bench Framework in Python

A Python-based test automation framework for controlling laboratory instruments in research and testing scenarios.

## Summary

This project provides a modular, YAML-driven test creation framework for automating measurements and control sequences using various laboratory instruments. It supports power supplies, source-measure units, oscilloscopes, waveform generators, and digital I/O devices through a unified action schema and step dispatcher system.

Key features:
- YAML-based test routine configuration
- Extensible instrument support via action schema
- Scripting capabilities with variable substitution
- Automatic documentation generation
- Support for delays and conditional execution

### Current Status
 - Minimum viable product achieved
 - All tests in routines folder passed

### Future Improvement Suggestions:
 - more efficient structure in [step_dispatcher](instruments/step_dispatcher.py): current implementation is clunky, but works. 
 - support for more modules of the NI TestBench: pymeasure proved quite a difficult library to work with. The NI TestBench currently only includes support for Digital IO and PSU, but other modes (MSO, Wave Generator) are also possible.
 - extending scripting support so that access to result variables is not just limited to the last action performed

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd RI_BatBal_TestBench
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install additional instrument drivers as needed.

## Usage

### Running a test routine
Run a test sequence by providing a YAML configuration file:
```bash
python run_test.py <testname>.yaml
```

The YAML file defines the instruments to connect to and the sequence of actions to execute. See the Examples section below for available test routines.

### Saving log file
Add the option `--save_log` to save the console output to a log file as `testbench_logs/<YYYYMMDD-HHMMSS-<testname>.log>`

### Viewing documentation
Use the `--help` option to view documentation directly from the command line:
- Show the overall usage: 
    ```bash
    python run_test.py --help
    ```
- Show documentation for a specific instrument: 
    ```bash
    python run_test.py --help <InstrumentName>
    ```

## Examples

This section provides example test routines demonstrating the framework's capabilities. Each example includes a description and links to execution logs.

### tektronix_mso58_test

This oscilloscope example shows waveform acquisition and analysis. It configures the Tektronix MSO58 with appropriate trigger settings, channel scaling, and measurement parameters for an externally set signal, captures waveform data to a CSV file, and takes a screenshot for visual verification.

[Routine File](routines/tektronix_mso58_test.yaml) | [Results](capture.csv) | [Successful Logfile](testbench_logs/20251218-162323-tektronix_mso58_test.log)

### keithley_2450_test

This example demonstrates basic source-measure unit (SMU) operation by performing an I-V sweep on the Keithley 2450. It configures the instrument for voltage sourcing and current measurement, sweeps voltage from 0V to 3.3V in 0.1V steps, and saves the resulting current measurements to a CSV file for analysis.

[Routine File](routines/keithley_2450_test.yaml) | [Results](results/iv_sweep.csv) | [Successful Logfile](testbench_logs/20251220-104439-keithley_2450_test.log)

### keysight_es36312_test

This routine shows how to control a programmable DC power supply. It configures the Keysight E36312 to set specific voltage and current limits, enables the output, measures the actual output values, and then safely disables the output.

[Routine File](routines/keysight_es36312_test.yaml) | [Successful Logfile](testbench_logs/20251218-124042-keysight_es36312_test.log)

### ni_vb_test

This example illustrates basic digital I/O functionality using the NI VirtualBench. It configures digital I/O pins for output, sets digital output voltages, and reads back the values from each selected pin.

[Routine File](routines/ni_vb_test.yaml) | [Successful Logfile](testbench_logs/20251218-172813-ni_vb_test.log)

### rigol_dg1062z_test

This routine demonstrates function generator control with the Rigol DG1062Z. It starts a waveform output, dynamically changes the output impedance settings, and then stops the waveform.

[Routine File](routines/rigol_dg1062z_test.yaml) | [Successful Logfile](testbench_logs/20251218-122837-rigol_dg1062z_test.log)

### multi_inst_test

This example demonstrates multi-instrument operation. It simultaneously controls a Keithley 2450 SMU for I-V characterization, a Keysight E36312 power supply for device biasing, and a Tektronix MSO58 oscilloscope for waveform monitoring.

[Routine File](routines/multi_inst_test.yaml) | [Successful Logfile](testbench_logs/20251218-174253-multi_inst_test.log)

### script_example

This example demonstrates the framework's scripting capabilities by generating a sine wave with the Rigol function generator, capturing it with the Tektronix oscilloscope, validating the captured waveform data using a custom Python script, and setting a DIO pin on the NI VirtualBench based on the validation result (pass/fail).

[Routine File](routines/script_example.yaml) | [Python Script](scripts/validate_waveform.py) | [Results](results/wave_capture.csv) | [Successful Logfile](testbench_logs/20251218-174048-script_example.log)

## Architecture

The framework follows a modular architecture with the intent of enabling maximum ease of use while also allowing for extensibility and maintainability. It attempts to clearly separate test definition, execution logic, and instrument-specific implementations such that it is straightforward to modify and extend for future users.

### Top Level: YAML Routines and Action Schema

Test routines are defined in human-readable `.yaml` files stored in the `routines/` directory. A template routine `.yaml` file can be found [here](routines/template.yaml).Each routine specifies: 

- **Description**: (optional) summary of the test actions
- **Instrument connections**: IP addresses or identifiers for each instrument used in the test. An example instrument connection section is as follows:
    ```yaml
        instruments:
            rigol_dg1062z:
                ip: "${RIGOL_IP}"

            tektronix_mso58:
                ip: "${TEKTRONIX_IP}"

            ni_virtualbench:
                ip: "${NI_VB_HOSTNAME}"

    ```
- **Sequence of steps**: Each step contains:
  - `action`: The specific operation to perform (drawn from the centralized action schema)
  - `instrument`: Which configured instrument instance to target
  - Action-specific parameters with automatic type validation
  - Optional timing controls (`delay_before`/`delay_after`) for precise sequencing

The `actions_schema.yaml` file serves as the single source of truth for all supported actions. It defines action parameters with types, defaults, enums, and descriptions, enabling:

- Automatic parameter validation and type coercion
- Schema-driven documentation generation
- Consistent action interfaces across instruments
- Easy addition of new actions without code changes

### YAML Parser and Step Dispatcher

The main execution script [run_test.py](run_test.py) serves as a tool for executing the instructions in a `.yaml` test file via the command line. It is kept as lean as possible with only a few command line arguments detailed in the Usage section above, allowing for most of the customization to be done within the more human-readable `.yaml` files.

The [step_dispatcher](instruments/step_dispatcher.py) module is the core execution engine that interprets and runs individual test steps. It serves as the central coordinator that:

- Parses step configurations from YAML routines, validating parameters against the action schema
- Resolves variable substitutions (e.g., `$last` references) to enable dynamic data flow between steps
- Dispatches actions to appropriate instrument methods based on the instrument type and action name
- Handles delays and error conditions with comprehensive logging
- Returns results for use in subsequent steps, enabling complex test sequences

The dispatcher uses a type coercion system to ensure parameter compatibility and includes robust error handling to provide clear feedback when tests fail.

### Instrument Classes

Instrument-specific functionality is encapsulated in classes inheriting from a common `Instrument` base class in `instruments/`. Each class implements action methods that translate high-level commands into instrument-specific SCPI commands over TCP/IP connections. This abstraction allows the framework to support diverse instruments while maintaining a unified programming interface.

**Note**: All instruments in the framework assume LAN (Ethernet) connectivity using TCP/IP communication. Instruments must be configured for network access and reachable via their specified IP addresses.

All methods within the instrument classes that map to an action in the [action schema](actions_schema.yaml) return a dictionary containing any relevant result information. This is useful both for logging purposes and to provide the possibility for using results from one step later in the test sequence.

### Environment Variables

The framework uses environment variables to securely manage instrument network configuration. 

**Variable Substitution**: YAML routine files use `${VAR_NAME}` syntax for environment variable substitution. At runtime, these placeholders are replaced with actual values from the environment.

**Automatic Loading**: The framework automatically loads environment variables from a `.env` file in the project root if it exists, eliminating the need for manual `export` commands.

**Required Variables**: The following environment variables must be set for the example routines:
- `KEITHLEY_IP`: IP address of the Keithley 2450 SMU
- `KEYSIGHT_IP`: IP address of the Keysight E36312 power supply  
- `RIGOL_IP`: IP address of the Rigol DG1062Z function generator
- `TEKTRONIX_IP`: IP address of the Tektronix MSO58 oscilloscope
- `NI_VB_HOSTNAME`: Hostname of the NI VirtualBench

**Setup**: Copy `.env.example` to `.env` and update with your actual instrument addresses. The framework will load these automatically when running tests.

## Customization

### Using previous results in subsequent actions

Steps can reference results from previous steps using `$last` syntax:

- `$last`: Use the entire previous result
- `$last.field`: Access a specific field from the previous result
- `$last[index]`: Access array elements

Example:
```yaml
sequence:
  - action: psu_measure_voltage
    instrument: keysight_e36312
    channel: 1
  - action: scope_configure
    instrument: tektronix_mso58
    trigger:
      level: $last.voltage  # Use measured voltage as trigger level
```

### Scripting

To further boost customizability, support exists for a python script to be inserted and run in the middle of a test sequence. The implementation of this functionality can be found in the [step_dispatcher](instruments/step_dispatcher.py) module, and a python script template can be found [here](scripts/script_template.py). The script gets `input_data` as a global variable containing the result output dictionary from the previous action step, and must define a dict `OUTPUT` containing the results to be accessed by the next action step. 

**Note**: If running a script inside a `.yaml` routine, `local` must be added to the `instruments` list as shown in the following example such that it will be properly read by the step dispatcher:
```yaml
    description: Measure a signal, compute a trigger level in a script, and reuse it.

    instruments:
        tektronix_mso58:
            ip: "${TEKTRONIX_IP}"

        local:
            ip: "localhost"

    sequence:
        - action: scope_configure
            instrument: tektronix_mso58
            trigger:
            type: edge
            source: CH1
            level: 0.0
            channels:
            CH1:
                scale: 0.5
                position: 0
            measurements:
            - type: vmax
                source: CH1

        - action: scope_capture
            instrument: tektronix_mso58
            channels: [CH1]
            duration: 0.01
            save_to: results/capture.csv

        # Script computes a new value from the measurement
        - action: run_script
            instrument: local
            script: scripts/compute_trigger_level.py

        # Script output is reused here
        - action: scope_configure
            instrument: tektronix_mso58
            trigger:
            type: edge
            source: CH1
            level: "$last.trigger_level"
            channels:
            CH1:
                scale: 0.5
                position: 0
```
A simple python script `compute_trigger_level.py` could then look like the following:
```python
    # Provided automatically by step dispatcher
    data = input_data

    vmax = data["measurements"]["vmax"]

    # Compute a new trigger level (50% of peak)
    trigger_level = vmax / 2.0

    print(f"Computed trigger level: {trigger_level:.3f} V")

    OUTPUT = {
        "trigger_level": trigger_level
    }
```
An additional example with scripting can be found [here](routines/script_example.yaml).

### Delays

Timing control can also be added to action steps using either `delay_before` or `delay_after`. For example:

```yaml
sequence:
  - action: psu_set_power
    instrument: keysight_e36312
    voltage: 3.3
    current_limit: 1.0
    delay_after: 2.0  # Wait 2 seconds after setting power
  - action: smu_sweep
    instrument: keithley_2450
    delay_before: 1.0  # Wait 1 second before starting sweep
```

### Multiple Instrument Instances

The framework supports using multiple instances of the same instrument type by defining them with different names in the YAML configuration. Each instance requires its own IP address and can be controlled independently.

Example configuration with two Keithley 2450 SMUs:
```yaml
description: Test with two Keithley 2450 SMUs for differential measurements

instruments:
  keithley_2450_primary:
    ip: "${KEITHLEY_IP_1}"
  keithley_2450_secondary:
    ip: "${KEITHLEY_IP_2}"

sequence:
  # Configure both SMUs
  - action: smu_configure
    instrument: keithley_2450_primary
    source_function: voltage
    source_level: 0.0
    compliance_limit: 0.1
    measure_function: current
    output_enabled: true

  - action: smu_configure
    instrument: keithley_2450_secondary
    source_function: voltage
    source_level: 0.0
    compliance_limit: 0.1
    measure_function: current
    output_enabled: true

  # Perform coordinated sweep
  - action: smu_set_source
    instrument: keithley_2450_primary
    level: 1.0

  - action: smu_measure_current
    instrument: keithley_2450_primary

  - action: smu_set_source
    instrument: keithley_2450_secondary
    level: -1.0  # Opposite polarity

  - action: smu_measure_current
    instrument: keithley_2450_secondary
```

**Environment Variables**: Set separate environment variables for each instrument instance:
```bash
KEITHLEY_IP_1=<keithley.ip.1>
KEITHLEY_IP_2=<keithley.ip.2>
```

This approach enables complex test scenarios requiring multiple identical instruments.

## Adding New Instruments/Actions

To add support for a new instrument or action:

1. **Create Instrument Class**: In `instruments/`, create a new class inheriting from `Instrument` or appropriate base class.

2. **Implement Methods**: Add methods for each supported action. For clarity, it is recommended to follow the naming convention from the schema: <inst>_<action>

3. **Update Registry**: Add the new class to `INSTRUMENT_CLASSES` in `instrument_registry.py`.

4. **Define Actions**: Add action definitions to `actions_schema.yaml` with parameters, types, and descriptions.

5. **Add Action Dispatch**: In `step_dispatcher.py`, add an `elif action == "new_action":` block to call the instrument method with parameters.

6. **Test Implementation**: Create a test routine in `routines/` and verify functionality.

7. **Update Documentation**: Run `python generate_docs.py` to regenerate instrument documentation.

## Documentation Generation

The `generate_docs.py` script automatically generates and updates documentation:

- Parses `actions_schema.yaml` for action definitions
- Extracts parameter information, types, enums, and descriptions
- Recursively formats complex nested schemas
- Creates individual `.md` files for each instrument in `docs/instruments/`
- Updates the main reference in `docs/reference.md`

Run `python generate_docs.py` after schema changes to keep documentation current.

## Supported Instruments and Actions

### keysight_e36312

The Keysight E36312 is a triple-output programmable DC power supply capable of delivering up to 6V/5A, ±25V/1A, and ±25V/1A. 
It provides stable voltage and current outputs for powering electronic circuits and devices under test.

Connection via LAN is supported. Example configuration: 
``` yaml
    instruments:
        rigol_dg1062z:
            ip: "<rigol_lan_ip>"
```

[Manual](manuals/keysight-e36312.md)

#### psu_configure

Configure baseline PSU channel settings.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | Power supply channel number (1-3) |
| current_limit | float | no | - | Current limit in amperes |
| voltage_limit | float | no | - | Voltage limit in volts |
| output_enabled | bool | no | False | Whether to enable the output after configuration |
| sense_mode | string | no | local | Sense mode for measurements Allowed values: `local`, `remote` |

##### Returns

Type: dict

#### psu_set_power

Convenience action to set voltage and current limit.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | Power supply channel number (1-3) |
| voltage | float | yes | - | Voltage to set in volts |
| current_limit | float | yes | - | Current limit in amperes |
| ramp_time | float | no | 0.0 |  |

##### Returns

Type: dict

#### psu_ramp_voltage

Ramp PSU voltage to a target value.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | Power supply channel number (1-3) |
| target_voltage | float | yes | - | Target voltage to ramp to in volts |
| ramp_time | float | yes | - | Time to ramp voltage in seconds |

##### Returns

Type: dict

#### psu_measure_voltage

Measure PSU output voltage.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | Power supply channel number (1-3) |

##### Returns

Type: dict

#### psu_measure_current

Measure PSU output current.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | Power supply channel number (1-3) |

##### Returns

Type: dict

#### psu_measure_power

Measure PSU output power.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | Power supply channel number (1-3) |

##### Returns

Type: dict


### keithley_2450

The Keithley 2450 is a Source Measure Unit (SMU) that combines precision voltage/current sourcing with high-accuracy measurement capabilities. 
It excels in I-V characterization, semiconductor testing, and materials research requiring both sourcing and sensing.

Connection via LAN is supported. Example configuration: 
``` yaml
    instruments:
        keithley_2450:
            ip: "<keithley_lan_ip>"
```

[Manual](manuals/keithley-2450.md)

#### smu_configure

Configure baseline SMU source and measurement settings.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| source_function | string | yes | - | Source function (voltage or current) Allowed values: `voltage`, `current` |
| source_level | float | yes | - | Source level value |
| compliance_limit | float | yes | - | Compliance limit (A when sourcing voltage, V when sourcing current). |
| measure_function | string | yes | - | Measurement function (voltage or current) Allowed values: `voltage`, `current` |
| sense_mode | string | no | 2w | Sensing mode (2-wire or 4-wire) Allowed values: `2w`, `4w` |
| output_enabled | bool | no | False | Whether to enable output after configuration |

##### Returns

Active SMU configuration.

Type: dict

#### smu_set_output

Enable or disable SMU output.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| enabled | bool | yes | - | True to enable output, False to disable |

##### Returns

Type: dict

Properties:

| Name | Type |
|------|------|
| output_enabled | bool |

#### smu_set_source

Convenience action to set SMU source level and compliance.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| source_function | string | yes | - | Source function (voltage or current) Allowed values: `voltage`, `current` |
| level | float | yes | - | Source level value |
| compliance_limit | float | yes | - | Compliance limit value |
| output_enabled | bool | no | True | Whether to enable output after setting |

##### Returns

Type: dict

#### smu_measure_voltage

Measure voltage using the SMU.

##### Returns

Type: dict

Properties:

| Name | Type |
|------|------|
| voltage | float |

#### smu_measure_current

Measure current using the SMU.

##### Returns

Type: dict

Properties:

| Name | Type |
|------|------|
| current | float |

#### smu_sweep

Perform a stepped source sweep and measure at each step.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| start | float | yes | - | Starting value for the sweep |
| stop | float | yes | - | Ending value for the sweep |
| step | float | yes | - | Step size for the sweep |
| delay | float | no | 0.0 | Delay between steps in seconds |
| save_to | string | no | - | Optional path to save sweep results as CSV |

##### Returns

Sweep results.

Type: dict

Properties:

| Name | Type |
|------|------|
| points | list |
| file | string |

#### smu_reset

Reset the SMU to its default state.

##### Returns

Type: dict

#### smu_zero_output

Set source level to zero and disable output.

##### Returns

Type: dict


### rigol_dg1062z

The Rigol DG1062Z is a dual-channel function/arbitrary waveform generator with frequencies up to 60 MHz. 
It generates various waveforms including sine, square, ramp, and arbitrary shapes for signal generation and testing.

Connection via LAN is supported. Example configuration: 
``` yaml
    instruments:
        rigol_dg1062z:
            ip: "<rigol_lan_ip>"
```

[Manual](manuals/rigol-dg1062z.md)

#### wavegen_configure

Configure waveform generator output settings.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | Waveform generator channel number |
| impedance | string | no | - | Output load impedance Allowed values: `50ohm`, `highz` |
| enabled | bool | no | - | Enable or disable waveform output. |

##### Returns

Active output configuration.

Type: dict

Properties:

| Name | Type |
|------|------|
| channel | int |
| impedance | string |
| output_enabled | bool |

#### wavegen_start_waveform

Configure waveform parameters and start output.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | Waveform generator channel number |
| waveform | dict | yes | - | dict:<br>- type: string<br>allowed: `sine`, `square`, `ramp`<br>- frequency: float<br>- amplitude: float<br>- offset: float |
| output | dict | no | - | Optional output configuration overrides. (dict:<br>- impedance: string<br>allowed: `50ohm`, `highz`<br>- enabled: bool) |

##### Returns

Type: dict

#### wavegen_stop_waveform

Disable waveform output on a channel.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | Waveform generator channel number |

##### Returns

Type: dict

Properties:

| Name | Type |
|------|------|
| channel | int |
| output_enabled | bool |


### tektronix_mso58

The Tektronix MSO58 is a 8-channel mixed signal oscilloscope with 1 GHz bandwidth and 6.25 GS/s sample rate. 
It captures and analyzes analog and digital signals simultaneously, with advanced triggering and measurement capabilities.

Connection via LAN is supported. Example configuration: 
``` yaml
    instruments:
        tektronix_mso58:
            ip: "<tektronix_lan_ip>"
```

[Manual](manuals/tektronix-mso58.pdf)

#### scope_configure

Configure oscilloscope trigger, channels, timebase, and measurements.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| trigger | dict | yes | - | dict:<br>- type: string<br>allowed: `edge`<br>- source: string (Trigger source channel (e.g. CH1).)<br>- level: float (Trigger level in volts.) |
| channels | dict | yes | - | Per-channel configuration keyed by channel name (e.g. CH1). (dict:<br>- scale: float (Vertical scale in volts per division.)<br>- position: float (Vertical position in divisions.)) |
| timebase | dict | no | - | Horizontal timebase configuration. (dict:<br>- scale: float (Time scale in seconds per division.)<br>- position: float (Trigger position in divisions.)) |
| measurements | list | no | - | Automatic oscilloscope measurements. (list of:<br>dict:<br>- type: string<br>allowed: `vpp`, `vmax`, `vmin`, `vtop`, `vbase`, `vamp`, `vrms`, `vmean`, `freq`, `period`, `duty`, `poswidth`, `negwidth`, `rise`, `fall`, `overshoot`, `preshoot` (Measurement type)<br>- source: string (Channel name (e.g. CH1).)) |

##### Returns

Active oscilloscope configuration.

Type: dict

Properties:

| Name | Type |
|------|------|
| trigger | dict |
| channels | dict |
| timebase | dict |
| measurements | list |

#### scope_capture

Capture waveform from oscilloscope and save to CSV.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channels | list | yes | - | List of channels to capture (e.g. ['CH1', 'CH2']) |
| duration | float | yes | - | Duration of capture in seconds |
| save_to | string | yes | - | Path where the CSV file will be saved |
| show_plot | bool | no | False | Display a simple plot of the captured waveform |

##### Returns

Capture result metadata.

Type: dict

Properties:

| Name | Type |
|------|------|
| channels | list |
| duration | float |
| file | string |
| num_channels | int |
| samples_per_channel | dict |
| measurements | dict |

#### scope_screenshot

Save a screenshot of the oscilloscope display.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| save_to | string | yes | - | Path where the screenshot image will be saved. |

##### Returns

Screenshot metadata.

Type: dict

Properties:

| Name | Type |
|------|------|
| file | string |
| colors | string |


### ni_virtualbench

The NI VirtualBench is a modular all-in-one instrument that combines oscilloscope, function generator, power supply, and digital I/O capabilities. 
It provides a compact solution for mixed-signal test and measurement applications.

Connection via LAN is supported. 
**Note**: The NI VirtualBench is configured using the hostname, not the LAN IP address.
Example configuration: 
``` yaml
    instruments:
        ni_virtualbench:
            ip: "<ni_virtualbench_hostname>"
```

[Manual](manuals/ni-virtualbench.md)

#### vb_psu_configure

Configure VirtualBench PSU channel settings.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | PSU channel number |
| voltage | float | no | - | Voltage setting in volts |
| current_limit | float | no | - | Current limit in amperes |
| output_enabled | bool | no | False |  |

##### Returns

Type: dict

#### vb_psu_set_power

Set PSU voltage and current limit and enable output.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | PSU channel number |
| voltage | float | yes | - | Voltage to set in volts |
| current_limit | float | yes | - | Current limit in amperes |

##### Returns

Type: dict

#### vb_dio_configure

Configure Digital IO direction.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| lines | list | yes | - | List of digital IO line numbers |
| direction | string | yes | - | Direction for the lines Allowed values: `input`, `output` |

##### Returns

Type: dict

#### vb_dio_write

Write values to Digital IO lines.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| lines | list | yes | - | List of digital IO line numbers |
| values | list | yes | - | List of values to write (0 or 1) |

##### Returns

Type: dict

#### vb_dio_read

Read values from Digital IO lines.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| lines | list | yes | - | List of digital IO line numbers |

##### Returns

Type: dict

