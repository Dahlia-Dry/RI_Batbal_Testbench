# tektronix_mso58

The Tektronix MSO58 is a 8-channel mixed signal oscilloscope with 1 GHz bandwidth and 6.25 GS/s sample rate. 
It captures and analyzes analog and digital signals simultaneously, with advanced triggering and measurement capabilities.

Connection via LAN is supported. Example configuration: 
``` yaml
    instruments:
        tektronix_mso58:
            ip: "<tektronix_lan_ip>"
```

[Manual](manuals/tektronix-mso58.pdf)

## scope_configure

Configure oscilloscope trigger, channels, timebase, and measurements.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| trigger | dict | yes | - | dict:<br>- type: string<br>allowed: `edge`<br>- source: string (Trigger source channel (e.g. CH1).)<br>- level: float (Trigger level in volts.) |
| channels | dict | yes | - | Per-channel configuration keyed by channel name (e.g. CH1). (dict:<br>- scale: float (Vertical scale in volts per division.)<br>- position: float (Vertical position in divisions.)) |
| timebase | dict | no | - | Horizontal timebase configuration. (dict:<br>- scale: float (Time scale in seconds per division.)<br>- position: float (Trigger position in divisions.)) |
| measurements | list | no | - | Automatic oscilloscope measurements. (list of:<br>dict:<br>- type: string<br>allowed: `vpp`, `vmax`, `vmin`, `vtop`, `vbase`, `vamp`, `vrms`, `vmean`, `freq`, `period`, `duty`, `poswidth`, `negwidth`, `rise`, `fall`, `overshoot`, `preshoot` (Measurement type)<br>- source: string (Channel name (e.g. CH1).)) |

### Returns

Active oscilloscope configuration.

Type: dict

Properties:

| Name | Type |
|------|------|
| trigger | dict |
| channels | dict |
| timebase | dict |
| measurements | list |

## scope_capture

Capture waveform from oscilloscope and save to CSV.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channels | list | yes | - | List of channels to capture (e.g. ['CH1', 'CH2']) |
| duration | float | yes | - | Duration of capture in seconds |
| save_to | string | yes | - | Path where the CSV file will be saved |
| show_plot | bool | no | False | Display a simple plot of the captured waveform |

### Returns

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

## scope_screenshot

Save a screenshot of the oscilloscope display.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| save_to | string | yes | - | Path where the screenshot image will be saved. |

### Returns

Screenshot metadata.

Type: dict

Properties:

| Name | Type |
|------|------|
| file | string |
| colors | string |

