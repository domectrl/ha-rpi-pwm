"""Config flow definition for rpi_pwm."""

import logging
from typing import Any, ClassVar

import voluptuous as vol
from homeassistant.components.number import (
    DEFAULT_MAX_VALUE,
    DEFAULT_MIN_VALUE,
    DEFAULT_STEP,
)
from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
)
from homeassistant.const import (
    CONF_MAXIMUM,
    CONF_MINIMUM,
    CONF_MODE,
    CONF_NAME,
    CONF_TYPE,
    Platform,
)
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_FREQUENCY,
    CONF_INVERT,
    CONF_NORMALIZE_LOWER,
    CONF_NORMALIZE_UPPER,
    CONF_PIN,
    CONF_STEP,
    CONST_PWM_FREQ_MAX,
    CONST_PWM_FREQ_MIN,
    DEFAULT_FREQ,
    DOMAIN,
    MODE_AUTO,
    MODE_BOX,
    MODE_SLIDER,
    GPIO12,
    GPIO13,
    GPIO18,
    GPIO19,
    RPI_PWM_PINS,
)

_LOGGER = logging.getLogger(__name__)


class RpiPWMConfigFlow(ConfigFlow, domain=DOMAIN):
    """RpiPWM device Config handler."""

    VERSION = 1

    _all_pins: ClassVar[list[str]] = [GPIO12, GPIO13, GPIO18, GPIO19]
    _available_pins: ClassVar[list[str]] = [GPIO12, GPIO13, GPIO18, GPIO19]

    def _update_free_pins(self) -> None:
        """Update list of pins that are free to use."""
        self._available_pins.clear()
        self._available_pins.extend(self._all_pins)
        for pwm in self.hass.config_entries.async_entries(DOMAIN):
            self._available_pins.remove(pwm.data[CONF_PIN])

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        self._update_free_pins()

        if (  # From 4 pins only 2 can be assigned to PWMs
            len(self._all_pins) - len(self._available_pins) >= RPI_PWM_PINS
        ):
            return self.async_abort(
                reason="All pins are configured: there are only "
                + str(RPI_PWM_PINS)
                + " PWM pins available for use on RPi.",
            )

        options = {}
        options["light"] = "Light"
        options["fan"] = "Fan"
        options["number"] = "Number"
        return self.async_show_menu(menu_options=options)

    async def async_step_light(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Add a light."""
        if user_input is not None:
            # Assign a unique ID to the flow and abort the flow
            # if another flow with the same unique ID is in progress
            title = self._make_entity_title(user_input=user_input)
            await self.async_set_unique_id(title)
            self._abort_if_unique_id_configured()

            user_input[CONF_TYPE] = Platform.LIGHT
            return self.async_create_entry(
                title=self._make_entity_title(user_input=user_input),
                data=user_input,
            )
        return self.async_show_form(
            step_id="light", data_schema=self._generate_schema_light()
        )

    async def async_step_number(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Add a light."""
        if user_input is not None:
            # Assign a unique ID to the flow and abort the flow
            # if another flow with the same unique ID is in progress
            title = self._make_entity_title(user_input=user_input)
            await self.async_set_unique_id(title)
            self._abort_if_unique_id_configured()
            user_input[CONF_TYPE] = Platform.NUMBER
            return self.async_create_entry(
                title=title,
                data=user_input,
            )

        return self.async_show_form(
            step_id="number", data_schema=self._generate_schema_number()
        )

    async def async_step_fan(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Add a light."""
        if user_input is not None:
            # Assign a unique ID to the flow and abort the flow
            # if another flow with the same unique ID is in progress
            title = self._make_entity_title(user_input=user_input)
            await self.async_set_unique_id(title)
            self._abort_if_unique_id_configured()
            user_input[CONF_TYPE] = Platform.FAN
            return self.async_create_entry(
                title=title,
                data=user_input,
            )
        return self.async_show_form(
            step_id="fan", data_schema=self._generate_schema_fan()
        )

    def _generate_schema_light(self) -> vol.Schema:
        """Generate schema for fan config."""
        return self._generate_schema_fan().extend(
            {
                vol.Optional(
                    CONF_FREQUENCY, default=DEFAULT_FREQ
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=CONST_PWM_FREQ_MIN,
                        max=CONST_PWM_FREQ_MAX,
                        mode=selector.NumberSelectorMode.BOX,
                        step=1,
                    ),
                ),
            }
        )

    def _generate_schema_fan(self) -> vol.Schema:
        """Generate schema for fan."""
        pin_selector = [
            selector.SelectOptionDict(value=str(pin), label=str(pin))
            for pin in self._available_pins
        ]
        return vol.Schema(
            {
                vol.Required(CONF_NAME): selector.TextSelector(),
                vol.Required(
                    CONF_PIN, default=str(self._available_pins[0])
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=pin_selector, mode=selector.SelectSelectorMode.DROPDOWN
                    ),
                ),
            }
        )

    def _generate_schema_number(self) -> vol.Schema:
        """Generate schema for number config."""
        return self._generate_schema_light().extend(
            {
                vol.Optional(CONF_INVERT, default=False): selector.BooleanSelector(),
                vol.Optional(
                    CONF_MINIMUM, default=DEFAULT_MIN_VALUE
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(mode=selector.NumberSelectorMode.BOX)
                ),
                vol.Optional(
                    CONF_MAXIMUM, default=DEFAULT_MAX_VALUE
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(mode=selector.NumberSelectorMode.BOX)
                ),
                vol.Optional(
                    CONF_NORMALIZE_LOWER, default=DEFAULT_MIN_VALUE
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(mode=selector.NumberSelectorMode.BOX)
                ),
                vol.Optional(
                    CONF_NORMALIZE_UPPER, default=DEFAULT_MAX_VALUE
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(mode=selector.NumberSelectorMode.BOX)
                ),
                vol.Optional(CONF_STEP, default=DEFAULT_STEP): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, mode=selector.NumberSelectorMode.BOX
                    )
                ),
                vol.Optional(CONF_MODE, default=MODE_SLIDER): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(value=MODE_BOX, label=MODE_BOX),
                            selector.SelectOptionDict(
                                value=MODE_SLIDER, label=MODE_SLIDER
                            ),
                            selector.SelectOptionDict(value=MODE_AUTO, label=MODE_AUTO),
                        ]
                    )
                ),
            }
        )

    def _make_entity_title(self, user_input: dict[str, Any]) -> str:
        """Create a title for the entity."""
        return user_input[CONF_NAME] + " @ pin " + user_input[CONF_PIN]

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Reconfigure the rpi-pwm device."""
        errors = {}
        if user_input is not None:
            # Check if the device was already configured.
            exists = False
            for pca in self.hass.config_entries.async_entries(DOMAIN):
                exists |= (pca.data[CONF_BUS] == user_input[CONF_BUS]) and (
                    pca.data[CONF_ADDR] == user_input[CONF_ADDR]
                )

            if not exists:
                return self.async_update_reload_and_abort(
                    self._get_reconfigure_entry(),
                    data_updates=user_input,
                )
            errors[CONF_ADDR] = "already_configured"

        schema = self.add_suggested_values_to_schema(
            await self._async_bus_scheme(), self._get_reconfigure_entry().data
        )

        return self.async_show_form(
            step_id="reconfigure", data_schema=schema, errors=errors
        )
