"""The RPi PWM component."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from pathlib import Path

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.LIGHT, Platform.NUMBER, Platform.FAN]


def _find_board_revision() -> str:
    """Return board revision of the raspberry pi."""
    """e.g.: Raspberry Pi 5 Model B Rev 1.0."""
    p = Path("//proc//device-tree//model")
    if p.is_file():
        return p.read_text()
    _LOGGER.warning(
        "Could not detect raspberry pi model, are you sure this is a pi?"
        " rpi-pwm will continue in simlation mode."
    )
    return ""


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up rpi-pwm from a config entry."""

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(config_entry_update_listener))
    return True


async def config_entry_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener, called when the config entry options are changed."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
