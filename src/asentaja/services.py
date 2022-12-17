# This file contains the global variables to configure preset services.

import asentaja.options

# Reflector

import asentaja.lib.services.reflector
reflector = asentaja.lib.services.reflector.Reflector()
asentaja.options.register_option(reflector)

