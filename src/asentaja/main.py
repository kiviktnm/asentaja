import os
import subprocess

from asentaja.asetukset import komennot as cmd
from asentaja.asetukset import tiedostojärjestelmän_alku
import asentaja.tallennus
import asentaja


def päivitys(vain_tiedostot=False):
    # Suoritusjärjestyksellä on merkitystä

    asentaja.grub.asenna()
    asentaja.mkinitcpio.asenna()
    asentaja.doas.asenna()

    try:
        nykyiset_paketit = subprocess.check_output(cmd["listaa-asennetut"], shell=True).decode().split()
    except subprocess.CalledProcessError as e:
        print("Pakettien listaus epäonnistui. Keskeytetään ohjelman suorittaminen.")
        print(e)
        exit(10)

    nykyiset_palvelut = asentaja.tallennus.lue_lista("aktivoidut-palvelut")
    nykyiset_tiedostot = asentaja.tallennus.lue_lista("kirjoitetut-tiedostot")
    suoritetut_aktivointikomennot = asentaja.tallennus.lue_lista("suoritetut-aktivointikomennot")

    if vain_tiedostot:
        luodut_tiedostot = _luo_tiedostot()
        _tuhoa_poistetut_tiedostot(nykyiset_tiedostot, luodut_tiedostot)
        return

    _päivitä()
    _asenna_uudet_paketit(nykyiset_paketit)

    # _luo_tiedostot() uudelleenluo kaikki tiedostot jolloin ei ole oleellista ottaa huomioon aikaisemmin tehtyja asioita kuten esim palveluiden kohdalla täytyy.
    luodut_tiedostot = _luo_tiedostot()
    kaikki_aktivoidut_palvelut = _aktivoi_uudet_palvelut(nykyiset_palvelut)
    _deaktivoi_poistetut_palvelut(nykyiset_palvelut)
    _poista_poistetut_paketit(nykyiset_paketit)
    _tuhoa_poistetut_tiedostot(nykyiset_tiedostot, luodut_tiedostot)

    kaikki_suoritetut_aktivointikomennot = _suorita_aktivointikomennot(suoritetut_aktivointikomennot)

    _suorita_lopetuskomennot()

    asentaja.tallennus.kirjoita_lista("kirjoitetut-tiedostot", sisältö=luodut_tiedostot)
    asentaja.tallennus.kirjoita_lista("aktivoidut-palvelut", sisältö=kaikki_aktivoidut_palvelut)
    asentaja.tallennus.kirjoita_lista("suoritetut-aktivointikomennot", sisältö=kaikki_suoritetut_aktivointikomennot)


def _päivitä():
    try:
        subprocess.run(cmd["päivitä"], shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Pakettien päivitys epäonnistui. Keskeytetään ohjelman suorittaminen.")
        print(e)
        exit(20)


def _asenna_uudet_paketit(nykyiset_paketit):
    uudet_paketit = []

    for paketti in asentaja.paketit:
        if paketti not in nykyiset_paketit:
            uudet_paketit.append(paketti)

    if uudet_paketit:
        try:
            subprocess.run(cmd["asenna"].format(" ".join(uudet_paketit)), shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f'Pakettien \'{", ".join(uudet_paketit)}\' asennus epäonnistui. Keskeytetään ohjelman suorittaminen.')
            print(e)
            exit(30)


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

            lähde.kirjoita_tiedostoon(tiedosto)
            luodut_tiedostot.append(tiedosto)
            
            os.chmod(tiedosto, lähde.oikeudet)
            os.chown(tiedosto, lähde.uid(), lähde.gid())
        except OSError as e:
            print(f"Tiedoston '{tiedosto}' kirjoittaminen epäonnistui.")
            print(e)

    return luodut_tiedostot


def _aktivoi_uudet_palvelut(nykyiset_palvelut):
    aktivoitavat_palvelut = []
    aikaisemmin_aktivoidut_palvelut = []

    # Jokainen palvelu käydään läpi erikseen, jolloin on mahdollista osoittaa, minkä palvelun aktivointi epäonnistui.

    for palvelu in asentaja.palvelut:
        if palvelu in nykyiset_palvelut:
            aikaisemmin_aktivoidut_palvelut.append(palvelu)
        else:
            try:
                subprocess.run(cmd["aktivoi-palvelu"].format(palvelu), shell=True, check=True)
                aktivoitavat_palvelut.append(palvelu)
            except subprocess.CalledProcessError as e:
                print(f"Palvelun '{palvelu}' aktivointi epäonnistui.")
                print(e)

    # Palauttaa kaikki koskaan aktivoidut palvelut (ei vain tällä kertaa aktivoidut)
    return aktivoitavat_palvelut + aikaisemmin_aktivoidut_palvelut


def _deaktivoi_poistetut_palvelut(nykyiset_palvelut):
    # Jokainen palvelu käydään läpi erikseen, jolloin on mahdollista osoittaa, minkä palvelun deaktivointi epäonnistui.

    for palvelu in nykyiset_palvelut:
        if palvelu not in asentaja.palvelut:
            try:
                subprocess.run(cmd["deaktivoi-palvelu"].format(palvelu), shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Palvelun '{palvelu}' deaktivointi epäonnistui.")
                print(e)


def _poista_poistetut_paketit(nykyiset_paketit):
    poistettavat_paketit = []

    for paketti in nykyiset_paketit:
        if paketti not in asentaja.paketit:
            poistettavat_paketit.append(paketti)

    if poistettavat_paketit:
        try:
            subprocess.run(cmd["poista"].format(" ".join(poistettavat_paketit)), shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f'Pakettien \'{", ".join(poistettavat_paketit)}\' poisto epäonnistui.')
            print(e)


def _tuhoa_poistetut_tiedostot(nykyiset_tiedostot, luodut_tiedostot):
    for tiedosto in nykyiset_tiedostot:
        if tiedosto not in luodut_tiedostot:
            try:
                os.remove(tiedosto)
            except OSError as e:
                print(f"Tiedoston '{tiedosto}' poisto epäonnistui")
                print(e)


def _suorita_aktivointikomennot(suoritetut_aktivointikomennot):
    aikaisemmin_suoritetut_aktivointikomennot = []
    nyt_suoritetut_aktivointikomennot = []

    for komento in asentaja.aktivointikomennot:
        if komento in suoritetut_aktivointikomennot:
            aikaisemmin_suoritetut_aktivointikomennot.append(komento)
        else:
            try:
                subprocess.run(komento, shell=True, check=True)
                nyt_suoritetut_aktivointikomennot.append(komento)
            except subprocess.CalledProcessError as e:
                print(f"Aktivointikomennon '{komento}' suorittaminen epäonnistui.")
                print(e)

    return aikaisemmin_suoritetut_aktivointikomennot + nyt_suoritetut_aktivointikomennot


def _suorita_lopetuskomennot():
    grub_asetusten_sijainti = os.path.join(tiedostojärjestelmän_alku, "boot/grub/grub.cfg")

    try:
        subprocess.run(cmd["luo-grub-asetukset"].format(grub_asetusten_sijainti), shell=True)
        subprocess.run(cmd["generoi-mkinitcpio"], shell=True)
    except subprocess.CalledProcessError as e:
        print("Grub-asetuksien tai mkinitcpion generaatio epäonnistui.")
        print(e)

    for komento in asentaja.lopetuskomennot:
        try:
            subprocess.run(komento, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Lopetuskomennon '{komento}' suorittaminen epäonnistui.")
            print(e)

