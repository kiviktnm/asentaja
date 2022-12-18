import grp
import pwd

class Tiedosto:
    def __init__(self, lähde=None, sisältö="", oikeudet=0o644, omistaja="root", ryhmä="root"):
        self.lähde = lähde
        self.sisältö = sisältö
        self.oikeudet = oikeudet
        self.omistaja = omistaja
        self.ryhmä = ryhmä

    def hanki_sisältö(self):
        if self.lähde is not None:
            try:
                with open(self.lähde, "rt") as tiedosto:
                    return tiedosto.read()
            except Exception as e:
                print(f"Tiedoston '{self.lähde}' lukeminen epäonnistui.")
                print(e)
                return self.sisältö
        else:
            return self.sisältö

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
    "opendoas",
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

import asentaja.grub
grub = asentaja.grub.Grub()

import asentaja.mkinitcpio
mkinitcpio = asentaja.mkinitcpio.Mkinitcpio()


