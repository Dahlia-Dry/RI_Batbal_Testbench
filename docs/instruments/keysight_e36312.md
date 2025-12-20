# keysight_e36312

The Keysight E36312 is a triple-output programmable DC power supply capable of delivering up to 6V/5A, ±25V/1A, and ±25V/1A. 
It provides stable voltage and current outputs for powering electronic circuits and devices under test.

[Manual](manuals/keysight-e36312.md)

## psu_configure

Configure baseline PSU channel settings.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | Power supply channel number (1-3) |
| current_limit | float | no | - | Current limit in amperes |
| voltage_limit | float | no | - | Voltage limit in volts |
| output_enabled | bool | no | False | Whether to enable the output after configuration |
| sense_mode | string | no | local | Sense mode for measurements Allowed values: `local`, `remote` |

### Returns

Type: dict

## psu_set_power

Convenience action to set voltage and current limit.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | Power supply channel number (1-3) |
| voltage | float | yes | - | Voltage to set in volts |
| current_limit | float | yes | - | Current limit in amperes |
| ramp_time | float | no | 0.0 |  |

### Returns

Type: dict

## psu_ramp_voltage

Ramp PSU voltage to a target value.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | Power supply channel number (1-3) |
| target_voltage | float | yes | - | Target voltage to ramp to in volts |
| ramp_time | float | yes | - | Time to ramp voltage in seconds |

### Returns

Type: dict

## psu_measure_voltage

Measure PSU output voltage.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | Power supply channel number (1-3) |

### Returns

Type: dict

## psu_measure_current

Measure PSU output current.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | Power supply channel number (1-3) |

### Returns

Type: dict

## psu_measure_power

Measure PSU output power.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | Power supply channel number (1-3) |

### Returns

Type: dict

