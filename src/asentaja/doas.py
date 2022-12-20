import asentaja

class Doas:
    asetukset = "permit persist keepenv :wheel\n"

    def asenna(self):
        asentaja.paketit += [ "opendoas" ]
        asentaja.tiedostot["/etc/doas.conf"] = asentaja.Tiedosto(sisältö=self.asetukset, omistaja="root", ryhmä="root", oikeudet=0o400)

