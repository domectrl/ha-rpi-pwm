# Home Assistant Raspberry Pi PWM custom integration

**The original Home Assistant integration that supported PWM output on direct IO pins  was removed in Home Assistant Core 2022.4. The original rpi_gpi_pwm was stored [here](https://github.com/RedMeKool/HA-Raspberry-pi-GPIO-PWM/). This variant depends on the pigpio add-on, and does not support the RPi5 hardware. In order to make the integration simpler, and less dependency-prone, and running on the RPi5, this integration moves to the lightweight alternative [rpi-hardware-pwm](https://pypi.org/project/rpi-hardware-pwm). This variant is installable and configurable via confg flow instead of via YAML, and does not need other components to be installed on [Home Assistant OS](https://github.com/home-assistant/operating-system). You will only need to configure the overlays in advance.**

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

**Description.**

The rpi-pwm component allows to control multiple outputs using pulse-width modulation. This can be used to control devices, for example LED strips. It supports one-color, RGB and RGBW LEDs driven by the hardware pins. A PWM output can also be configured as a number. Connection to the hardware is made via the device file system of Linux.

Before use you might need to configure your systems overlays. Please check the details at the webpage of [rpi-hardware-pwm](https://pypi.org/project/rpi-hardware-pwm).

**This integration can set up the following platforms.**

Platform | Description
-- | --
`light` | Write LED signal to digital PWM outputs.
`fan` | Control a fan output.
`number` | Writes signal represented by a number to PWM outputs.




### HACS (Preferred)
1. [Add](http://homeassistant.local:8123/hacs/integrations) the custom integration repository: https://github.com/domectrl/ha-rpi-pwm
2. Select `Raspberry Pi PWM` in the Integration tab and click `download`
3. Restart Home Assistant
4. Done!

### Manual
1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `ha-rpi-pwm`.
1. Download _all_ the files from the `custom_components//` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant

## Configuration via user interface:
* In the user interface go to "Configuration" -> "Integrations" click "+" and search for "Raspberry Pi PWM"
* For a description of the configuration parameters, see Configuration parameters

## YAML Configuration

This integration can no longer be configured via YAML. Use the config flow function instead. 
### Configuration parameters

***Light, Fan and number shared settings:***
- name: Name of the entity to create.
  > default: empty 
- pin: Select the pin to be used for your entity. 
  Note that the numbering of the pins corresponds with the GPIO numbers like shown on [pinouts](https://pinout.xyz/). Only the pins not yet occupied by other entities can be selected. Note that only 2 pins can be configured as a PWM pin at the same time, so after configuring 2 pins the config flow will forbide you to add more devices. Note also that you will have to [configure your overlays](https://pypi.org/project/rpi-hardware-pwm) to make the pins of your choice generating PWM output.
  > default: first / next pin available
- frequency: Frequency of the PWM cycles.
  Only for light and number, for fan this value is set to the default (100Hz).
  > default: 100Hz

***number specific settings:***
- invert: Invert signal of the PWM generator
  > default: false
- minimum: Minimal value of the number.
  > default: 0
- maximum: Maximal value of the number. 
  > default: 100
- normalize_lower: Lower value to normalize the output of the PWM signal on. 
  > default: 0
- normalize_upper: Upper value to normalize the output of the PWM output on.
  > default: 100

These last four parameters might require a little more explanation:
- The minimum/maximum define the range one can select on this number, for example 0..100%.
- The 'normalize' parameters define at what range the output of the PWM normalizes. The Raspberry Pi registers can be programmed with a range of 0..100%. In normal cases, the the output register of the PCA9685 is set to 0% for value 0, and 100% for value 100. If the normalize value is for example to 10..60, it will set the register value 0% for each value <10. Above 10, it will start raising the register, up to 100% for value 60. Above 60, the register value will remain 100%.
- Using a negative value for the normalize_lower parameter, will clip the output to the register. This way, someone can assure that the value of the register will be always for larger than, for example, 10%. Using a larger-than-maximum value will clip the output to the register on the upper side.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[commits-shield]: https://img.shields.io/github/commit-activity/y/domectrl/ha-rpi-pwm.svg?style=for-the-badge
[commits]: https://github.com/domectrl/ha-rpi-pwm/commits/main
[hacs]: https://hacs.xyz/
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/domectrl/ha-rpi-pwm.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-domectrl-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/domectrl/ha-rpi-pwm.svg?style=for-the-badge
[releases]: https://github.com/domectrl/ha-rpi-pwm/releases
