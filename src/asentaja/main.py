import os
import subprocess

from asentaja.asetukset import komennot as cmd
from asentaja.asetukset import tiedostojärjestelmän_alku
import asentaja.tallennus
import asentaja
import asentaja.logger as log


def päivitys(vain_tiedostot=False):
    log.info("Aloitetaan päivitys.")

    # Suoritusjärjestyksellä on merkitystä

    asentaja.grub.asenna()
    asentaja.mkinitcpio.asenna()
    asentaja.doas.asenna()

    _käsittele_kokonaisuudet(vain_tiedostot)

    nykyiset_tiedostot = asentaja.tallennus.lue_lista("kirjoitetut-tiedostot")

    if vain_tiedostot:
        log.info("Asennetaan vain tiedostoja.")
        luodut_tiedostot = _luo_tiedostot()
        _tuhoa_poistetut_tiedostot(nykyiset_tiedostot, luodut_tiedostot)
        return

    log.info("Tarkistetaan nykyiset paketit.")
    try:
        nykyiset_paketit = subprocess.check_output(cmd["listaa-asennetut"], shell=True).decode().split()
    except subprocess.CalledProcessError as e:
        log.virhe("Pakettien listaus epäonnistui.")
        log.virhetiedot(e)
        exit(10)

    nykyiset_palvelut = asentaja.tallennus.lue_lista("aktivoidut-palvelut")
    suoritetut_aktivointikomennot = asentaja.tallennus.lue_lista("suoritetut-aktivointikomennot")
    nykyiset_kokonaisuudet = asentaja.tallennus.lue_lista("aktivoidut-kokonaisuudet")

    _päivitä()
    _asenna_uudet_paketit(nykyiset_paketit)

    # _luo_tiedostot() uudelleenluo kaikki tiedostot jolloin ei ole oleellista ottaa huomioon aikaisemmin tehtyja asioita kuten esim palveluiden kohdalla täytyy.
    luodut_tiedostot = _luo_tiedostot()
    kaikki_aktivoidut_palvelut = _aktivoi_uudet_palvelut(nykyiset_palvelut)
    _deaktivoi_poistetut_palvelut(nykyiset_palvelut)
    _poista_poistetut_paketit()
    _tuhoa_poistetut_tiedostot(nykyiset_tiedostot, luodut_tiedostot)
    _suorita_deaktivointikomennot(nykyiset_kokonaisuudet)

    kaikki_suoritetut_aktivointikomennot = _suorita_aktivointikomennot(suoritetut_aktivointikomennot)

    _suorita_lopetuskomennot()

    log.info("Päivitys valmis.")

    asentaja.tallennus.kirjoita_lista("kirjoitetut-tiedostot", sisältö=luodut_tiedostot)
    asentaja.tallennus.kirjoita_lista("aktivoidut-palvelut", sisältö=kaikki_aktivoidut_palvelut)
    asentaja.tallennus.kirjoita_lista("suoritetut-aktivointikomennot", sisältö=kaikki_suoritetut_aktivointikomennot)
    asentaja.tallennus.kirjoita_lista("aktivoidut-kokonaisuudet", sisältö=asentaja.aktiiviset_kokonaisuudet)


def _käsittele_kokonaisuudet(vain_tiedostot):
    for kokonaisuus in asentaja.aktiiviset_kokonaisuudet:
        if kokonaisuus not in asentaja.kokonaisuudet.keys():
            log.varoitus(f"Kokonaisuutta '{kokonaisuus}' ei ole määritelty. Se jätetään huomiotta.")
            continue

        tiedostomuuttujat = asentaja.kokonaisuudet[kokonaisuus].get("tiedostomuuttujat", {})

        for tiedostonimi, tiedosto in asentaja.kokonaisuudet[kokonaisuus].get("tiedostot", {}).items():
            if tiedosto.tiedostomuuttujat is not None:
                tiedosto.tiedostomuuttujat.update(tiedostomuuttujat)
            else:
                tiedosto.tiedostomuuttujat = tiedostomuuttujat
            asentaja.tiedostot[tiedostonimi] = tiedosto

        for kansionimi, kansio in asentaja.kokonaisuudet[kokonaisuus].get("kansiot", {}).items():
            if kansio.tiedostomuuttujat is not None:
                kansio.tiedostomuuttujat.update(tiedostomuuttujat)
            else:
                kansio.tiedostomuuttujat = tiedostomuuttujat
            asentaja.kansiot[kansionimi] = kansio

        # Jos vain tiedostot käsitellään, kokonaisuuksistakin käsitellään vain tiedostot ja kansiot.
        if vain_tiedostot:
            continue

        asentaja.paketit += asentaja.kokonaisuudet[kokonaisuus].get("paketit", [])
        asentaja.palvelut += asentaja.kokonaisuudet[kokonaisuus].get("palvelut", [])
        asentaja.lopetuskomennot += asentaja.kokonaisuudet[kokonaisuus].get("lopetuskomennot", [])
        asentaja.aktivointikomennot += asentaja.kokonaisuudet[kokonaisuus].get("aktivointikomennot", [])

        deaktivointikomennot = asentaja.kokonaisuudet[kokonaisuus].get("deaktivointikomennot", [])
        asentaja.tallennus.kirjoita_lista(f"deaktivointikomennot-{kokonaisuus}", sisältö=deaktivointikomennot)


def _päivitä():
    log.info("Päivitetään järjestelmän nykyiset paketit.")
    try:
        subprocess.run(cmd["päivitä"], shell=True, check=True)
    except subprocess.CalledProcessError as e:
        log.virhe("Nykyisten pakettien päivitys epäonnistui.")
        log.virhetiedot(e)
        exit(12)


def _asenna_uudet_paketit(nykyiset_paketit):
    uudet_paketit = []

    for paketti in asentaja.paketit:
        if paketti not in nykyiset_paketit:
            uudet_paketit.append(paketti)

    if uudet_paketit:
        log.info(f"Asennetaan uudet paketit '{' '.join(uudet_paketit)}'.")
        try:
            subprocess.run(cmd["asenna"].format(" ".join(uudet_paketit)), shell=True, check=True)
        except subprocess.CalledProcessError as e:
            log.virhe(f'Pakettien \'{" ".join(uudet_paketit)}\' asennus epäonnistui.')
            log.virhetiedot(e)
            exit(13)
    else:
        log.info("Ei uusia paketteja asennettavaksi.")


def _luo_tiedostot():
    luodut_tiedostot = []

    for kohde, lähde in asentaja.tiedostot.items():
        log.info(f"Luodaan tiedosto '{kohde}'.")

        # Tämä sallii kahden polun, jotka molemmat alkavat '/'-merkillä yhteen liittämisen
        tiedosto = os.path.normpath("/".join([tiedostojärjestelmän_alku, kohde]))
        luodut_tiedostot += lähde.kirjoita_tiedostoon(tiedosto)

    for kohde, lähde in asentaja.kansiot.items():
        log.info(f"Kopioidaan kansio '{lähde.lähde}' kohteeseen '{kohde}'.")

        kansio = os.path.normpath("/".join([tiedostojärjestelmän_alku, kohde]))
        luodut_tiedostot += lähde.kirjoita_kansioon(kansio)

    return luodut_tiedostot


def _aktivoi_uudet_palvelut(nykyiset_palvelut):
    aktivoitavat_palvelut = []
    aikaisemmin_aktivoidut_palvelut = []

    for palvelu in asentaja.palvelut:
        if palvelu in nykyiset_palvelut:
            aikaisemmin_aktivoidut_palvelut.append(palvelu)
        else:
            aktivoitavat_palvelut.append(palvelu)

    if aktivoitavat_palvelut:
        log.info(f"Aktivoidaan uudet palvelut '{' '.join(aktivoitavat_palvelut)}'.")
        try:
            subprocess.run(cmd["aktivoi-palvelu"].format(" ".join(aktivoitavat_palvelut)), shell=True, check=True)
        except subprocess.CalledProcessError as e:
            log.virhe(f"Palveluiden '{' '.join(aktivoitavat_palvelut)}' aktivointi epäonnistui.")
            log.virhetiedot(e)
            exit(14)
    else:
        log.info("Ei uusia palveluita aktivoitavaksi.")

    # Palauttaa kaikki koskaan aktivoidut palvelut (ei vain tällä kertaa aktivoidut)
    return aktivoitavat_palvelut + aikaisemmin_aktivoidut_palvelut


def _deaktivoi_poistetut_palvelut(nykyiset_palvelut):
    deaktivoitavat_palvelut = []

    for palvelu in nykyiset_palvelut:
        if palvelu not in asentaja.palvelut:
            deaktivoitavat_palvelut.append(palvelu)

    if deaktivoitavat_palvelut:
        log.info(f"Deaktivoidaan palvelut '{' '.join(deaktivoitavat_palvelut)}'.")
        try:
            subprocess.run(cmd["deaktivoi-palvelu"].format(" ".join(deaktivoitavat_palvelut)), shell=True, check=True)
        except subprocess.CalledProcessError as e:
            log.virhe(f"Palveluiden '{' '.join(deaktivoitavat_palvelut)}' deaktivointi epäonnistui.")
            log.virhetiedot(e)
            exit(15)
    else:
        log.info("Ei palveluita deaktivoitavaksi.")


def _poista_poistetut_paketit():
    poistettavat_paketit = []

    # Nykyiset paketit selvitetään uudestaan, koska asennuksen aikana joku paketti on voinut korvata toisen.
    try:
        nykyiset_paketit = subprocess.check_output(cmd["listaa-asennetut"], shell=True).decode().split()
    except subprocess.CalledProcessError as e:
        log.virhe("Pakettien listaus epäonnistui.")
        log.virhetiedot(e)
        exit(10)

    for paketti in nykyiset_paketit:
        if paketti not in asentaja.paketit:
            poistettavat_paketit.append(paketti)

    if poistettavat_paketit:
        log.info(f"Poistetaan paketit '{' '.join(poistettavat_paketit)}'.")
        try:
            subprocess.run(cmd["poista"].format(" ".join(poistettavat_paketit)), shell=True, check=True)
        except subprocess.CalledProcessError as e:
            log.virhe(f'Pakettien \'{", ".join(poistettavat_paketit)}\' poisto epäonnistui.')
            log.virhetiedot(e)
            exit(16)
    else:
        log.info("Ei paketteja poistettavaksi.")


def _tuhoa_poistetut_tiedostot(nykyiset_tiedostot, luodut_tiedostot):
    poistettiinko_tiedostoja = False

    for tiedosto in nykyiset_tiedostot:
        if tiedosto not in luodut_tiedostot:
            poistettiinko_tiedostoja = True
            log.info(f"Poistetaan asetuslähteestä poistettu tiedosto '{tiedosto}'.")
            try:
                os.remove(tiedosto)
            except OSError as e:
                log.varoitus(f"Asetuslähteestä poistetun tiedoston '{tiedosto}' poisto epäonnistui.")
                log.varoitus("Ehkä tiedosto oli poistettu manuaalisesti.")
                log.virhetiedot(e)

    if poistettiinko_tiedostoja:
        log.info("Ei tiedostoja poistettavaksi.")


def _suorita_deaktivointikomennot(nykyiset_kokonaisuudet):
    deaktivoidut_kokonaisuudet = []

    for kokonaisuus in nykyiset_kokonaisuudet:
        if kokonaisuus not in asentaja.aktiiviset_kokonaisuudet:
            deaktivoidut_kokonaisuudet.append(kokonaisuus)

    if deaktivoidut_kokonaisuudet:
        log.info(f"Deaktivoidaan kokonaisuudet '{' '.join(deaktivoidut_kokonaisuudet)}'.")

        for deaktivoitu_kokonaisuus in deaktivoidut_kokonaisuudet:
            for deaktivointikomento in asentaja.tallennus.lue_lista(f"deaktivointikomennot-{deaktivoitu_kokonaisuus}"):
                log.info(f"Suoritetaan deaktivointikomento '{deaktivointikomento}'.")
                try:
                    subprocess.run(deaktivointikomento, shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    log.varoitus(f"Deaktivointikomennon '{deaktivointikomento}' suorittaminen epäonnistui.")
                    log.virhetiedot(e)
            asentaja.tallennus.poista_lista(f"deaktivointikomennot-{deaktivoitu_kokonaisuus}", salli_virheet=True)
    else:
        log.info("Ei deaktivoitavia kokonaisuuksia.")


def _suorita_aktivointikomennot(suoritetut_aktivointikomennot):
    aikaisemmin_suoritetut_aktivointikomennot = []
    nyt_suoritetut_aktivointikomennot = []

    for komento in asentaja.aktivointikomennot:
        if komento in suoritetut_aktivointikomennot:
            log.info(f"Jätetään jo aikaisemmin suoritettu aktivointikomento '{komento}' suorittamatta.")
            aikaisemmin_suoritetut_aktivointikomennot.append(komento)
        else:
            log.info(f"Suoritetaan uusi aktivointikomento '{komento}'.")
            try:
                subprocess.run(komento, shell=True, check=True)
                nyt_suoritetut_aktivointikomennot.append(komento)
            except subprocess.CalledProcessError as e:
                log.varoitus(f"Aktivointikomennon '{komento}' suorittaminen epäonnistui.")
                log.virhetiedot(e)

    return aikaisemmin_suoritetut_aktivointikomennot + nyt_suoritetut_aktivointikomennot


def _suorita_lopetuskomennot():
    grub_asetusten_sijainti = os.path.join(tiedostojärjestelmän_alku, "boot/grub/grub.cfg")

    try:
        if asentaja.grub.suorita_generoimiskomento:
            log.info("Suoritetaan grub-luomiskomento.")
            subprocess.run(cmd["luo-grub-asetukset"].format(grub_asetusten_sijainti), shell=True, check=True)
        if asentaja.mkinitcpio.suorita_generoimiskomento:
            log.info("Suoritetaan mkinitcpio-luomiskomento.")
            subprocess.run(cmd["generoi-mkinitcpio"], shell=True, check=True)
    except subprocess.CalledProcessError as e:
        log.virhe("Grub tai mkinitcpio -luomiskomentojen suorittaminen epäonnistui.")
        log.virhetiedot(e)
        exit(17)

    for komento in asentaja.lopetuskomennot:
        log.info(f"Suoritetaan lopetuskomento '{komento}'.")
        try:
            subprocess.run(komento, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            log.varoitus(f"Lopetuskomennon '{komento}' suorittaminen epäonnistui.")
            log.virhetiedot(e)

