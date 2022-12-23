import grp
import pwd
import os

# Tämä luo puuttuvat kansiot rekursiivisesti ja asettaa niiden omistajan / ryhmän samaksi
# kuin uuden tiedoston.
def _luo_puuttuvat_kansiot(kansio, omistaja_uid, ryhmä_gid):
    if not os.path.isdir(kansio):
        ylempi_kansio = os.path.dirname(kansio)
        if not os.path.isdir(ylempi_kansio):
            _luo_puuttuvat_kansiot(ylempi_kansio, omistaja_uid, ryhmä_gid)
        os.mkdir(kansio)
        os.chown(kansio, omistaja_uid, ryhmä_gid)

class Tiedosto:
    def __init__(self, lähde=None, sisältö="", oikeudet=0o644, omistaja="root", ryhmä="root"):
        self.lähde = lähde
        self.sisältö = sisältö
        self.oikeudet = oikeudet
        self.omistaja = omistaja
        self.ryhmä = ryhmä

    def kirjoita_tiedostoon(self, tiedosto):
        """Kirjoittaa sisältönsä syötetyyn tiedostoon."""

        sisältö = bytes(self.sisältö, "utf-8")

        if self.lähde is not None:
            try:
                with open(self.lähde, "rb") as lähde:
                    sisältö = lähde.read()
            except:
                print(f"Tiedoston '{self.lähde}' lukeminen epäonnistui.")
                raise

        _luo_puuttuvat_kansiot(os.path.dirname(tiedosto), self.uid(), self.gid())

        with open(tiedosto, "wb") as kohde:
            kohde.write(sisältö)

        os.chmod(tiedosto, self.oikeudet)
        os.chown(tiedosto, self.uid(), self.gid())

        return [ tiedosto ]

    def uid(self):
        return pwd.getpwnam(self.omistaja).pw_uid

    def gid(self):
        return grp.getgrnam(self.ryhmä).gr_gid


class Kansio:
    def __init__(self, lähde, omistaja="root", ryhmä="root", oikeudet=0o644):
        self.lähde = lähde
        self.omistaja = omistaja
        self.ryhmä = ryhmä
        self.oikeudet = oikeudet

    def kirjoita_kansioon(self, kansio):
        """Kirjoittaa kaikki sisältönsä syötettyyn kansioon."""

        luodut_tiedostot = []

        for lähdekansio, _, lähdekansion_tiedostot in os.walk(self.lähde):
            kohdekansio = lähdekansio.replace(self.lähde, kansio, 1)

            _luo_puuttuvat_kansiot(kohdekansio, self.uid(), self.gid())

            for tiedosto in lähdekansion_tiedostot:
                lähdetiedosto = os.path.join(lähdekansio, tiedosto)
                kohdetiedosto = os.path.join(kohdekansio, tiedosto)

                try:
                    with open(lähdetiedosto, "rb") as lähde:
                        with open(kohdetiedosto, "wb") as kohde:
                            kohde.write(lähde.read())
                            luodut_tiedostot.append(kohdetiedosto)
                except OSError as e:
                    print(f"Kansiota '{kansio}' luodess tiedoston '{lähdetiedosto}' kopiointi kohteeseen '{kohdetiedosto}' epäonnistui.")
                    print(e)

                os.chmod(tiedosto, self.oikeudet)
                os.chown(tiedosto, self.uid(), self.gid())

        return luodut_tiedostot

    def uid(self):
        return pwd.getpwnam(self.omistaja).pw_uid

    def gid(self):
        return grp.getgrnam(self.ryhmä).gr_gid


paketit = [
    "base",
    "linux",
    "linux-firmware",
    "python",
    "git",
    "autoconf",
    "automake",
    "binutils",
    "bison",
    "debugedit",
    "fakeroot",
    "flex",
    "gcc",
    "groff",
    "libtool",
    "m4",
    "make",
    "patch",
    "pkgconf",
    "texinfo",
    "which",
    "grub",
    "efibootmgr",
    "pikaur"
]

palvelut: list[str] = []

tiedostot: dict[str, Tiedosto] = {}

kansiot: dict[str, Kansio] = {}

lopetuskomennot: list[str] = []

aktivointikomennot: list[str] = []

import asentaja.grub
grub = asentaja.grub.Grub()

import asentaja.mkinitcpio
mkinitcpio = asentaja.mkinitcpio.Mkinitcpio()

import asentaja.doas
doas = asentaja.doas.Doas()
