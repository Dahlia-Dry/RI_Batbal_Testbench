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

### keithley_2450_test

This example demonstrates basic source-measure unit (SMU) operation by performing an I-V sweep on the Keithley 2450. It configures the instrument for voltage sourcing and current measurement, sweeps voltage from 0V to 3.3V in 0.1V steps, and saves the resulting current measurements to a CSV file for analysis.

[Routine File](routines/keithley_2450_test.yaml) | [Results](results/iv_sweep.csv) | [Logs](testbench_logs/)

### keysight_es36312_test

This routine shows how to control a programmable DC power supply. It configures the Keysight E36312 to set specific voltage and current limits, enables the output, measures the actual output values, and then safely disables the output.

[Routine File](routines/keysight_es36312_test.yaml) | [Logs](testbench_logs/)

### multi_inst_test

This example demonstrates coordinated multi-instrument operation. It simultaneously controls a Keithley 2450 SMU for I-V characterization, a Keysight E36312 power supply for device biasing, and a Tektronix MSO58 oscilloscope for waveform monitoring, illustrating the framework's ability to synchronize multiple instruments in a single test sequence.

[Routine File](routines/multi_inst_test.yaml) | [Logs](testbench_logs/)

### ni_vb_test

This example illustrates digital I/O and analog functionality using the NI VirtualBench. It configures digital I/O pins for output, sets analog output voltages, reads back analog input values, and demonstrates basic digital control operations.

[Routine File](routines/ni_vb_test.yaml) | [Logs](testbench_logs/)

### rigol_dg1062z_test

This routine demonstrates function generator control with the Rigol DG1062Z. It starts a waveform output, dynamically changes the output impedance settings, and then stops the waveform, showing how to control signal generation parameters programmatically.

[Routine File](routines/rigol_dg1062z_test.yaml) | [Logs](testbench_logs/)

### script_example

This example demonstrates the framework's scripting capabilities by generating a sine wave with the Rigol function generator, capturing it with the Tektronix oscilloscope, validating the captured waveform data using a custom Python script (validate_waveform.py), and setting a DIO pin on the NI VirtualBench based on the validation result (pass/fail).

[Routine File](routines/script_example.yaml) | [Results](results/wave_capture.csv) | [Logs](testbench_logs/)

### tektronix_mso58_test

This oscilloscope example shows waveform acquisition and analysis. It configures the Tektronix MSO58 with appropriate trigger settings, channel scaling, and measurement parameters, captures waveform data to a CSV file, and takes a screenshot for visual verification.

[Routine File](routines/tektronix_mso58_test.yaml) | [Results](capture.csv) | [Logs](testbench_logs/)

## Architecture

The framework follows a modular architecture designed for extensibility and maintainability in laboratory automation. At its core, it separates concerns between test definition, execution logic, and instrument-specific implementations.

### Step Dispatcher

The `step_dispatcher.py` module is the core execution engine that interprets and runs individual test steps. It serves as the central coordinator that:

- Parses step configurations from YAML routines, validating parameters against the action schema
- Resolves variable substitutions (e.g., `$last` references) to enable dynamic data flow between steps
- Dispatches actions to appropriate instrument methods based on the instrument type and action name
- Handles delays and error conditions gracefully, with comprehensive logging
- Returns results for use in subsequent steps, enabling complex test sequences

The dispatcher uses a type coercion system to ensure parameter compatibility and includes robust error handling to provide clear feedback when tests fail.

### YAML Routines and Action Schema

Test routines are defined in human-readable YAML files stored in the `routines/` directory. Each routine specifies:

- **Instrument connections**: IP addresses or identifiers for each instrument used in the test
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

### Instrument Classes

Instrument-specific functionality is encapsulated in classes inheriting from a common `Instrument` base class in `instruments/`. Each class implements action methods that translate high-level commands into instrument-specific SCPI commands over TCP/IP connections. This abstraction allows the framework to support diverse instruments while maintaining a unified programming interface.

**Note**: All instruments in the framework assume LAN (Ethernet) connectivity using TCP/IP communication. Instruments must be configured for network access and reachable via their specified IP addresses.

The modular design enables researchers to focus on test logic rather than low-level instrument communication details.

### Environment Variables

The framework uses environment variables to securely manage instrument network configuration. This approach keeps sensitive information like IP addresses out of version control while allowing easy sharing of test routines.

**Variable Substitution**: YAML routine files use `${VAR_NAME}` syntax for environment variable substitution. At runtime, these placeholders are replaced with actual values from the environment.

**Automatic Loading**: The framework automatically loads environment variables from a `.env` file in the project root if it exists, eliminating the need for manual `export` commands.

**Required Variables**: The following environment variables must be set for the example routines:
- `KEITHLEY_IP`: IP address of the Keithley 2450 SMU
- `KEYSIGHT_IP`: IP address of the Keysight E36312 power supply  
- `RIGOL_IP`: IP address of the Rigol DG1062Z function generator
- `TEKTRONIX_IP`: IP address of the Tektronix MSO58 oscilloscope
- `NI_VB_IP`: Hostname/IP of the NI VirtualBench

**Setup**: Copy `.env.example` to `.env` and update with your actual instrument addresses. The framework will load these automatically when running tests.

## Customization

### Scripting with $last

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

### Delays

Add timing controls to steps:

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

This approach enables complex test scenarios requiring multiple identical instruments, such as differential measurements, load sharing, or parallel testing.

## Adding New Instruments/Actions

To add support for a new instrument or action:

1. **Create Instrument Class**: In `instruments/`, create a new class inheriting from `Instrument` or appropriate base class.

2. **Implement Methods**: Add methods for each supported action, following the naming convention from the schema.

3. **Define Actions**: Add action definitions to `actions_schema.yaml` with parameters, types, and descriptions.

4. **Add Action Dispatch**: In `step_dispatcher.py`, add an `elif action == "new_action":` block to call the instrument method with parameters.

5. **Test Implementation**: Create a test routine in `routines/` and verify functionality.

6. **Update Documentation**: Run `python generate_docs.py` to regenerate instrument documentation.

## Documentation Generation

The `generate_docs.py` script automatically generates comprehensive documentation:

- Parses `actions_schema.yaml` for action definitions
- Extracts parameter information, types, enums, and descriptions
- Recursively formats complex nested schemas
- Creates individual `.md` files for each instrument in `docs/instruments/`
- Updates the main reference in `docs/reference.md`

Run `python generate_docs.py` after schema changes to keep documentation current.

## Supported Instruments and Actions

### Keysight E36312

The Keysight E36312 is a triple-output programmable DC power supply capable of delivering up to 6V/5A, ±25V/1A, and ±25V/1A. 
It provides stable voltage and current outputs for powering electronic circuits and devices under test.

[Manual](manuals/keysight_e36312.md)

#### psu_configure

Configure baseline PSU channel settings.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | Power supply channel number (1-3) |
| current_limit | float | no | - | Current limit in amperes |
| voltage_limit | float | no | - | Voltage limit in volts |
| output_enabled | bool | no | false | Whether to enable the output after configuration |
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

### Keithley 2450

The Keithley 2450 is a Source Measure Unit (SMU) that combines precision voltage/current sourcing with high-accuracy measurement capabilities. 
It excels in I-V characterization, semiconductor testing, and materials research requiring both sourcing and sensing.

[Manual](manuals/keithley_2450.md)

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
| output_enabled | bool | no | false | Whether to enable output after configuration |

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
| output_enabled | bool | no | true | Whether to enable output after setting |

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
| file | string | Path to saved CSV file (if saved). |

#### smu_reset

Reset the SMU to its default state.

##### Returns

Type: dict

#### smu_zero_output

Set source level to zero and disable output.

##### Returns

Type: dict

### Rigol DG1062Z

The Rigol DG1062Z is a dual-channel function/arbitrary waveform generator with frequencies up to 60 MHz. 
It generates various waveforms including sine, square, ramp, and arbitrary shapes for signal generation and testing.

[Manual](manuals/rigol_dg1062z.md)

#### wavegen_configure

Configure waveform generator output settings.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | Waveform generator channel number |
| impedance | string | no | - | Output load impedance Allowed values: `50ohm`, `highz` |
| enabled | bool | no | - | Enable waveform output |

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

### Tektronix MSO58

The Tektronix MSO58 is a 8-channel mixed signal oscilloscope with 1 GHz bandwidth and 6.25 GS/s sample rate. 
It captures and analyzes analog and digital signals simultaneously, with advanced triggering and measurement capabilities.

[Manual](manuals/tektronix_mso58.pdf)

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
| measurements | dict | Retrieved oscilloscope measurement values. |

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
| file | string | Path to the saved screenshot file. |
| colors | string | Color mode used for the screenshot. |

### NI VirtualBench

The NI VirtualBench is a modular all-in-one instrument that combines oscilloscope, function generator, power supply, and digital I/O capabilities. 
It provides a compact solution for mixed-signal test and measurement applications.

[Manual](manuals/ni_virtualbench.md)

#### vb_psu_configure

Configure VirtualBench PSU channel settings.

##### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | PSU channel number |
| voltage | float | no | - | Voltage setting in volts |
| current_limit | float | no | - | Current limit in amperes |
| output_enabled | bool | no | false |  |

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

