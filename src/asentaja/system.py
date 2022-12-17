# This file contains global system configuration variables.

import asentaja.options

# Order matters in this file, since other system presets may change the booting preset.
# Only booting preset should ever be modified by another system preset.

# NVIDIA

import asentaja.lib.system.nvidia
nvidia = asentaja.lib.system.nvidia.Nvidia()
asentaja.options.register_option(nvidia)

# AMD / ATI

import asentaja.lib.system.amd
amd = asentaja.lib.system.amd.AMD()
asentaja.options.register_option(amd)

# Booting, keep this last

import asentaja.lib.system.boot
boot = asentaja.lib.system.boot.Boot()
asentaja.options.register_option(boot)

