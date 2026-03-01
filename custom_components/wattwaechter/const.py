"""Constants for the WattWächter Plus integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
)

DOMAIN = "wattwaechter"

DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 5
MAX_SCAN_INTERVAL = 120
OTA_CHECK_INTERVAL = 21600  # 6 hours in seconds

CONF_DEVICE_ID = "device_id"
CONF_MODEL = "model"
CONF_MAC = "mac"
CONF_FW_VERSION = "fw_version"

MANUFACTURER = "SmartCircuits GmbH"
DEVICE_NAME = "WattWächter Plus"


# --- OBIS Sensor Descriptions ---


@dataclass(frozen=True, kw_only=True)
class ObisSensorDescription(SensorEntityDescription):
    """Describes a WattWächter OBIS sensor."""


KNOWN_OBIS_CODES: dict[str, ObisSensorDescription] = {
    # Energy meters (kWh) - total_increasing
    "1-0:1.8.0": ObisSensorDescription(
        key="1-0:1.8.0",
        translation_key="import_total",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "1-0:2.8.0": ObisSensorDescription(
        key="1-0:2.8.0",
        translation_key="export_total",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "1-0:1.8.1": ObisSensorDescription(
        key="1-0:1.8.1",
        translation_key="import_tariff_1",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "1-0:1.8.2": ObisSensorDescription(
        key="1-0:1.8.2",
        translation_key="import_tariff_2",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "1-0:2.8.1": ObisSensorDescription(
        key="1-0:2.8.1",
        translation_key="export_tariff_1",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "1-0:2.8.2": ObisSensorDescription(
        key="1-0:2.8.2",
        translation_key="export_tariff_2",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    # Power (W) - measurement
    "1-0:16.7.0": ObisSensorDescription(
        key="1-0:16.7.0",
        translation_key="active_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "1-0:36.7.0": ObisSensorDescription(
        key="1-0:36.7.0",
        translation_key="active_power_l1",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "1-0:56.7.0": ObisSensorDescription(
        key="1-0:56.7.0",
        translation_key="active_power_l2",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "1-0:76.7.0": ObisSensorDescription(
        key="1-0:76.7.0",
        translation_key="active_power_l3",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Voltage (V) - measurement
    "1-0:32.7.0": ObisSensorDescription(
        key="1-0:32.7.0",
        translation_key="voltage_l1",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "1-0:52.7.0": ObisSensorDescription(
        key="1-0:52.7.0",
        translation_key="voltage_l2",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "1-0:72.7.0": ObisSensorDescription(
        key="1-0:72.7.0",
        translation_key="voltage_l3",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Current (A) - measurement
    "1-0:31.7.0": ObisSensorDescription(
        key="1-0:31.7.0",
        translation_key="current_l1",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "1-0:51.7.0": ObisSensorDescription(
        key="1-0:51.7.0",
        translation_key="current_l2",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "1-0:71.7.0": ObisSensorDescription(
        key="1-0:71.7.0",
        translation_key="current_l3",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Frequency (Hz) - measurement
    "1-0:14.7.0": ObisSensorDescription(
        key="1-0:14.7.0",
        translation_key="frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Power factor - measurement
    "1-0:13.7.0": ObisSensorDescription(
        key="1-0:13.7.0",
        translation_key="power_factor",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "1-0:33.7.0": ObisSensorDescription(
        key="1-0:33.7.0",
        translation_key="power_factor_l1",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "1-0:53.7.0": ObisSensorDescription(
        key="1-0:53.7.0",
        translation_key="power_factor_l2",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "1-0:73.7.0": ObisSensorDescription(
        key="1-0:73.7.0",
        translation_key="power_factor_l3",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
}


# --- Diagnostic Sensor Descriptions ---


@dataclass(frozen=True, kw_only=True)
class DiagnosticSensorDescription(SensorEntityDescription):
    """Describes a WattWächter diagnostic sensor."""

    system_section: str
    system_key: str


DIAGNOSTIC_SENSORS: tuple[DiagnosticSensorDescription, ...] = (
    DiagnosticSensorDescription(
        key="wifi_signal",
        translation_key="wifi_signal",
        system_section="wifi",
        system_key="signal_strength",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    DiagnosticSensorDescription(
        key="wifi_ssid",
        translation_key="wifi_ssid",
        system_section="wifi",
        system_key="ssid",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    DiagnosticSensorDescription(
        key="ip_address",
        translation_key="ip_address",
        system_section="wifi",
        system_key="ip_address",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    DiagnosticSensorDescription(
        key="firmware_version",
        translation_key="firmware_version",
        system_section="esp",
        system_key="os_version",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    DiagnosticSensorDescription(
        key="uptime",
        translation_key="uptime",
        system_section="uptime",
        system_key="uptime",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)
