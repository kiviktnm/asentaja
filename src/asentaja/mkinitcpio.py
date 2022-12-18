import asentaja

class Mkinitcpio:
    hooks = [ "base", "udev", "autodetect", "modconf", "kms", "keyboard", "keymap", "consolefont", "block", "filesystems", "fsck" ]
    modules = []
    files = []
    binaries = []
    extra_asetukset = []

    def asenna(self):
        mkinitcpio_asetukset = f"""# Tämä tiedosto on Asentajan automaattisesti luoma.
MODULES=({" ".join(self.modules)})
BINARIES=({" ".join(self.binaries)})
FILES=({" ".join(self.files)})
HOOKS=({" ".join(self.hooks)})
{self.extra_asetukset}"""

        asentaja.tiedostot["/etc/mkinitcpio.conf"] = asentaja.Tiedosto(sisältö=mkinitcpio_asetukset)


