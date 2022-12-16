import arconf.options

# Doas

import arconf.lib.programs.doas
doas = arconf.lib.programs.doas.Doas()
arconf.options.register_option(doas)

