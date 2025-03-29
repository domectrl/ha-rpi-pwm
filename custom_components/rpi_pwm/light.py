"""Support for LED lights that can be controlled using PWM."""

import logging
from datetime import timedelta
from types import MappingProxyType
from typing import Any

import homeassistant.util.dt as dt_util
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_TRANSITION,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    CONF_TYPE,
    STATE_ON,
    Platform,
)
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import (
    async_track_time_interval,
)
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import ConfigType

from . import _make_pwm_device
from .const import (
    CONF_RPI,
    CONF_RPI_MODEL,
    DEFAULT_BRIGHTNESS,
    DOMAIN,
    RPI_UNKNOWN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up this platform for a specific PWM pin."""
    if config_entry.data[CONF_TYPE] == Platform.LIGHT:
        async_add_entities(
            [
                RpiPwmLed(
                    hass=hass,
                    config=config_entry.data,
                    unique_id=config_entry.unique_id,
                )
            ]
        )


class RpiPwmLed(LightEntity, RestoreEntity):
    """Representation of a simple one-color PWM LED."""

    _attr_color_mode = ColorMode.BRIGHTNESS

    def __init__(
        self,
        config: MappingProxyType[str, Any],
        unique_id: str | None,
        hass: HomeAssistant,
    ) -> None:
        """Initialize one-color PWM LED."""
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
        self._attr_is_on = False
        self._attr_brightness = DEFAULT_BRIGHTNESS
        self._attr_supported_features |= LightEntityFeature.TRANSITION
        self._attr_name = config[CONF_NAME]
        self._transition_step_time = timedelta(
            milliseconds=150
        )  # Transition step time in ms
        self._transition_lister: CALLBACK_TYPE | None = None
        self._transition_start = dt_util.utcnow().replace(microsecond=0)
        self._transition_end = self._transition_start
        self._transition_begin_brightness: float = 0.0
        self._transition_end_brightness: float = 0.0
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    async def async_added_to_hass(self) -> None:
        """Handle entity about to be added to hass event."""
        await super().async_added_to_hass()

        if not self._simulate_rpi:
            self._pwm = await self._hass.async_add_executor_job(
                _make_pwm_device, self._config
            )

        if last_state := await self.async_get_last_state():
            self._attr_is_on = last_state.state == STATE_ON
            self._attr_brightness = last_state.attributes.get(
                "brightness", DEFAULT_BRIGHTNESS
            )
            if (self._attr_brightness is not None) and not self._simulate_rpi:
                self._hass.async_add_executor_job(
                    self._pwm.start, self._from_hass_brightness(self._attr_brightness)
                )

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    async def async_turn_on(self, **kwargs: ConfigType) -> None:
        """Turn on a led."""
        if ATTR_BRIGHTNESS in kwargs:
            self._attr_brightness = kwargs[ATTR_BRIGHTNESS]

        if ATTR_TRANSITION in kwargs:
            transition_time: float = kwargs[ATTR_TRANSITION]
            await self._async_start_transition(
                brightness=self._from_hass_brightness(self._attr_brightness),
                duration=timedelta(seconds=transition_time),
            )
        elif not self._simulate_rpi:
            self._hass.async_add_executor_job(
                self._pwm.change_duty_cycle,
                self._from_hass_brightness(self._attr_brightness),
            )
        self._attr_is_on = True
        self.schedule_update_ha_state()

    async def async_turn_off(self, **kwargs: ConfigType) -> None:
        """Turn off a LED."""
        if self.is_on:
            if ATTR_TRANSITION in kwargs:
                transition_time: float = kwargs[ATTR_TRANSITION]
                await self._async_start_transition(
                    brightness=0, duration=timedelta(seconds=transition_time)
                )
            elif not self._simulate_rpi:
                self._hass.async_add_executor_job(self._pwm.change_duty_cycle, 0.0)

        self._attr_is_on = False
        self.schedule_update_ha_state()

    async def _async_start_transition(
        self, brightness: float, duration: timedelta
    ) -> None:
        """Start light transitio."""
        # First check if a transition was in progress; in that case stop it.
        if self._transition_lister:
            self._transition_lister()
        # initialize relevant values
        if not self._simulate_rpi:
            self._transition_begin_brightness = self._pwm._duty_cycle  # noqa: SLF001
        if self._transition_begin_brightness != brightness:
            self._transition_start = dt_util.utcnow()
            self._transition_end = self._transition_start + duration
            self._transition_end_brightness = brightness
            # Start transition cycles.
            self._transition_lister = async_track_time_interval(
                self.hass, self._async_step_transition, self._transition_step_time
            )

    @callback
    async def _async_step_transition(self, args: None = None) -> None:  # noqa: ARG002
        """Cycle for transition of output."""
        # Calculate switch off time, and if in the future, add a lister to hass
        now = dt_util.utcnow()
        if now > self._transition_end:
            if not self._simulate_rpi:
                self._hass.async_add_executor_job(
                    self._pwm.change_duty_cycle,
                    self._transition_end_brightness,
                )
            if self._transition_lister:
                self._transition_lister()  # Stop cycling
        else:
            elapsed: float = (now - self._transition_start).total_seconds()
            total_transition: float = (
                self._transition_end - self._transition_start
            ).total_seconds()
            target_brightness = int(
                self._transition_begin_brightness
                + (
                    (
                        (
                            self._transition_end_brightness
                            - self._transition_begin_brightness
                        )
                        * elapsed
                    )
                    / total_transition
                )
            )
            if not self._simulate_rpi:
                self._hass.async_add_executor_job(
                    self._pwm.change_duty_cycle, target_brightness
                )

    def _from_hass_brightness(self, brightness: int | None) -> float:
        """Convert Home Assistant  units (0..256) to 0.0..1000."""
        if brightness:
            r_val = (brightness * 100.0) / 255
            r_val = min(r_val, 100.0)
            return max(r_val, 0.0)

        return 0
