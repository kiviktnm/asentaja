import grp
import pwd

class Tiedosto:
    def __init__(self, lähde=None, sisältö="", oikeudet=0o644, omistaja="root", ryhmä="root"):
        self.lähde = lähde
        self.sisältö = sisältö
        self.oikeudet = oikeudet
        self.omistaja = omistaja
        self.ryhmä = ryhmä

    def kirjoita_tiedostoon(self, tiedosto):
        sisältö = bytes(self.sisältö, "utf-8")

        if self.lähde is not None:
            try:
                with open(self.lähde, "rb") as lähde:
                    sisältö = lähde.read()
            except:
                print(f"Tiedoston '{self.lähde}' lukeminen epäonnistui.")
                raise

        with open(tiedosto, "wb") as kohde:
            kohde.write(sisältö)

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

lopetuskomennot: list[str] = []

aktivointikomennot: list[str] = []

import asentaja.grub
grub = asentaja.grub.Grub()

import asentaja.mkinitcpio
mkinitcpio = asentaja.mkinitcpio.Mkinitcpio()

import asentaja.doas
doas = asentaja.doas.Doas()
