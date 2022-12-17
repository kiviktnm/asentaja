import asentaja

class Doas:
    enable = False
    persist = False
    group = "wheel"
    extra_config = ""

    def apply(self):
        if self.enable:
            config = "permit "

            if self.persist:
                config += "persist "

            config += f":{self.group}\n"

            if self.extra_config != "":
                config += self.extra_config + "\n"

            config += "\n"

            asentaja.packages += [ "opendoas" ]
            asentaja.file_mappings["/etc/doas.conf"] = asentaja.FileMapping(content=config, permissions=0o400)

