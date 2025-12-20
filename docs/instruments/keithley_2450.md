# keithley_2450

The Keithley 2450 is a Source Measure Unit (SMU) that combines precision voltage/current sourcing with high-accuracy measurement capabilities. 
It excels in I-V characterization, semiconductor testing, and materials research requiring both sourcing and sensing.

Connection via LAN is supported. Example configuration: 
``` yaml
    instruments:
        keithley_2450:
            ip: "<keithley_lan_ip>"
```

[Manual](manuals/keithley-2450.md)

## smu_configure

Configure baseline SMU source and measurement settings.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| source_function | string | yes | - | Source function (voltage or current) Allowed values: `voltage`, `current` |
| source_level | float | yes | - | Source level value |
| compliance_limit | float | yes | - | Compliance limit (A when sourcing voltage, V when sourcing current). |
| measure_function | string | yes | - | Measurement function (voltage or current) Allowed values: `voltage`, `current` |
| sense_mode | string | no | 2w | Sensing mode (2-wire or 4-wire) Allowed values: `2w`, `4w` |
| output_enabled | bool | no | False | Whether to enable output after configuration |

### Returns

Type: dict

Properties:

| Name | Type |
|------|------|
| source_function | string |
| source_level | float |
| compliance_limit | float |
| measure_function | string |
| sense_mode | string |
| output_enabled | bool |

## smu_set_output

Enable or disable SMU output.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| enabled | bool | yes | - | True to enable output, False to disable |

### Returns

Type: dict

Properties:

| Name | Type |
|------|------|
| output_enabled | bool |

## smu_set_source

Convenience action to set SMU source level and compliance.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| source_function | string | yes | - | Source function (voltage or current) Allowed values: `voltage`, `current` |
| level | float | yes | - | Source level value |
| compliance_limit | float | yes | - | Compliance limit value |
| output_enabled | bool | no | True | Whether to enable output after setting |

### Returns

Type: dict

Properties:

| Name | Type |
|------|------|
| source_function | string |
| level | float |
| compliance_limit | float |
| output_enabled | bool |

## smu_measure_voltage

Measure voltage using the SMU.

### Returns

Type: dict

Properties:

| Name | Type |
|------|------|
| voltage | float |

## smu_measure_current

Measure current using the SMU.

### Returns

Type: dict

Properties:

| Name | Type |
|------|------|
| current | float |

## smu_sweep

Perform a stepped source sweep and measure at each step.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| start | float | yes | - | Starting value for the sweep |
| stop | float | yes | - | Ending value for the sweep |
| step | float | yes | - | Step size for the sweep |
| delay | float | no | 0.0 | Delay between steps in seconds |
| save_to | string | no | - | Optional path to save sweep results as CSV |

### Returns

Sweep results.

Type: dict

Properties:

| Name | Type |
|------|------|
| points | list |
| file | string |

## smu_reset

Reset the SMU to its default state.

### Returns

Type: dict

## smu_zero_output

Set source level to zero and disable output.

### Returns

Type: dict

