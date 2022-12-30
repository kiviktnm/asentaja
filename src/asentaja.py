#!/usr/bin/env python

import argparse
import sys
import os

import asentaja.main
import asentaja.tallennus

import asentaja.logger as log


def main():
    parser = argparse.ArgumentParser(
            prog="asentaja",
            description="Ohjelma Arch Linuxin deklaratiiviseen hallintaan.")

    parser.add_argument("--lähde", help="asetuskansion sijainti, arvo tallennetaan tulevia ajokertoja varten")
    parser.add_argument("--informatiivinen", action="store_true", help="näytä kaikki viestit, arvo tallennetaan tulevia ajokertoja varten")
    parser.add_argument("--hiljainen", action="store_true", help="näytä vain tärkeät viestit, arvo tallennetaan tulevia ajokertoja varten")
    parser.add_argument("--ei-root", action="store_true", help="salli ohjelman suorittaminen tavallisena käyttäjänä")
    parser.add_argument("--päivitä", action="store_true", help="päivitä järjestelmä asetuskansion mukaisesti")
    parser.add_argument("--vain-tiedostot", action="store_true", help="Asentaja muuttaa vain järjestelmän tiedostoja")

    args = parser.parse_args()

    # Hiljainen on ensisijainen suhteessa informatiivinen-vaihtoehtoon.
    if args.hiljainen:
        log.informatiivinen = False
    elif args.informatiivinen:
        log.informatiivinen = True
    else:
        # Jos mitään ei ole määritelty, lue aikaisemmin tallennettu arvo, jos se on olemassa
        # Jos arvoa ei ole oletus on True
        log.informatiivinen = asentaja.tallennus.lue_lista("informatiivinen", salli_virheet=True, oletus=[ "True" ])[0] == "True"

    # Kirjoita informatiivinen muuttuja talteen
    asentaja.tallennus.kirjoita_lista("informatiivinen", sisältö=[ str(log.informatiivinen) ], salli_virheet=True)

    if not args.ei_root:
        if not varmista_root():
            log.virhe("Suorita ohjelma root-käyttäjänä.")
            exit(1)

    asetuslähde = ""
    if args.lähde:
        asetuslähde = args.lähde
    else:
        log.info("Asetuslähdettä ei annettu. Luetaan tallennettu arvo.")
        # Oletetaan, että kukaan ei ole manuaalisesti muokannut tiedostoa, jolloin jos se on olemassa, siellä on yksi listan jäsen joka sisältää asetuslähteen.
        asetuslähde = asentaja.tallennus.lue_lista("asetuslähde", salli_virheet=False)[0]

    if not os.path.isdir(asetuslähde):
        log.virhe(f"Asetuslähteen sijainti '{asetuslähde}' on virheellinen.")
        exit(2)

    log.info(f"Nykyinen asetuslähde on '{asetuslähde}'.")

    asentaja.tallennus.kirjoita_lista("asetuslähde", sisältö=[asetuslähde])

    if args.päivitä:
        päivitä(asetuslähde, args.vain_tiedostot)
    else:
        log.info("Päivityskomentoa ei annettu. Jos haluat, että järjestelmä päivitetään, lisää '--päivitä'-vaihtoehto komennon perään.")


def varmista_root():
    return os.geteuid() == 0


def päivitä(asetuslähde, vain_tiedostot):
    # Vaihdetaan nykyinen kansio asetuslähteeseen, jolloin asetuslähteen tiedostot voivat olla suhteellisia asetuslähteeseen.
    os.chdir(asetuslähde)

    # Sallitaan Python-moduulien tuominen nykyisestä kansiosta eli asetuslähteestä.
    sys.path.append(".")

    # Varmistetaan onko asetukset.py tiedosto olemassa
    if not os.path.isfile("asetukset.py"):
        log.virhe("Asetuskansiossa ei ole 'asetukset.py'-tiedostoa.")
        exit(3)

    # Tämä suorittaa asetukset.py tiedoston, jonka pitäisi määritellä asennettava järjestelmä.
    import asetukset

    asentaja.main.päivitys(vain_tiedostot)


if __name__ == "__main__":
    main()

