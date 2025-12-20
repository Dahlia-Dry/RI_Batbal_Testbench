# ni_virtualbench

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

## vb_psu_configure

Configure VirtualBench PSU channel settings.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | PSU channel number |
| voltage | float | no | - | Voltage setting in volts |
| current_limit | float | no | - | Current limit in amperes |
| output_enabled | bool | no | False |  |

### Returns

Type: dict

## vb_psu_set_power

Set PSU voltage and current limit and enable output.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | PSU channel number |
| voltage | float | yes | - | Voltage to set in volts |
| current_limit | float | yes | - | Current limit in amperes |

### Returns

Type: dict

## vb_dio_configure

Configure Digital IO direction.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| lines | list | yes | - | List of digital IO line numbers |
| direction | string | yes | - | Direction for the lines Allowed values: `input`, `output` |

### Returns

Type: dict

## vb_dio_write

Write values to Digital IO lines.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| lines | list | yes | - | List of digital IO line numbers |
| values | list | yes | - | List of values to write (0 or 1) |

### Returns

Type: dict

## vb_dio_read

Read values from Digital IO lines.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| lines | list | yes | - | List of digital IO line numbers |

### Returns

Type: dict

