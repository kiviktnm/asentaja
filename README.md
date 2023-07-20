# Asentaja

Mahdollistaa deklaratiivisen hallinan Arch Linuxille Pythonin avulla.

## Käyttö

### Asenna Arch Linux

Asenna minimaalinen Arch Linux instanssi joko noudattamalla [virallisia asennusohjeita](https://wiki.archlinux.org/title/Installation_guide) tai esimerkiksi archinstall-skriptin avulla. Huolehdi, että asennat Grub2:en bootloader-ohjelmaksi, sillä Asentaja käyttää sitä kernelin parametrien asettamiseen.

Tässä vaiheessa on myös hyvä luoda tavallinen käyttäjä järjestelmän normaaliajoon varsinkin silloin, jos osa tämän käyttäjän tiedostoista on Asentajan hallinnoimia.

### Asentajan tarvitsemat paketit

Asentaja tarvitsee joitain paketteja toimiakseen. [Nämä paketit asentaja myös asentaa itse.](#automaattisesti-asennetut-paketit) Huomaa, että Asentaja omasta tahdostani johtuen jättää sudon asentamatta ja asentaa opendoas-paketin sen sijaan.

Suorita seuraava komento asentaaksesi Asentajan vaatimat paketit.

```
# pacman -S --needed base linux linux-firmware python git opendoas autoconf automake binutils bison debugedit fakeroot flex gcc groff libtool m4 make patch pkgconf texinfo which grub efibootmgr
```

Käytännössä listattuna on perustavanlaatuiset paketit (base, linux, linux-firmware), python, git, opendoas, grub, ja base-devel-pakettiryhmän paketit.

Huomaa, että koska sudoa ei ole asennettu, luo symbolinen linkki doas ja sudo-ohjelman välille.

```
# ln -s $(which doas) /usr/bin/sudo
```

Asenna myös [pikaur](https://github.com/actionless/pikaur)-avustajaohjelma. Asentaja käyttää pikauria rajapintana pacmaniin, eli se asentaa tavallisetkin paketit pikaurin avulla.

### Asentajan asentaminen

Suorita seuraavat komennot:

```
# git clone https://github.com/Windore/asentaja.git /opt/asentaja
# bash /opt/asentaja/bin/asenna-asentaja
```

### Käyttöönotto

Luo kansio, jossa on Python-tiedosto nimeltä `asetukset.py`.
Muokkaa `asetukset.py`-tiedostoa sopivaksi. Seuraava on esimerkki yksinkertaisesta `asetukset.py`-tiedostosta.

```py
import asentaja

# Määrittele vaaditut paketit. Kaikki muut paketit poistetaan. Listaa myös AUR paketit tänne.
# Asentaja asentaa itse osan tarvitsemistaan paketeista.
# Huomaa: Tällä hetkellä pakettiryhmät (package groups) eivät ole mahdollisia asentaa tällä tavalla. Listaa niiden sisältämät paketit erikseen.

asentaja.paketit += [
    # Dokumentaatio-ohjelmat
    "man-pages", "man-db", "tldr",

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
# Huomaa, että Asentaja ei tue symbolisia linkkejä. Jos asentajan lähdetiedostona on symbolinen linkki, asentaja lukee linkin osoittaman tiedoston ja kirjoittaa sen sisällön kohteeseensa.

asentaja.tiedostot["/etc/vconsole.conf"] = asentaja.Tiedosto(sisältö="KEYMAP=fi")

# Oletuksena Asentaja luo tiedostot 'rw-r--r--'-oikeuksin, niin että ne kuuluvat root-käyttäjälle ja -ryhmään. Se on muutettavissa.
asentaja.tiedostot["/home/kk/.bin/hei.sh"] = asentaja.Tiedosto(sisältö="echo Hei!", omistaja="kk", ryhmä="kk", oikeudet=0o744)

# Asentaja lukee lähdetiedostot suhteessa `asetukset.py`-tiedoston kansioon, eli kansioon joka määriteltiin 'asentaja --lähde'-komennolla.
asentaja.tiedostot["/etc/hostname"] = asentaja.Tiedosto(lähde="nimi.txt")

# Kuten tiedostoja Asentaja voi asentaa myös kansioita.
asentaja.kansiot["/home/kk/.bin/"] = asentaja.Kansio(lähde="bin/", omistaja="kk", oikeudet=0o744)

# Määrittele komennot, jotka Asentaja suorittaa päivityksen jälkeen. Huomaa, että komennot suoritetaan root-käyttäjän oikeuksin.
asentaja.lopetuskomennot += [ "locale-gen" ]

# Määrittele komennot, jotka Asentaja suorittaa vain yhden kerran kun ne ensimmäisen kerran määritellään.
asentaja.aktivointikomennot += [ "echo En keksi parempaa esimerkkiä" ]

# Kokonaisuudet on tapa organisoida yhteen liittyviä kokonaisuuksia. Samalla ne mahdollistavat deaktivointikomentojen ja tiedostomuuttujien käytön. Kokonaisuudella on uniikki nimi.
# Deaktivointikomennot ovat komentoja, jotka suoritetaan kun kokonaisuus poistetaan käytöstä.
# Tiedostomuuttujat ovat tekstipätkiä, jotka korvataan *kaikissa* tiedostoissa (ja kansioiden sisältämissä tiedostoissa).
asentaja.kokonaisuudet["esimerkki"] = {
    "paketit": [ "esimerkki" ],
    "palvelut": [ "esimerkki.service" ],
    "lopetuskomennot": [ "esimerkkikomento" ],
    "aktivointikomennot": [ "esimerkkikomento" ],
    "deaktivointikomennot": [ "esimerkkikomento" ],
    "tiedostot": {
        "/etc/esimerkki": asentaja.Tiedosto(sisältö="esimerkki"),
    },
    "kansiot" : {
        "/home/kk/esimerkki/": asentaja.Kansio(lähde="esimerkki/", omistaja="kk"),
    },
    "tiedostomuuttujat": {
        "%PÄÄVÄRI%": "#000000",
    }
}

# Kokonaisuudet pitää aktivoida erikseen. Tällä tavalla voi helposti valita, mitä kokonaisuuksia järjestelmässä käyttää.
asentaja.aktiiviset_kokonaisuudet = [
    "esimerkki",
]

# Määrittele kernelin parametrit.
# Muiden grub asetusten asettaminen tapahtuu myös tämän tiedoston avulla erikseen määriteltyjen asetuksien avulla.
asentaja.grub.kernel_parametrit += [ "quiet", "splash" ]

# Määrittele mkinitcpio moduulit yms.
asentaja.mkinitcpio.modules += [ "nvidia", "nvidia_modeset", "nvidia_uvm", "nvidia_drm" ]

# Kun määrittelee mkinitcpion hookit, on poikkeuksellisesti hyödyllistä määritellä koko lista uudelleen, jotta järjestys on varmasti oikea.
asentaja.mkinitcpio.hooks = [ "base", "udev", "autodetect", "modconf", "kms", "keyboard", "keymap", "consolefont", "block", "filesystems", "fsck" ]

# Sekä grubin, doasin ja mkinitcpion lisäasetukset ovat nähtävillä tiedostoissa src/asentaja/grub.py, src/asentaja/doas.py ja src/asentaja/mkinitcpio.py
```

Tämän jälkeen suorita seuraava komento root-käyttäjän oikeuksin saadaksesi `asetukset.py`-tiedoston mukaisen järjestelmän käyttöösi. Päivityskomento on interaktiivinen, eli se kysyy varmistuksia pakettien poistoista ja asentamisista. Tämä johtuu siitä, että Asentaja kutsuu pikaur-ohjelmaa suoraan.

```
# asentaja --päivitä --lähde polku/asetuskansion/luokse
```

Vain ensimmäisellä kerralla on tarpeellista määrittää Asentajan lähde, sillä asentaja muistaa aikaisemman asetuskansion. Jos kansion sijainti muuttuu, lähde pitää määrittää jälleen uudelleen.

## Päivitykset

### Järjestelmän päivitykset

Päivityskomentoa tulee käyttää jatkossa järjestelmän päivittämiseen ja joka kerta kuin muuttaa `asetukset.py`-tiedostoa (tai sen kutsumia tiedostoja).

```
# asentaja --päivitä
```

Asentajan päivityskomento on hitaampi kuin päivitys pelkästään esim. `pikaur -Syu` komennolla, koska Asentaja suorittaa ylimääräisiä komentoja ja esimerkiksi kirjoittaa tiedostot aina uudelleen. On siis teoriassa mahdollista nopeuttaa päivitystä manuaalisen komennon suorittamisella, mutta tämä ei ole suositeltavaa ja voi johtaa erilaisiin ongelmiin.

Pelkästään tiedostojen päivittäminen onnistuu lisäämällä komentoon argumentin `--vain-tiedostot`. Tämä on käytännöllistä esimerkiksi silloin, kun työskentelee asetustiedostojen parissa.

```
# asentaja --päivitä --vain-tiedostot
```

Huomaa, että jos esimerkiksi `mkinitcpio.conf`-tiedostoa muutetaan, sen vaikutukset eivät tule näkymään.

### Asentajan päivittäminen

Asentaja ei päivitä itseään järjestelmäpäivityksen aikana, vaan sen sijaan Asentajan mukana tulee ohjelma sen itsensä päivittämiseen .

```
# päivitä-asentaja
```

## Asentajan toiminta

Asentaja suorittaa tarvittavat operaatiot seuraavassa järjestyksessä.

1. Päivittää nykyisen järjestelmän
2. Asentaa uudet paketit
3. Luo tiedostot
4. Aktivoi uudet palvelut
5. Deaktivoi poistetut palvelut
6. Poistaa poistetut paketit
7. Tuhoaa poisteut tiedostot
8. Suorittaa deaktivointikomennot.
9. Suorittaa vain kerran suoritettavat aktivointikomennot
10. Suorittaa generoimiskomennot (mkinitcpio, grub), jos grub tai mkinitcpio asetukset ovat muuttuneet.
11. Suorittaa muut lopetuskomennot

## Automaattisesti asennetut paketit

Asentaja asentaa automaattisesti itse tarvitsemansa paketit sekä paketit minimaalisen Arch Linuxin ylläpitoon. Sen lisäksi Asentaja huolehtii itse grub, mkinitcpio ja doas -ohjelmien asetuksien säätämisestä, jolloin niitä ei tarvitse tehdä *täysin* manuaalisesti (kts. esimerkkitiedosto).

- base
- linux
- linux-firmware
- python
- git
- opendoas
- autoconf
- automake
- binutils
- bison
- debugedit
- fakeroot
- flex
- gcc
- groff
- libtool
- m4
- make
- patch
- pkgconf
- texinfo
- which
- grub
- efibootmgr
- pikaur (AUR)

