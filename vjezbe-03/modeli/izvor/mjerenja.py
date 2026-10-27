"""Konačna mjerenja za blokove interakcije (vježbe 3), NetLogo 7.0.4 headless.

Pokretanje:  python -I mjerenja.py [b1 b2 b3 b4 slike]   (bez argumenata: sve)
Izlaz u ../mjerenja/: CSV svakog eksperimenta, rezultati.json, rezultati.md, slike/*.png
"""
import io, json, os, statistics as st, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mjeri import pokreni, xml_eksperiment, MJERENJA

SLIKE = os.path.join(MJERENJA, "slike")
os.makedirs(SLIKE, exist_ok=True)
JSON = os.path.join(MJERENJA, "rezultati.json")
rez = json.load(open(JSON, encoding="utf-8")) if os.path.exists(JSON) else {}
koji = sys.argv[1:] or ["b1", "b2", "b3", "b4", "slike"]


def sazetak(v):
    v = sorted(v)
    return {"n": len(v), "sred": round(st.mean(v), 4), "med": round(st.median(v), 4),
            "min": round(v[0], 4), "max": round(v[-1], 4),
            "iznad_0_9": sum(1 for a in v if a > 0.9), "ispod_0_1": sum(1 for a in v if a < 0.1)}

def grupe(redovi, kljucevi, mjera, step=None):
    g = collections.defaultdict(list)
    for r in redovi:
        if step is None or r["[step]"] == str(step):
            g[" | ".join(f"{k}={r[k]}" for k in kljucevi)].append(float(r[mjera]))
    return {k: sazetak(v) for k, v in sorted(g.items(), key=lambda kv: kv[0])}

def zadnji(redovi):
    """Za runMetricsEveryStep=true: zadnji red svakog pokretanja."""
    z = {}
    for r in redovi:
        z[r["[run number]"]] = r
    return list(z.values())

PRAGOVI = [0.1, 0.2, 0.3, 0.5, 1, 2]

if "b1" in koji:
    r = pokreni("v03-blok1-povjerenje.nlogox", "m-grupe",
                xml_eksperiment("m-grupe", 10, 500, ["broj-grupa", "udio-za"],
                                [("prag", PRAGOVI), ("mediji-rade?", ["false"])], svaki_korak=True))
    rez["b1_grupe_150"] = grupe(r, ["prag"], "broj-grupa", 150)
    rez["b1_grupe_500"] = grupe(r, ["prag"], "broj-grupa", 500)
    rez["b1_udio_za_bez_medija_500"] = grupe(r, ["prag"], "udio-za", 500)
    r = pokreni("v03-blok1-povjerenje.nlogox", "m-mediji",
                xml_eksperiment("m-mediji", 10, 150, ["udio-za"],
                                [("prag", PRAGOVI), ("mediji-rade?", ["true"])], svaki_korak=True))
    rez["b1_udio_za_mediji_0"] = grupe(r, ["prag"], "udio-za", 0)
    rez["b1_udio_za_mediji_150"] = grupe(r, ["prag"], "udio-za", 150)
    print("b1 gotov")

if "b2" in koji:
    r = pokreni("v03-blok2-prag.nlogox", "m-rasipanje",
                xml_eksperiment("m-rasipanje", 200, 200, ["udio-aktivnih", "ticks"],
                                [("prosjek-praga", [0.3]), ("rasipanje-praga", [0, 0.02, 0.04, 0.05, 0.06, 0.08, 0.1, 0.15, 0.2, 0.3]),
                                 ("pokretaci", [10])]))
    rez["b2_rasipanje"] = grupe(r, ["rasipanje-praga"], "udio-aktivnih")
    rez["b2_rasipanje_ticks"] = grupe(r, ["rasipanje-praga"], "ticks")
    r = pokreni("v03-blok2-prag.nlogox", "m-pokretaci",
                xml_eksperiment("m-pokretaci", 200, 200, ["udio-aktivnih"],
                                [("prosjek-praga", [0.3]), ("rasipanje-praga", [0.05]), ("pokretaci", [5, 10, 20, 40, 80])]))
    rez["b2_pokretaci"] = grupe(r, ["pokretaci"], "udio-aktivnih")
    r = pokreni("v03-blok2-prag.nlogox", "m-prosjek",
                xml_eksperiment("m-prosjek", 200, 200, ["udio-aktivnih"],
                                [("prosjek-praga", [0.2, 0.25, 0.3, 0.35, 0.4]), ("rasipanje-praga", [0.1]), ("pokretaci", [10])]))
    rez["b2_prosjek"] = grupe(r, ["prosjek-praga"], "udio-aktivnih")
    print("b2 gotov")

if "b3" in koji:
    r = pokreni("v03-blok3-mreza.nlogox", "m-daleke",
                xml_eksperiment("m-daleke", 20, 500, ["udio-za", "prosjecan-stav", "mean [ count link-neighbors ] of ljudi"],
                                [("udio-dalekih-veza", [0, 0.05, 0.2, 1]), ("broj-medija", [2])], svaki_korak=True))
    for t in (0, 150, 500):
        rez[f"b3_udio_za_{t}"] = grupe(r, ["udio-dalekih-veza"], "udio-za", t)
    rez["b3_poznanika"] = grupe(r, ["udio-dalekih-veza"], "mean [ count link-neighbors ] of ljudi", 0)
    print("b3 gotov")

if "b4" in koji:
    r = pokreni("v03-blok4-preseljenje.nlogox", "m-trazeni",
                xml_eksperiment("m-trazeni", 10, 500, ["prosjecno-slicnih", "udio-nezadovoljnih", "ticks"],
                                [("trazeni-udio-slicnih", [0.2, 0.3, 0.4, 0.5, 0.6, 0.75]), ("gustina", [0.7])], svaki_korak=True))
    rez["b4_slicnih_pocetak"] = grupe(r, ["trazeni-udio-slicnih"], "prosjecno-slicnih", 0)
    kraj = zadnji(r)
    rez["b4_slicnih_kraj"] = grupe(kraj, ["trazeni-udio-slicnih"], "prosjecno-slicnih")
    rez["b4_nezadovoljnih_kraj"] = grupe(kraj, ["trazeni-udio-slicnih"], "udio-nezadovoljnih")
    rez["b4_ticks_kraj"] = grupe(kraj, ["trazeni-udio-slicnih"], "ticks")
    print("b4 gotov")

if "t3" in koji:
    # Tačka 3 zadatka v02: jednosmjerno (v02-model-stav) i obostrano (blok 1 s pragom 2 = uvijek razgovaraju)
    for ime, model, dodatno in (("jednosmjerno", "../../v02/modeli/v02-model-stav.nlogox", []),
                                ("obostrano", "v03-blok1-povjerenje.nlogox", [("prag", [2])])):
        r = pokreni(model, f"t3-{ime}",
                    xml_eksperiment(f"t3-{ime}", 20, 150, ["udio-za"], [("mediji-rade?", ["false", "true"])] + dodatno,
                                    svaki_korak=True))
        for t in (25, 150):
            rez[f"t3_{ime}_{t}"] = grupe(r, ["mediji-rade?"], "udio-za", t)
    print("t3 gotov")

if "slike" in koji:
    # Jedno pokretanje po slici, s fiksnim random-seed; broj sjemena ide u potpis slike.
    def slika(model, ime, seed, ticks, vrijednosti, metrike=()):
        put = os.path.join(SLIKE, f"{ime}.png").replace("\\", "/")
        izvoz = f'export-view "{put}"'
        if ticks == 0:   # timeLimit="0" znači bez ograničenja, pa se slika uzima odmah poslije setup
            postavke = dict(setup=f"random-seed {seed} setup {izvoz}", final="", svaki_korak=True)
            ticks = 1
        else:
            postavke = dict(setup=f"random-seed {seed} setup", final=izvoz)
        r = pokreni(model, f"s-{ime}",
                    xml_eksperiment(f"s-{ime}", 1, ticks, list(metrike) or ["ticks"], vrijednosti, **postavke))
        return r[0] if postavke["final"] == "" else r[-1]
    s = {}
    for prag in (0.2, 0.5, 2):
        red = slika("v03-blok1-povjerenje.nlogox", f"b1-prag-{prag}", 1, 500,
                    [("prag", [prag]), ("mediji-rade?", ["false"])], ["broj-grupa", "udio-za", "sort [ stav ] of ljudi"])
        s[f"b1-prag-{prag}"] = {"seed": 1, "ticks": 500, "broj-grupa": red["broj-grupa"], "udio-za": red["udio-za"],
                                "stavovi": [float(x) for x in red["sort [ stav ] of ljudi"].strip("[]").split()]}
    for ras, t in ((0.05, 200), (0.1, 3), (0.1, 6), (0.1, 20), (0.1, 30), (0.1, 40), (0.1, 200)):
        red = slika("v03-blok2-prag.nlogox", f"b2-ras-{ras}-t{t}", 3, t,
                    [("prosjek-praga", [0.3]), ("rasipanje-praga", [ras]), ("pokretaci", [10])], ["udio-aktivnih", "ticks"])
        s[f"b2-ras-{ras}-t{t}"] = {"seed": 3, "udio-aktivnih": red["udio-aktivnih"], "ticks": red["ticks"]}
    for p in (0, 0.2):
        red = slika("v03-blok3-mreza.nlogox", f"b3-daleke-{p}", 2, 500,
                    [("udio-dalekih-veza", [p]), ("broj-medija", [2])], ["udio-za"])
        s[f"b3-daleke-{p}"] = {"seed": 2, "ticks": 500, "udio-za": red["udio-za"]}
    for t in (0, 500):
        red = slika("v03-blok4-preseljenje.nlogox", f"b4-t{t}", 4, t,
                    [("trazeni-udio-slicnih", [0.3]), ("gustina", [0.7])], ["prosjecno-slicnih", "ticks"])
        s[f"b4-t{t}"] = {"seed": 4, "prosjecno-slicnih": red["prosjecno-slicnih"], "ticks": red["ticks"]}
    rez["slike"] = s
    print("slike gotove")

json.dump(rez, open(JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- čitljiv sažetak ----------
L = ["# Mjerenja blokova interakcije (vježbe 3)", "",
     "NetLogo 7.0.4 headless, skript `izvor/mjerenja.py`. Zadane vrijednosti klizača osim navedenih.",
     "Kolone: broj pokretanja, prosjek, medijan, najmanje, najviše; za udjele i broj pokretanja iznad 0,9 i ispod 0,1.", ""]
for kljuc, tab in rez.items():
    if kljuc == "slike":
        continue
    L += [f"## {kljuc}", "", "| uslov | n | prosjek | medijan | min | max | >0,9 | <0,1 |", "|---|---|---|---|---|---|---|---|"]
    for uslov, x in tab.items():
        L.append(f"| {uslov} | {x['n']} | {x['sred']} | {x['med']} | {x['min']} | {x['max']} | {x['iznad_0_9']} | {x['ispod_0_1']} |")
    L.append("")
if "slike" in rez:
    L += ["## slike (jedno pokretanje, fiksni random-seed)", ""]
    for k, v in rez["slike"].items():
        L.append(f"- `slike/{k}.png`: " + ", ".join(f"{a}={b}" for a, b in v.items() if a != "stavovi"))
io.open(os.path.join(MJERENJA, "rezultati.md"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
print("rezultati.md napisan")
