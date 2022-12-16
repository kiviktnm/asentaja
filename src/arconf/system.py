# This file contains global system configuration variables.

import arconf.options

# Order matters in this file, since other system presets may change the booting preset.
# Only booting preset should ever be modified by another system preset.

# NVIDIA

import arconf.lib.system.nvidia
nvidia = arconf.lib.system.nvidia.Nvidia()
arconf.options.register_option(nvidia)

# AMD / ATI

import arconf.lib.system.amd
amd = arconf.lib.system.amd.AMD()
arconf.options.register_option(amd)

# Booting, keep this last

import arconf.lib.system.boot
boot = arconf.lib.system.boot.Boot()
arconf.options.register_option(boot)

