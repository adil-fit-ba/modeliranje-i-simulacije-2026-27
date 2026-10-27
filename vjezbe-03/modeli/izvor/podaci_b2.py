"""Podaci za mini-prezentaciju bloka 2: zapis sale krug po krug iz pravih NetLogo pokretanja (fiksni random-seed).

Pokretanje:  python -I podaci_b2.py
Izlaz:       ../mjerenja/podaci-b2.json
  { "sala": 31, "zapisi": [ { "kljuc", "rasipanje", "seed", "prag": [961 × prag·1000],
                               "ustao": [961 × krug u kojem je ustao, −1 = nikad], "krugova", "udio_kraj" } ] }
Redoslijed mjesta je `sort patches`: red po red odozgo, u redu slijeva nadesno.
"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mjeri import pokreni, xml_eksperiment, MJERENJA

MODEL = "v03-blok2-prag.nlogox"
AKT = "map [ p -> [ ifelse-value aktivan? [ 1 ] [ 0 ] ] of one-of ljudi-on p ] sort patches"
PRAG = "map [ p -> round (1000 * [ moj-prag ] of one-of ljudi-on p) ] sort patches"

def zapis(kljuc, ras, seed):
    x = xml_eksperiment(f"p2-{kljuc}", 1, 200, [AKT, PRAG, "udio-aktivnih"],
                        [("prosjek-praga", [0.3]), ("rasipanje-praga", [ras]), ("pokretaci", [10])],
                        svaki_korak=True, setup=f"random-seed {seed} setup")
    redovi = pokreni(MODEL, f"p2-{kljuc}", x)
    stanja = [[int(v) for v in r[AKT].strip("[]").split()] for r in redovi]
    ustao = [-1] * len(stanja[0])
    for t, st in enumerate(stanja):
        for i, a in enumerate(st):
            if a and ustao[i] < 0:
                ustao[i] = t
    return {"kljuc": kljuc, "rasipanje": ras, "seed": seed, "prosjek": 0.3, "pokretaci": 10,
            "prag": [int(float(v)) for v in redovi[0][PRAG].strip("[]").split()],
            "ustao": ustao, "krugova": max(ustao), "udio_kraj": float(redovi[-1]["udio-aktivnih"])}

zapisi = [zapis("ras01", 0.1, 3)]
# uz rasipanje 0,05 talas nastane u oko 40% pokretanja: uzmi prvo sjeme bez talasa i prvo s talasom
bez, sa = None, None
for seed in range(1, 30):
    z = zapis(f"ras005-s{seed}", 0.05, seed)
    if z["udio_kraj"] < 0.1 and bez is None:
        bez = z
    if z["udio_kraj"] > 0.9 and sa is None:
        sa = z
    if bez and sa:
        break
bez["kljuc"], sa["kljuc"] = "ras005-bez", "ras005-sa"
zapisi += [bez, sa]
for z in zapisi:
    print(z["kljuc"], "seed", z["seed"], "krugova", z["krugova"], "udio na kraju", z["udio_kraj"])
put = os.path.join(MJERENJA, "podaci-b2.json")
json.dump({"model": MODEL, "netlogo": "7.0.4", "sala": 31, "zapisi": zapisi}, open(put, "w", encoding="utf-8"), separators=(",", ":"))
print("napisano:", put, os.path.getsize(put) // 1024, "KB")
