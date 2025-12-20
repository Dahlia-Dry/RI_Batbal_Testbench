# rigol_dg1062z

The Rigol DG1062Z is a dual-channel function/arbitrary waveform generator with frequencies up to 60 MHz. 
It generates various waveforms including sine, square, ramp, and arbitrary shapes for signal generation and testing.

Connection via LAN is supported. Example configuration: 
``` yaml
    instruments:
        rigol_dg1062z:
            ip: "<rigol_lan_ip>"
```

[Manual](manuals/rigol-dg1062z.md)

## wavegen_configure

Configure waveform generator output settings.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | Waveform generator channel number |
| impedance | string | no | - | Output load impedance Allowed values: `50ohm`, `highz` |
| enabled | bool | no | - | Enable or disable waveform output. |

### Returns

Active output configuration.

Type: dict

Properties:

| Name | Type |
|------|------|
| channel | int |
| impedance | string |
| output_enabled | bool |

## wavegen_start_waveform

Configure waveform parameters and start output.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | Waveform generator channel number |
| waveform | dict | yes | - | dict:<br>- type: string<br>allowed: `sine`, `square`, `ramp`<br>- frequency: float<br>- amplitude: float<br>- offset: float |
| output | dict | no | - | Optional output configuration overrides. (dict:<br>- impedance: string<br>allowed: `50ohm`, `highz`<br>- enabled: bool) |

### Returns

Type: dict

Properties:

| Name | Type |
|------|------|
| channel | int |
| waveform | string |
| frequency | float |
| amplitude | float |
| offset | float |
| impedance | string |
| output_enabled | bool |

## wavegen_stop_waveform

Disable waveform output on a channel.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel | int | yes | - | Waveform generator channel number |

### Returns

Type: dict

Properties:

| Name | Type |
|------|------|
| channel | int |
| output_enabled | bool |

