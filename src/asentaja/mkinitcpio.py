import asentaja
import asentaja.logger as log

class Mkinitcpio:
    hooks = [ "base", "udev", "autodetect", "modconf", "kms", "keyboard", "keymap", "consolefont", "block", "filesystems", "fsck" ]
    modules = []
    files = []
    binaries = []
    extra_asetukset = ""
    suorita_generoimiskomento = False

    def asenna(self):
        mkinitcpio_asetukset = f"""# Tämä tiedosto on Asentajan automaattisesti luoma.
MODULES=({" ".join(self.modules)})
BINARIES=({" ".join(self.binaries)})
FILES=({" ".join(self.files)})
HOOKS=({" ".join(self.hooks)})
{self.extra_asetukset}"""

        # Tarkista onko mkinitcpio asetustiedoston sisältö muuttunut. Jos sisältö on muuttunut, generoimiskomento tulee suorittaa.

        try:
            with open("/etc/mkinitcpio.conf", "rt") as asetustiedosto:
                entiset_asetukset = asetustiedosto.read()
            if entiset_asetukset != mkinitcpio_asetukset:
                log.info("Mkinitcpio asetukset ovat muuttuneet. Generoimiskomento suoritetaan.")
                self.suorita_generoimiskomento = True
            else:
                log.info("Mkinitcpio asetukset eivät ole muuttuneet. Generoimiskomentoa ei suoriteta.")
        except OSError:
            log.varoitus("Mkinitcpio asetustiedoston sisällön luku epäonnistui. Generoimiskomento suoritetaan.")
            self.suorita_generoimiskomento = True

        asentaja.tiedostot["/etc/mkinitcpio.conf"] = asentaja.Tiedosto(sisältö=mkinitcpio_asetukset)


