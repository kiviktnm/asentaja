#!/usr/bin/env python

import argparse
import sys
import os

import asentaja.main
import asentaja.tallennus


def varmista_root():
    return os.geteuid() == 0


def päivitä(asetuslähde):
    if not os.path.isdir(asetuslähde):
        print(f"Virheellinen asetuskansion sijainti '{asetuslähde}'.")
        exit(2)

    asentaja.tallennus.kirjoita_lista("asetuslähde", sisältö=[asetuslähde])

    # Vaihdetaan nykyinen kansio asetuslähteeseen, jolloin asetuslähteen tiedostot voivat olla suhteellisia asetuslähteeseen.
    os.chdir(asetuslähde)

    # Sallitaan Python-moduulien tuominen nykyisestä kansiosta eli asetuslähteestä.
    sys.path.append(".")

    # Varmistetaan onko asetukset.py tiedosto olemassa
    if not os.path.isfile("asetukset.py"):
        print("Asetuskansiossa ei ole 'asetukset.py'-tiedostoa.")
        exit(2)

    # Tämä suorittaa asetukset.py tiedoston, jonka pitäisi määritellä asennettava järjestelmä.
    import asetukset

    asentaja.main.päivitys()


def main():
    parser = argparse.ArgumentParser(
            prog="asentaja",
            description="Ohjelma Arch Linuxin deklaratiiviseen hallintaan.")

    parser.add_argument("--lähde", help="asetuskansion sijainti, oletus on edellinen annettu sijainti")
    parser.add_argument("--ei-root", action="store_true", help="salli ohjelman suorittaminen tavallisena käyttäjänä")
    parser.add_argument("--päivitä", action="store_true", help="päivitä järjestelmä asetuskansion mukaisesti")

    args = parser.parse_args()

    if not args.ei_root:
        if not varmista_root():
            print("Suorita ohjelma root-käyttäjänä.")
            exit(1)

    asetuslähde = ""
    if args.lähde:
        asetuslähde = args.lähde
    else:
        # Oletetaan, että kukaan ei ole manuaalisesti muokannut tiedostoa, jolloin jos se on olemassa, siellä on yksi listan jäsen joka sisältää asetuslähteen.
        asetuslähde = asentaja.tallennus.lue_lista("asetuslähde", salli_virheet=False)[0]

    if args.päivitä:
        päivitä(asetuslähde)


if __name__ == "__main__":
    main()

