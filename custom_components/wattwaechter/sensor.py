
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from . import DOMAIN

OBIS_INFO = {
    # Energiezähler
    "1.8.0": {"name": "Bezug (1.8.0)", "unit": "kWh", "device_class": "energy", "state_class": "total_increasing"},
    "2.8.0": {"name": "Einspeisung (2.8.0)", "unit": "kWh", "device_class": "energy", "state_class": "total_increasing"},
    "1.8.1": {"name": "Bezug Tarif 1", "unit": "kWh", "device_class": "energy", "state_class": "total_increasing"},
    "1.8.2": {"name": "Bezug Tarif 2", "unit": "kWh", "device_class": "energy", "state_class": "total_increasing"},
    "2.8.1": {"name": "Einspeisung Tarif 1", "unit": "kWh", "device_class": "energy", "state_class": "total_increasing"},
    "2.8.2": {"name": "Einspeisung Tarif 2", "unit": "kWh", "device_class": "energy", "state_class": "total_increasing"},

    # Momentanleistung
    "16.7.0": {"name": "Wirkleistung (gesamt)", "unit": "W", "device_class": "power", "state_class": "measurement"},
    "36.7.0": {"name": "Leistung L1", "unit": "W", "device_class": "power", "state_class": "measurement"},
    "56.7.0": {"name": "Leistung L2", "unit": "W", "device_class": "power", "state_class": "measurement"},
    "76.7.0": {"name": "Leistung L3", "unit": "W", "device_class": "power", "state_class": "measurement"},

    # Spannung
    "32.7.0": {"name": "Spannung L1", "unit": "V", "device_class": "voltage", "state_class": "measurement"},
    "52.7.0": {"name": "Spannung L2", "unit": "V", "device_class": "voltage", "state_class": "measurement"},
    "72.7.0": {"name": "Spannung L3", "unit": "V", "device_class": "voltage", "state_class": "measurement"},

    # Stromstärke
    "31.7.0": {"name": "Strom L1", "unit": "A", "device_class": "current", "state_class": "measurement"},
    "51.7.0": {"name": "Strom L2", "unit": "A", "device_class": "current", "state_class": "measurement"},
    "71.7.0": {"name": "Strom L3", "unit": "A", "device_class": "current", "state_class": "measurement"},

    # Frequenz (falls unterstützt)
    "14.7.0": {"name": "Frequenz", "unit": "Hz", "device_class": "frequency", "state_class": "measurement"},

    # Blindleistung (var)
    "18.7.0": {"name": "Blindleistung", "unit": "var", "device_class": None, "state_class": "measurement"},

    # Scheinleistung (VA)
    "30.7.0": {"name": "Scheinleistung gesamt", "unit": "VA", "device_class": None, "state_class": "measurement"},

    # Leistungsfaktor (cos φ)
    "33.7.0": {"name": "Leistungsfaktor L1", "unit": "", "device_class": None, "state_class": "measurement"},
    "53.7.0": {"name": "Leistungsfaktor L2", "unit": "", "device_class": None, "state_class": "measurement"},
    "73.7.0": {"name": "Leistungsfaktor L3", "unit": "", "device_class": None, "state_class": "measurement"},

    # Zählernummer (string)
    "0.0.0": {"name": "Zählernummer", "unit": "", "device_class": None, "state_class": None},

    # Aktuelle Uhrzeit (falls verfügbar)
    "0.9.1": {"name": "Uhrzeit", "unit": "", "device_class": "timestamp", "state_class": None},
    "0.9.2": {"name": "Datum", "unit": "", "device_class": "timestamp", "state_class": None},
}

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    initial_data = coordinator.data

    entities = []

    for obis_code, value in initial_data.items():
        info = OBIS_INFO.get(obis_code, {
            "name": f"OBIS {obis_code}",
            "unit": "",
            "device_class": None,
            "state_class": None
        })

        entities.append(WattwaechterSensor(coordinator, obis_code, info))

    async_add_entities(entities)

class WattwaechterSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, obis, info):
        super().__init__(coordinator)
        self._obis = obis
        self._attr_name = info["name"]
        self._attr_native_unit_of_measurement = info["unit"]
        self._attr_device_class = info["device_class"]
        self._attr_state_class = info["state_class"]
        device_id = coordinator.device_id  # MAC oder serialno vom ESP32 – eindeutig pro Gerät
        self._attr_unique_id = f"wattwaechter_{device_id}_{obis}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "wattwaechter")},
            "name": "Wattwächter",
            "manufacturer": "Wattwächter",
            "model": "ESP32-C6"
        }

    @property
    def native_value(self):
        return self.coordinator.data.get(self._obis)
