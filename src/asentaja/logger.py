_punainen_prefix = "\033[91m"
_keltainen_prefix = "\033[93m"
_sininen_prefix = "\033[96m" 
_harmaa_prefix = "\033[2m"
_yleinen_suffix = "\033[m"


informatiivinen = True


def info(viesti):
    if informatiivinen:
        print(f"{_sininen_prefix}INFO{_yleinen_suffix}:     {viesti}")


def varoitus(viesti):
    print(f"{_keltainen_prefix}VAROITUS{_yleinen_suffix}: {viesti}")


def virhe(viesti):
    print(f"{_punainen_prefix}VIRHE{_yleinen_suffix}:    {viesti}")


def virhetiedot(virhe):
    print(f"\n{_harmaa_prefix}{virhe}{_yleinen_suffix}\n")

