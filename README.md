# Asentaja

Mahdollistaa deklaratiivisen hallinan Arch Linuxille Pythonin avulla.

## Käyttö

### Asenna Arch Linux

Asenna minimaalinen Arch Linux instanssi joko noudattamalla [virallisia asennusohjeita](https://wiki.archlinux.org/title/Installation_guide) tai esimerkiksi `archinstall`-skriptin avulla.
Huolehdi, että asennat Grub2:en bootloader-ohjelmaksi, sillä Asentaja käyttää sitä kernelin parametrien asettamiseen.

Lisäksi asenna `python`, `git` ja `base-devel` sekä jokin tekstieditori kuten `neovim`.

### Asentajan asentaminen

TODO: Rakenna automaattinen asennusohjelma ym.

Asentaja asentaa automaattisesti myös [pikaur](https://github.com/actionless/pikaur)-avustajaohjelman, joka mahdollistaa AUR ohjelmien asentamisen.
Asentaja käyttää pikauria rajapintana pacmaniin, eli se asentaa tavallisetkin paketit pikaurin avulla.

### Käyttöönotto

Luo kansio, jossa on Python-tiedosto nimeltä `asetukset.py`.

Aseta tämä kansio Asentajan lähteeksi. Suorita komenta root-käyttäjän oikeuksin.

```
# asentaja seuraa polku/kansion/luokse
```

Jos kansion sijainti muuttuu, sama komento pitää suorittaa uudestaan.

Muokkaa `asetukset.py`-tiedostoa sopivaksi. Seuraava on esimerkki yksinkertaisesta `asetukset.py`-tiedostosta.

```py
import asentaja

# Määrittele vaaditut paketit. Kaikki muut paketit poistetaan. Listaa myös AUR paketit tänne.
# Asentaja asentaa itse `python` ja `git` paketit, koska se tarvitsee niitä toimiakseen.
# Huomaa: Tällä hetkellä pakettiryhmät (package groups) eivät ole mahdollisia asentaa tällä tavalla. Listaa niiden sisältämät paketit erikseen.

asentaja.paketit += [
    # Vaaditut paketit
    "base", "linux", "linux-firmware",

    # Dokumentaatio-ohjelmat
    "man-pages", "man-db", "texinfo", "tldr",

    # Verkko-ohjelma
    "networkmanager",

    # Tekstinmuokkausohjelma
    "neovim",
]

# Määrittele palvelut (services), jotka otetaan käyttöön.
# Huomaa, että asentaja ei käynnistä palveluita (start) vain pelkästään aktivoi ne (enable).
# Asentaja hallinnoi pelkästään täällä määriteltyjä palveluita, jolloin muualla aktivoidut / deaktivoidut palvelut eivät vaikuta Asentajan toimintaan.

asentaja.palvelut += [ "NetworkManager.service" ]

# Määrittele tiedostot, joita Asentaja ylläpitää.
# Jos täällä määritelty tiedosto poistetaan täältä, tiedosto poistetaan myös määränpäästään.
# Asentaja luo automaattisesti tarvittavat kansiot, muttei myöhemmin poista niitä.

# On siis teoriassa mahdollista nopeuttaa päivitystä manuaalisen komennon suorittamisella, mutta tämä ei ole suositeltavaa.
asentaja.tiedostot["/etc/vconsole.conf"] = asentaja.Tiedosto(sisältö="KEYMAP=fi")

# Oletuksena Asentaja luo tiedostot 'rw-r--r--'-oikeuksin, niin että ne kuuluvat root-käyttäjälle ja -ryhmään. Se on muutettavissa.
asentaja.tiedostot["/home/kk/.bin/hei.sh"] = asentaja.Tiedosto(sisältö="echo Hei!", omistaja="kk", ryhmä="kk", oikeudet=0o744)

# Asentaja lukee lähdetiedostot suhteessa `asetukset.py`-tiedoston kansioon, eli kansioon joka määriteltiin 'asentaja seuraa'-komennolla.
asentaja.tiedostot["/etc/hostname"] = asentaja.Tiedosto(lähde="nimi.txt")

# Määrittele kernelin parametrit. Edellyttää Grub2-ohjelmaa.
asentaja.kernel_parametrit += [ "quiet", "splash" ]

# Grub2 asetusten asettaminen tapahtuu myös tämän tiedoston avulla erikseen määriteltyjen asetuksien avulla.
# TODO: Lisää nämä asetukset tähän esimerkkitiedostoon.

# Määrittele mkinitcpio moduulit yms.
asentaja.mkinitcpio.modules += [ "nvidia", "nvidia_modeset", "nvidia_uvm", "nvidia_drm" ]
```

Tämän jälkeen suorita seuraava komento root-käyttäjän oikeuksin saadaksesi `asetukset.py`-tiedoston mukaisen järjestelmän käyttöösi.
Päivityskomento on interaktiivinen, eli se kysyy varmistuksia pakettien poistoista ja asentamisista. Tämä johtuu siitä, että Asentaja kutsuu pikaur-ohjelmaa suoraan.

```
# asentaja päivitä
```

Samaa komentoa tulee käyttää jatkossa järjestelmän päivittämiseen ja joka kerta kuin muuttaa `asetukset.py`-tiedostoa (tai sen kutsumia tiedostoja).

Asentajan päivityskomento on hitaampi kuin päivitys pelkästään esim. `pikaur -Syu` komennolla, koska Asentaja uudelleenrakentaa Grub-asetukset ym. joka päivityksen yhteydessä varmuuden vuoksi.
On siis teoriassa mahdollista nopeuttaa päivitystä manuaalisen komennon suorittamisella, mutta tämä ei ole suositeltavaa.

