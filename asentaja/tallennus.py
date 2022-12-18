# Kaikki Asentajan omat tiedot tallennetaan listoina, koska se on helpoin ja yleistettävin tapa säilöä tietoa.

import os
import asentaja.asetukset


_sijainti = "var/lib/asentaja/"


def lue_lista(nimi, oletus=[], salli_virheet=True):
    tiedosto = os.path.join(asentaja.asetukset.tiedostojärjestelmän_alku, _sijainti, nimi)
    try:
        with open(tiedosto, "rt") as t:
            return t.read().split()
    except:
        if salli_virheet:
            return oletus
        else:
            print(f"Asentajan oman tiedoston '{tiedosto}' luku epäonnistui.")
            raise


def kirjoita_lista(nimi, sisältö=[], salli_virheet=False):
    kansio = os.path.join(asentaja.asetukset.tiedostojärjestelmän_alku, _sijainti)
    tiedosto = os.path.join(kansio, nimi)
    try:
        os.makedirs(kansio, exist_ok=True)
        with open(tiedosto, "wt") as t:
            t.write("\n".join(sisältö))
    except:
        if not salli_virheet:
            print(f"Asentajan oman tiedoston '{tiedosto}' kirjoitus epäonnistui.")
            raise

