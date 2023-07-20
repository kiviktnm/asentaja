import asentaja
import asentaja.logger as log

class Grub:
    kernel_parametrit = []
    aktivoi_os_prober = False
    oletusasetukset = """# Tämä tiedosto on Asentajan automaattisesti luoma.
GRUB_CMDLINE_LINUX=""

# Grub muistaa automaattisesti viimeksi valitun tiedoston
GRUB_DEFAULT=saved
GRUB_SAVEDEFAULT=true

# Oletusasetuksia yhdestä automaattisesti luodusta tiedostosta
GRUB_TIMEOUT=5
GRUB_DISTRIBUTOR=Arch
GRUB_PRELOAD_MODULES="part_gpt part_msdos"
GRUB_TIMEOUT_STYLE=menu
GRUB_TERMINAL_INPUT=console
GRUB_GFXMODE=auto
GRUB_GFXPAYLOAD_LINUX=keep
GRUB_DISABLE_RECOVERY=true"""
    lisäasetukset = ""
    suorita_generoimiskomento = False

    def asenna(self):
        grub_asetukset = f"""{self.oletusasetukset}
GRUB_CMDLINE_LINUX_DEFAULT="{" ".join(self.kernel_parametrit)}"
"""
        if self.aktivoi_os_prober:
            asentaja.paketit.append("os-prober")
            grub_asetukset += "GRUB_DISABLE_OS_PROBER=false\n"
        else:
            grub_asetukset += "GRUB_DISABLE_OS_PROBER=true\n"

        grub_asetukset += self.lisäasetukset

        # Tarkista onko grub asetustiedoston sisältö muuttunut. Jos sisältö on muuttunut, generoimiskomento tulee suorittaa.

        try:
            with open("/etc/default/grub", "rt") as asetustiedosto:
                entiset_asetukset = asetustiedosto.read()
            if entiset_asetukset != grub_asetukset:
                log.info("Grub asetukset ovat muuttuneet. Generoimiskomento suoritetaan.")
                self.suorita_generoimiskomento = True
            else:
                log.info("Grub asetukset eivät ole muuttuneet. Generoimiskomentoa ei suoriteta.")
        except OSError:
            log.varoitus("Grub asetustiedoston sisällön luku epäonnistui. Generoimiskomento suoritetaan.")
            self.suorita_generoimiskomento = True

        asentaja.tiedostot["/etc/default/grub"] = asentaja.Tiedosto(sisältö=grub_asetukset)


