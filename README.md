# WattWächter Plus – Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/SmartCircuits-GmbH/WattWaechter_HA_Integration)](https://github.com/SmartCircuits-GmbH/WattWaechter_HA_Integration/releases)

Custom Home Assistant integration for [WattWächter](https://wattwächter.de) smart meter energy monitoring devices by SmartCircuits GmbH.

## Features

- **Auto-discovery** — device is found automatically on your network
- **Smart meter sensors** — energy (kWh), power (W), voltage (V), current (A), frequency (Hz), power factor
- **Per-phase monitoring** — individual readings for L1, L2, L3
- **Diagnostic sensors** — WiFi signal, IP address, firmware version, uptime
- **Firmware updates** — OTA updates directly from Home Assistant with progress bar
- **Dynamic OBIS codes** — unknown meter codes are automatically detected and added
- **Configurable polling** — update interval adjustable from 5 s to 15 min (default: 30 s)

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu (top right) → **Custom repositories**
3. Add `https://github.com/SmartCircuits-GmbH/WattWaechter_HA_Integration` as **Integration**
4. Search for "WattWächter" and install
5. Restart Home Assistant

### Manual

1. Copy the `custom_components/wattwaechter` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

After installation, the WattWächter device should be discovered automatically. If not:

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for "WattWächter"
3. Enter the IP address of your device
4. Optionally provide an API token (if authentication is enabled on the device)

### Options

Under **Settings → Devices & Services → WattWächter Plus → Configure**:

| Option | Default | Range |
|---|---|---|
| Update interval | 30 s | 5–900 s |

## Supported sensors

### Energy & Power

| Sensor | OBIS Code | Unit |
|---|---|---|
| Total consumption | 1.8.0 | kWh |
| Total feed-in | 2.8.0 | kWh |
| Consumption tariff 1/2 | 1.8.1 / 1.8.2 | kWh |
| Feed-in tariff 1/2 | 2.8.1 / 2.8.2 | kWh |
| Active power (total, L1–L3) | 16.7.0, 36/56/76.7.0 | W |

### Voltage, Current & Grid

| Sensor | OBIS Code | Unit |
|---|---|---|
| Voltage L1–L3 | 32/52/72.7.0 | V |
| Current L1–L3 | 31/51/71.7.0 | A |
| Grid frequency | 14.7.0 | Hz |
| Power factor (total, L1–L3) | 13/33/53/73.7.0 | — |

### Diagnostics

WiFi signal strength, SSID, IP address, firmware version, uptime.

## MQTT conflict detection

If your WattWächter device is already integrated via MQTT auto-discovery, this integration will detect the conflict and ask you to choose one method. Both cannot run simultaneously for the same device.

## Links

- [WattWächter Website](https://wattwächter.de)
- [Documentation](https://docs.wattwächter.de)
- [Report an issue](https://github.com/SmartCircuits-GmbH/WattWaechter_HA_Integration/issues)
