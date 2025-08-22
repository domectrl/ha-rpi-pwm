"""The rpi PWM component."""

import logging
from platform import uname
from types import MappingProxyType
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PIN, Platform
from homeassistant.core import HomeAssistant
from rpi_hardware_pwm import HardwarePWM

from .const import (
    CONF_FREQUENCY,
    CONF_RPI,
    GPIO13,
    GPIO18,
    GPIO19,
    KERNEL_VERSION_RPI5_CHIP_2,
    RPI5,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.LIGHT, Platform.NUMBER, Platform.FAN]


def _make_pwm_device(config: MappingProxyType[str, Any]) -> HardwarePWM:
    """Non-async function to create the HardwarePWM object."""
    chip = 0
    channel = 0
    if config[CONF_PIN] in [GPIO13, GPIO19]:
        channel = 1
    if config[CONF_RPI] == RPI5:
        release = uname().release.split(".")
        kernel_version = float(release[0] + "." + release[1])
        if kernel_version <= KERNEL_VERSION_RPI5_CHIP_2:
            chip = 2
        if config[CONF_PIN] in [GPIO18, GPIO19]:
            channel += 2
    pwm = HardwarePWM(
        pwm_channel=channel,
        hz=config[CONF_FREQUENCY],
        chip=chip,
    )
    pwm.start(0)
    return pwm


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
