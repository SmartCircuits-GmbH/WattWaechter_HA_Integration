---
title: WattWächter Plus
description: Instructions on how to integrate WattWächter Plus smart meter readers with Home Assistant.
ha_category:
  - Energy
ha_release: "2025.x"
ha_iot_class: Local Polling
ha_config_flow: true
ha_codeowners:
  - "@simono41"
ha_domain: wattwaechter
ha_zeroconf: true
ha_platforms:
  - sensor
  - update
ha_integration_type: device
---

The **WattWächter Plus** integration allows you to monitor your electricity smart meter data in Home Assistant using a [WattWächter Plus](https://wattwächter.de) device by SmartCircuits GmbH.

The WattWächter Plus is an ESP-based smart meter reader that connects to your electricity meter's infrared interface and provides real-time energy data over your local network.

{% include integrations/config_flow.md %}

## Prerequisites

- A WattWächter Plus device connected to your smart meter and your local network
- The device must be reachable via its IP address from your Home Assistant instance
- If authentication is enabled on the device, you need a valid API token

## Supported devices

- WattWächter Plus (WW-Plus)

The integration supports all smart meters that are compatible with the WattWächter Plus hardware, including meters using the SML and OBIS protocol.

## Sensors

The integration creates sensors dynamically based on the OBIS codes reported by your smart meter. Common sensors include:

### Energy

| Sensor | OBIS Code | Unit |
|--------|-----------|------|
| Total consumption | 1.8.0 | kWh |
| Total feed-in | 2.8.0 | kWh |
| Consumption tariff 1 | 1.8.1 | kWh |
| Consumption tariff 2 | 1.8.2 | kWh |
| Feed-in tariff 1 | 2.8.1 | kWh |
| Feed-in tariff 2 | 2.8.2 | kWh |

### Power

| Sensor | OBIS Code | Unit |
|--------|-----------|------|
| Active power (total) | 16.7.0 | W |
| Active power L1 | 36.7.0 | W |
| Active power L2 | 56.7.0 | W |
| Active power L3 | 76.7.0 | W |

### Voltage, Current, Frequency

| Sensor | OBIS Code | Unit |
|--------|-----------|------|
| Voltage L1/L2/L3 | 32.7.0 / 52.7.0 / 72.7.0 | V |
| Current L1/L2/L3 | 31.7.0 / 51.7.0 / 71.7.0 | A |
| Grid frequency | 14.7.0 | Hz |
| Power factor | 13.7.0 | - |

Additional OBIS codes reported by your meter are automatically created as generic sensors.

### Diagnostic sensors

| Sensor | Description |
|--------|-------------|
| WiFi signal | WiFi signal strength (dBm) |
| WiFi SSID | Connected WiFi network name |
| IP address | Device IP address |
| Firmware version | Current firmware version |
| Uptime | Device uptime |

## Firmware updates

The integration supports over-the-air (OTA) firmware updates. When a new firmware version is available, it appears as an update entity in Home Assistant. You can install the update directly from the Home Assistant UI.

## Configuration

### Update interval

The default polling interval is 30 seconds. You can change it in the integration options (5 to 900 seconds).

{% include integrations/option_flow.md %}

{% include integrations/config_flow.md %}

| Option | Description | Default |
|--------|-------------|---------|
| Update interval | How often to poll the device for new data (seconds) | 30 |

## Known limitations

- The integration communicates with the device over HTTP on the local network. There is no cloud connection.
- If the device is configured to use MQTT, you should either use MQTT or this integration, not both. The integration detects existing MQTT entities and warns you during setup.
- The available sensors depend on your smart meter model. Not all meters report all OBIS codes.

## Troubleshooting

### Cannot connect to the device

- Verify the device is powered on and connected to your WiFi network
- Check that the IP address is correct (try accessing `http://<device-ip>` in your browser)
- Ensure there are no firewall rules blocking communication between Home Assistant and the device

### Invalid API token

- If you recently changed the token on the device, use the re-authentication flow to update it in Home Assistant
- If you don't need authentication, leave the token field empty during setup

## Removing the integration

{% include integrations/remove_device_service.md %}
