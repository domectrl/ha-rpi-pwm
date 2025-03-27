"""Support for numbers that can be controlled using PWM."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.number import (
    RestoreNumber,
)
from homeassistant.const import (
    CONF_MAXIMUM,
    CONF_MINIMUM,
    CONF_MODE,
    CONF_NAME,
    CONF_PIN,
    CONF_TYPE,
    Platform,
)
from homeassistant.helpers.device_registry import DeviceInfo

from .const import (
    ATTR_FREQUENCY,
    ATTR_INVERT,
    CONF_FREQUENCY,
    CONF_INVERT,
    CONF_NORMALIZE_LOWER,
    CONF_NORMALIZE_UPPER,
    CONF_STEP,
    DOMAIN,
    GPIO13,
    GPIO18,
    GPIO19,
    RPI5,
)
from . import _find_board_revision
from rpi_hardware_pwm import HardwarePWM

if TYPE_CHECKING:
    from types import MappingProxyType

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up this platform for a specific ConfigEntry(==PCA9685 device)."""
    if config_entry.data[CONF_TYPE] == Platform.NUMBER:
        _LOGGER.debug(
            "Adding Number %s with id %s",
            config_entry.data[CONF_NAME],
            config_entry.unique_id,
        )
        async_add_entities(
            [
                RpiPwmNumber(
                    config=config_entry.data,
                    unique_id=config_entry.unique_id,
                )
            ]
        )


class RpiPwmNumber(RestoreNumber):
    """Representation of a simple  PWM output."""

    _attr_should_poll = False

    def __init__(
        self,
        config: MappingProxyType[str, Any],
        unique_id: str | None,
    ) -> None:
        """Initialize one-color PWM LED."""
        self._config = config
        self._simulate_rpi = False
        self._rpi_board_revision = _find_board_revision()
        if len(self._rpi_board_revision) == 0:
            self._simulate_rpi = True
        chip = 0
        channel = 0
        if config[CONF_PIN] in [GPIO13, GPIO19]:
            channel = 1
        if self._rpi_board_revision.find(RPI5) != -1:
            chip = 2
            if config[CONF_PIN] in [GPIO18, GPIO19]:
                channel += 2

        if not self._simulate_rpi:
            self._pwm: HardwarePWM = HardwarePWM(
                pwm_channel=channel, hz=config[CONF_FREQUENCY], chip=chip
            )

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "rpi_gpio")},
            name=DOMAIN.upper(),
            manufacturer="Raspberry Pi",
            model=self._rpi_board_revision.strip("\x00"),
        )
        self._attr_unique_id = unique_id

        self._attr_native_min_value = config[CONF_MINIMUM]
        self._attr_native_max_value = config[CONF_MAXIMUM]
        self._attr_native_step = config[CONF_STEP]
        self._attr_mode = config[CONF_MODE]
        self._attr_native_value = config[CONF_MINIMUM]
        self._attr_name = config[CONF_NAME]

    async def async_added_to_hass(self) -> None:
        """Handle entity about to be added to hass event."""
        await super().async_added_to_hass()
        if last_data := await self.async_get_last_number_data():
            try:
                await self.async_set_native_value(float(last_data.native_value))
            except ValueError:
                _LOGGER.warning(
                    "Could not read value %s from last state data for %s!",
                    last_data.native_value,
                    self.name,
                )
        else:
            await self.async_set_native_value(self._config[CONF_MINIMUM])

    @property
    def frequency(self) -> float:
        """Return PWM frequency."""
        if self._simulate_rpi:
            return self._config[CONF_FREQUENCY]
        return self._pwm._hz  # noqa: SLF001

    @property
    def invert(self) -> bool:
        """Return if output is inverted."""
        return self._config[CONF_INVERT]

    @property
    def capability_attributes(self) -> dict[str, Any]:
        """Return capability attributes."""
        attr = super().capability_attributes
        attr[ATTR_FREQUENCY] = self.frequency
        attr[ATTR_INVERT] = self.invert
        return attr

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        # Clip value to limits (don't know if this is required?)
        value = max(value, self._config[CONF_MINIMUM])
        value = min(value, self._config[CONF_MAXIMUM])

        # In case the invert bit is on, invert the value
        used_value = value
        if self._config[CONF_INVERT]:
            used_value = self._config[CONF_NORMALIZE_UPPER] - value
        used_value -= self._config[CONF_NORMALIZE_LOWER]
        # Scale range from N_L..N_U to 0..65535 (pca9685)
        range_pwm = 100.0
        range_value = (
            self._config[CONF_NORMALIZE_UPPER] - self._config[CONF_NORMALIZE_LOWER]
        )

        # Scale to range of the driver
        scaled_value = round((used_value / range_value) * range_pwm)
        # Make sure it will fit in the 12-bits range of the pca9685
        scaled_value = min(range_pwm, scaled_value)
        scaled_value = max(0, scaled_value)
        # Set value to driver
        if not self._simulate_rpi:
            self._pwm.change_duty_cycle(duty_cycle=scaled_value)
        self._attr_native_value = value
        self.schedule_update_ha_state()
