import asentaja.options

# Doas

import asentaja.lib.programs.doas
doas = asentaja.lib.programs.doas.Doas()
asentaja.options.register_option(doas)

