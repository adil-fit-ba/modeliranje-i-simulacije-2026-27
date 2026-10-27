"""Pravi ZIP s materijalima vježbi 3 za studente: nastava/v03/MiS-vjezbe-03-v3.zip (verzija 3, 27.10.2026.).

Raspored u ZIP-u je ravan: sadržaj mape v03 je u korijenu, a modeli s vježbi 2 su u modeli/ uz modele vježbi 3.
Linkovi između stranica ostaju ispravni, jer su relativni unutar v03 (blokovi/, netlogo-web/, modeli/).
- v03: sve osim nastavničkih dokumenata (prijedlog časa, vodič, obavijest, zabilješke), izvora prezentacije
  (deck-izvor/, izvor-html/), snimka časa i C# varijante stranice (dodatni materijal uz WASM projekat);
- modeli/: uz modele vježbi 3 i model stava i zadatak s vježbi 2 (prezentacija ih koristi uživo);
- materijali/: samo C# projekat netlogo-kroz-csharp, bez .vs, bin, obj i .csproj.user (WASM projekat se ne dijeli);
- PROCITAJ-ME.txt na vrhu.
Putevi u kopijama README fajlova prilagođeni su ovom rasporedu (IZMJENE).

Pokretanje: python -I napravi_zip.py
"""
import fnmatch
import pathlib
import re
import zipfile

V03 = pathlib.Path(__file__).resolve().parents[2]
NASTAVA = V03.parent
CILJ = V03 / "MiS-vjezbe-03-v3.zip"
KORIJEN = "MiS-vjezbe-03-v3"

IZVORI = [   # (odredište u ZIP-u, izvor, obrasci koji se izostavljaju); "" = korijen ZIP-a
    ("", V03, ["v03-prijedlog-casa.md", "v03-vodic-za-vjezbanje.md", "v03-obavijest.md",
               "v03-zabiljeske.md", "deck-izvor/*", "izvor-html/*",
               # C# varijanta stranice: dodatni materijal uz WASM projekat, ne dijeli se
               "v03-blokovi-interakcije-csharp.html", "*.zip", "*__pycache__*", "*.pyc", "~$*",
               # snimak časa, zvuk, transkript i kadrovi
               "MIS-v03-*", "*.mp4", "*.mp3", "*.wav", "*.vtt", "kadrovi/*"]),
    ("modeli", NASTAVA / "v02" / "modeli", None),
    ("materijali/netlogo-kroz-csharp", NASTAVA / "materijali" / "netlogo-kroz-csharp",
     [".vs/*", "bin/*", "obj/*", "*.csproj.user"]),
]
# izvori iz kojih ide samo nabrojano (obrasci relativno na izvor)
SAMO = {
    NASTAVA / "v02" / "modeli": ["v02-model-stav.nlogox", "v02-zadatak.nlogox"],
}

# izmjene u kopijama: veza na vodič (samo za nastavnike) i putevi prilagođeni ravnom rasporedu
IZMJENE = {
    "modeli/README.md": [
        (r"\s*\(vidi\s+`\.\./v03-vodic-za-vjezbanje\.md`, ispravka 24\.10\.\)", ""),
        (r"`\.\./\.\./v02/modeli/v02-model-stav\.nlogox`", "`v02-model-stav.nlogox` (u ovoj mapi)"),
        (r"`\.\./\.\./materijali/netlogo-kroz-csharp/Blokovi/`", "`../materijali/netlogo-kroz-csharp/Blokovi/`"),
    ],
    "materijali/netlogo-kroz-csharp/README.md": [
        (r"`nastava/v03/modeli/`", "`../../modeli/`"),
    ],
}

PROCITAJ = """\
Modeliranje i simulacije, vježbe 3 (24.10.2026.): interakcije
==============================================================
Verzija 3 (27.10.2026.):
- prezentacija s vježbi i kao web stranica: prezentacije/v03-interakcije.html (krive u dijelu
  „Rezultat“ su sada prosjek 20 pokretanja, umjesto 5);
- ujednačen izraz „web preglednik“ u tekstu stranica.

Verzija 2 (27.10.2026.), s ispravkama nakon časa:
- primjer „Jedno susjedstvo, s brojevima“ u bloku 4 sada radi;
- obrazac „Model na papiru“ na stranici v03-blokovi-interakcije.html ispravno je prikazan;
- tekst stranica jezički je dotjeran;
- raspored je jednostavniji: modeli s vježbi 2 su u mapi modeli/, uz modele vježbi 3.

ZIP treba raspakovati prije otvaranja; linkovi između stranica rade samo kad su fajlovi u ovim mapama.

- prezentacije/v03-interakcije.html: prezentacija s vježbi kao web stranica (strelice, „Čitanje“,
  cijeli ekran tipkom F); v03-interakcije.pdf i .pptx su ista prezentacija u ranijem obliku.
- v03-blokovi-interakcije.html: šest blokova interakcije sa simulacijama, mjerenjima, kodom u NetLogu
  i C# i obrascem za model na papiru. Otvara se dvoklikom i radi bez interneta.
- blokovi/: kratka prezentacija za svaki blok. Kroz slajdove se ide strelicama ili prevlačenjem;
  „Čitanje“ prikazuje sve slajdove jedan ispod drugog.
- netlogo-web/: isti modeli u NetLogo Webu, pravom NetLogu u web pregledniku, bez instalacije i bez
  interneta. Fajl ima oko 5 MB, pa se otvara nekoliko sekundi.
- modeli/: modeli za NetLogo 7.0.4 (.nlogox) s BehaviorSpace eksperimentima, uz model stava
  (v02-model-stav.nlogox) i zadatak (v02-zadatak.nlogox) s vježbi 2. U modeli/mjerenja/ su sva mjerenja
  iz materijala, a u modeli/izvor/ skripte kojima su napravljeni modeli, mjerenja i stranice.
- materijali/netlogo-kroz-csharp/: C# projekat koji pokazuje kako NetLogo radi „ispod haube“. Treba
  .NET SDK 8 ili noviji; upute su u README.md.

Simulacije na stranicama su ilustracija: isti kod je prepisan u JavaScript. Brojke u tekstu i na
grafikonima su iz NetLoga, 10–200 pokretanja po vrijednosti.
"""


def izostavi(rel, obrasci):
    return any(fnmatch.fnmatch(rel, o) or fnmatch.fnmatch(pathlib.PurePosixPath(rel).name, o)
               for o in obrasci or [])


def fajlovi():
    for odrediste, izvor, obrasci in IZVORI:
        for put in sorted(izvor.rglob("*")):
            rel = put.relative_to(izvor).as_posix()
            if not put.is_file():
                continue
            ime = f"{odrediste}/{rel}" if odrediste else rel
            if izvor in SAMO:
                if any(fnmatch.fnmatch(rel, o) for o in SAMO[izvor]):
                    yield ime, put
            elif not izostavi(rel, obrasci):
                yield ime, put


def main():
    upotrijebljene, imena = set(), set()
    with zipfile.ZipFile(CILJ, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr(f"{KORIJEN}/PROCITAJ-ME.txt", PROCITAJ.replace("\n", "\r\n").encode("utf-8-sig"))
        for ime, put in fajlovi():
            assert ime not in imena, f"isto ime u ZIP-u: {ime}"
            imena.add(ime)
            if ime in IZMJENE:
                tekst = put.read_text(encoding="utf-8")
                for obrazac, zamjena in IZMJENE[ime]:
                    tekst, n = re.subn(obrazac, zamjena, tekst)
                    assert n == 1, (ime, obrazac, n)
                upotrijebljene.add(ime)
                z.writestr(f"{KORIJEN}/{ime}", tekst.encode("utf-8"))
            else:
                z.write(put, f"{KORIJEN}/{ime}")
    assert upotrijebljene == set(IZMJENE), set(IZMJENE) - upotrijebljene
    print(f"{CILJ}: {len(imena) + 1} fajlova, {CILJ.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
