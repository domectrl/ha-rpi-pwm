"""Constants for the rpi-pwm integration."""

DOMAIN = "rpi-pwm"

CONF_FREQUENCY = "frequency"
CONF_NORMALIZE_LOWER = "normalize_lower"
CONF_NORMALIZE_UPPER = "normalize_upper"

CONF_INVERT = "invert"
CONF_STEP = "step"
CONF_RPI = "raspberry_pi"
CONF_RPI_MODEL = "rpi_board_model"

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

RPI1_2_3 = "Raspberry Pi"
RPI5 = "Raspberry Pi 5"
RPI_UNKNOWN = "unknown"

GPIO12 = "GPIO12"
GPIO13 = "GPIO13"
GPIO18 = "GPIO18"
GPIO19 = "GPIO19"

RPI_PWM_PINS = 2
