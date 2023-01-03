# Kaikki Asentajan omat tiedot tallennetaan listoina, koska se on helpoin ja yleistettävin tapa säilöä tietoa.

import os
import asentaja.asetukset

import asentaja.logger as log


_sijainti = "var/lib/asentaja/"


def lue_lista(nimi, oletus=[], salli_virheet=True):
    tiedosto = os.path.join(asentaja.asetukset.tiedostojärjestelmän_alku, _sijainti, nimi)
    try:
        with open(tiedosto, "rt") as t:
            return t.read().split("\n")
    except OSError as e:
        if salli_virheet:
            log.varoitus(f"Asentajan oman tiedoston '{tiedosto}' luku epäonnistui.")
            log.varoitus(f"Oletetaan, että tiedostoa ei ole vielä luotu.")
            return oletus
        else:
            log.virhe(f"Asentajan oman tiedoston '{tiedosto}' luku epäonnistui.")
            log.virhetiedot(e)
            exit(20)


def kirjoita_lista(nimi, sisältö=[], salli_virheet=False):
    kansio = os.path.join(asentaja.asetukset.tiedostojärjestelmän_alku, _sijainti)
    tiedosto = os.path.join(kansio, nimi)
    try:
        os.makedirs(kansio, exist_ok=True)
        with open(tiedosto, "wt") as t:
            t.write("\n".join(sisältö))
    except OSError as e:
        if salli_virheet:
            log.varoitus(f"Asentajan oman tiedoston '{tiedosto}' kirjoitus epäonnistui.")
            log.varoitus(f"Oletetaan, että virhe on merkityksetön.")
        else:
            log.virhe(f"Asentajan oman tiedoston '{tiedosto}' kirjoitus epäonnistui.")
            log.virhetiedot(e)
            exit(21)

