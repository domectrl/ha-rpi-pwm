"""Constants for the rpi-pwm integration."""

from typing import Final

DOMAIN = "rpi-pwm"

CONF_FREQUENCY = "frequency"
CONF_NORMALIZE_LOWER = "normalize_lower"
CONF_NORMALIZE_UPPER = "normalize_upper"

CONF_INVERT = "invert"
CONF_STEP = "step"
CONF_PIN = "pin"

MODE_SLIDER = "slider"
MODE_BOX = "box"
MODE_AUTO = "auto"

ATTR_FREQUENCY = "frequency"
ATTR_INVERT = "invert"

DEFAULT_BRIGHTNESS = 255
DEFAULT_COLOR = (0.0, 0.0)
DEFAULT_FREQ = 100
DEFAULT_MODE = "auto"
DEFAULT_FAN_PERCENTAGE = 100.0

CONST_HA_MAX_INTENSITY = 256
CONST_PWM_FREQ_MIN = 10
CONST_PWM_FREQ_MAX = 8000

RPI5 = "Raspberry Pi 5"

GPIO12 = "GPIO12"
GPIO13 = "GPIO13"
GPIO18 = "GPIO18"
GPIO19 = "GPIO19"

RPI_PWM_PINS = 2
