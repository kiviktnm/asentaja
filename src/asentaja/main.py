import os
import subprocess

from asentaja.asetukset import komennot as cmd
from asentaja.asetukset import tiedostojärjestelmän_alku
import asentaja.tallennus
import asentaja


def päivitys():
    # Suoritusjärjestyksellä on merkitystä

    asentaja.grub.asenna()

    nykyiset_paketit = subprocess.check_output(cmd["listaa-asennetut"], shell=True).decode().split()
    nykyiset_palvelut = asentaja.tallennus.lue_lista("aktivoidut-palvelut")
    nykyiset_tiedostot = asentaja.tallennus.lue_lista("kirjoitetut-tiedostot")

    _päivitä()
    _asenna_uudet_paketit(nykyiset_paketit)
    luodut_tiedostot = _luo_tiedostot()
    _aktivoi_uudet_palvelut(nykyiset_palvelut)
    _deaktivoi_poistetut_palvelut(nykyiset_palvelut)
    _poista_poistetut_paketit(nykyiset_paketit)
    _tuhoa_poistetut_tiedostot(nykyiset_tiedostot, luodut_tiedostot)

    _luo_grub_asetukset()
    _generoi_mkinitcpio()


def _päivitä():
    subprocess.run(cmd["päivitä"], shell=True)


def _asenna_uudet_paketit(nykyiset_paketit):
    uudet_paketit = []

    for paketti in asentaja.paketit:
        if paketti not in nykyiset_paketit:
            uudet_paketit.append(paketti)

    if uudet_paketit:
        subprocess.run(cmd["asenna"].format(" ".join(uudet_paketit)), shell=True)


def _luo_tiedostot():
    luodut_tiedostot = []

    for kohde, lähde in asentaja.tiedostot.items():
        # Tämä sallii kahden polun, jotka molemmat alkavat '/'-merkillä yhteen liittämisen
        tiedosto = os.path.normpath("/".join([tiedostojärjestelmän_alku, kohde]))
        try:
            tiedoston_kansio = os.path.dirname(tiedosto)

            # Tämä luo puuttuvat kansiot rekursiivisesti ja asettaa niiden omistajan / ryhmän samaksi
            # kuin uuden tiedoston.
            def luo_kansio(kansio):
                if not os.path.isdir(kansio):
                    ylempi_kansio = os.path.dirname(kansio)
                    if not os.path.isdir(ylempi_kansio):
                        luo_kansio(ylempi_kansio)
                    os.mkdir(kansio)
                    os.chown(kansio, lähde.uid(), lähde.gid())

            luo_kansio(tiedoston_kansio)

            with open(tiedosto, "wt") as t:
                t.write(lähde.hanki_sisältö())
                luodut_tiedostot.append(tiedosto)
            
            os.chmod(tiedosto, lähde.oikeudet)
            os.chown(tiedosto, lähde.uid(), lähde.gid())
        except Exception as e:
            print(f"Tiedoston '{tiedosto}' kirjoittaminen epäonnistui.")
            print(e)

    asentaja.tallennus.kirjoita_lista("kirjoitetut-tiedostot", sisältö=luodut_tiedostot)

    return luodut_tiedostot


def _aktivoi_uudet_palvelut(nykyiset_palvelut):
    aktivoitavat_palvelut = []

    for palvelu in asentaja.palvelut:
        if palvelu not in nykyiset_palvelut:
            aktivoitavat_palvelut.append(palvelu)

    subprocess.run(cmd["aktivoi-palvelu"].format(" ".join(aktivoitavat_palvelut)), shell=True)


def _deaktivoi_poistetut_palvelut(nykyiset_palvelut):
    deaktivoitavat_palvelut = []

    for palvelu in nykyiset_palvelut:
        if palvelu not in asentaja.palvelut:
            deaktivoitavat_palvelut.append(palvelu)

    subprocess.run(cmd["deaktivoi-palvelu"].format(" ".join(deaktivoitavat_palvelut)), shell=True)


def _poista_poistetut_paketit(nykyiset_paketit):
    poistettavat_paketit = []

    for paketti in nykyiset_paketit:
        if paketti not in asentaja.paketit:
            poistettavat_paketit.append(paketti)

    if poistettavat_paketit:
        subprocess.run(cmd["poista"].format(" ".join(poistettavat_paketit)), shell=True)


def _tuhoa_poistetut_tiedostot(nykyiset_tiedostot, luodut_tiedostot):
    for tiedosto in nykyiset_tiedostot:
        if tiedosto not in luodut_tiedostot:
            try:
                os.remove(tiedosto)
            except Exception as e:
                print(f"Tiedoston '{tiedosto}' poisto epäonnistui")
                print(e)


def _luo_grub_asetukset():
    grub_asetusten_sijainti = os.path.join(tiedostojärjestelmän_alku, "boot/grub/grub.cfg")
    subprocess.run(cmd["luo-grub-asetukset"].format(grub_asetusten_sijainti), shell=True)


def _generoi_mkinitcpio():
    subprocess.run(cmd["generoi-mkinitcpio"], shell=True)


