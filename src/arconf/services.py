# This file contains the global variables to configure preset services.

import arconf.options

# Reflector

import arconf.lib.services.reflector
reflector = arconf.lib.services.reflector.Reflector()
arconf.options.register_option(reflector)

