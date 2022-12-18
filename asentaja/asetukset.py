
komennot: dict[str, str] = {}
komennot["päivitä"] = "pikaur -Syu"
komennot["asenna"] = "pikaur -S {}"
komennot["poista"] = "pikaur -Rs {}"
komennot["listaa-asennetut"] = "pikaur -Qe"
komennot["aktivoi-palvelu"] = "systemctl enable {}"
komennot["deaktivoi-palvelu"] = "systemctl disable {}"
komennot["luo-grub-asetukset"] = "grub-mkconfig -o {}"
komennot["generoi-mkinitcpio"] = "mkinitcpio -P"

tiedostojärjestelmän_alku = "/"

