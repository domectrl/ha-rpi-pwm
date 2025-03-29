"""Support for fans that can be controlled using PWM."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.const import (
    STATE_ON,
    CONF_NAME,
    CONF_TYPE,
    Platform,
)
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.components.fan import (
    ATTR_PERCENTAGE,
    FanEntity,
    FanEntityFeature,
)

from .const import (
    CONF_RPI_MODEL,
    DOMAIN,
    DEFAULT_FAN_PERCENTAGE,
    RPI_UNKNOWN,
    CONF_RPI,
    CONF_RPI_MODEL,
)
from . import _make_pwm_device

if TYPE_CHECKING:
    from types import MappingProxyType

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

_LOGGER = logging.getLogger(__name__)

SUPPORT_SIMPLE_FAN = (
    FanEntityFeature.SET_SPEED | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up this platform for a specific ConfigEntry(==PCA9685 device)."""
    if config_entry.data[CONF_TYPE] == Platform.FAN:
        async_add_entities(
            [
                RpiPwmFan(
                    config=config_entry.data,
                    unique_id=config_entry.unique_id,
                    hass=hass,
                )
            ]
        )


class RpiPwmFan(FanEntity, RestoreEntity):
    """Representation of a simple PWM FAN."""

    _attr_should_poll = False

    def __init__(
        self,
        config: MappingProxyType[str, Any],
        unique_id: str | None,
        hass: HomeAssistant,
    ):
        """Initialize PWM FAN."""
        self._hass = hass
        self._config = config
        self._simulate_rpi = False
        if config[CONF_RPI] == RPI_UNKNOWN:
            self._simulate_rpi = True

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "rpi_gpio")},
            name=DOMAIN.upper(),
            manufacturer="Raspberry Pi",
            model=config[CONF_RPI_MODEL],
        )
        self._attr_unique_id = unique_id
        self._attr_name = config[CONF_NAME]
        self._attr_supported_features = SUPPORT_SIMPLE_FAN
        self._is_on = False
        self._percentage = DEFAULT_FAN_PERCENTAGE

    async def async_added_to_hass(self) -> None:
        """Handle entity about to be added to hass event."""
        await super().async_added_to_hass()

        if not self._simulate_rpi:
            self._pwm = await self._hass.async_add_executor_job(
                _make_pwm_device, self._config
            )
        if last_state := await self.async_get_last_state():
            self._percentage = last_state.attributes.get(
                "percentage", DEFAULT_FAN_PERCENTAGE
            )
            self._is_on = last_state.state == STATE_ON

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._is_on

    @property
    def percentage(self):
        """Return the percentage property."""
        return self._percentage

    def turn_on(self, percentage: None, preset_mode: None, **kwargs) -> None:
        """Turn on the fan."""
        if percentage is not None:
            self._percentage = percentage
        elif ATTR_PERCENTAGE in kwargs:
            self._percentage = kwargs[ATTR_PERCENTAGE]
        if not self._simulate_rpi:
            self._pwm.change_duty_cycle(duty_cycle=self._percentage)
        self._is_on = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs) -> None:
        """Turn the fan off."""
        if self.is_on and not self._simulate_rpi:
            self._pwm.change_duty_cycle(duty_cycle=0)
        self._is_on = False
        self.schedule_update_ha_state()

    def set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        self._percentage = percentage
        if not self._simulate_rpi:
            self._pwm.change_duty_cycle(duty_cycle=self._percentage)
        self._is_on = True
        self.schedule_update_ha_state()
