import asentaja

class Grub:
    kernel_parametrit = []
    oletus = 0
    aikakatkaisu = 5
    aktivoi_os_prober = True
    extra_asetukset = ""

    def asenna(self):
        grub_asetukset = f"""# Tämä tiedosto on Asentajan automaattisesti luoma.
GRUB_DEFAULT={self.oletus}
GRUB_TIMEOUT={self.aikakatkaisu}
GRUB_CMDLINE_LINUX_DEFAULT="{" ".join(self.kernel_parametrit)}"
"""
        if self.aktivoi_os_prober:
            asentaja.paketit.append("os-prober")
            grub_asetukset += "GRUB_DISABLE_OS_PROBER=false\n"
        else:
            grub_asetukset += "GRUB_DISABLE_OS_PROBER=true\n"

        grub_asetukset += self.extra_asetukset
        asentaja.tiedostot["/etc/default/grub"] = asentaja.Tiedosto(sisältö=grub_asetukset)


