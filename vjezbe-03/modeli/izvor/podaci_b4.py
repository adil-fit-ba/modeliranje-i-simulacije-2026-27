"""Podaci za mini-prezentaciju bloka 4 (preseljenje): pokretanja sa sjemenom, stanje mreže po ticku.

Pokretanje:  python -I podaci_b4.py
Izlaz:       ../mjerenja/podaci-b4.json
  { "pokretanja": [ { "kljuc", "trazeno", "gustina", "seed", "ticks": [...],
                      "mreza": ["0120…" po ticku: 41 × 41 znak, red po red odozgo (sort patches);
                                0 = prazno, 1 = grupa 0 (plava), 2 = grupa 1 (narandžasta)],
                      "slicnih": [...], "nezadovoljnih": [...] } ],
    "strogo": { "trazeno": 0.8, "n", "ticks_limit", "nezadovoljnih": [...], "slicnih": [...], "ticks": [...] } }
"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mjeri import pokreni, xml_eksperiment, MJERENJA

MODEL = "v03-blok4-preseljenje.nlogox"
SEED = 4
MREZA = "reduce word map [ p -> ifelse-value any? ljudi-on p [ 1 + [ grupa ] of one-of ljudi-on p ] [ 0 ] ] sort patches"

izlaz = {"model": MODEL, "netlogo": "7.0.4", "pokretanja": []}
for kljuc, trazeno, limit in (("t03", 0.3, 200), ("t075", 0.75, 300)):
    x = xml_eksperiment(f"b4-{kljuc}", 1, limit, [MREZA, "prosjecno-slicnih", "udio-nezadovoljnih"],
                        [("trazeni-udio-slicnih", [trazeno]), ("gustina", [0.7])],
                        svaki_korak=True, setup=f"random-seed {SEED} setup")
    redovi = pokreni(MODEL, f"b4-{kljuc}", x)
    mreze = [r[MREZA].strip('"') for r in redovi]
    assert all(len(m) == 41 * 41 for m in mreze), {len(m) for m in mreze}
    p = {"kljuc": kljuc, "trazeno": trazeno, "gustina": 0.7, "seed": SEED,
         "ticks": [int(r["[step]"]) for r in redovi], "mreza": mreze,
         "slicnih": [round(float(r["prosjecno-slicnih"]), 4) for r in redovi],
         "nezadovoljnih": [round(float(r["udio-nezadovoljnih"]), 4) for r in redovi]}
    izlaz["pokretanja"].append(p)
    print(kljuc, "tickova:", p["ticks"][-1], "slicnih:", p["slicnih"][0], "->", p["slicnih"][-1],
          "nezadovoljnih:", p["nezadovoljnih"][0], "->", p["nezadovoljnih"][-1])

# preoštar zahtjev: 80% sličnih, 10 pokretanja, najviše 300 mjeseci
x = xml_eksperiment("b4-strogo", 10, 300, ["udio-nezadovoljnih", "prosjecno-slicnih", "ticks"],
                    [("trazeni-udio-slicnih", [0.8]), ("gustina", [0.7])])
redovi = pokreni(MODEL, "b4-strogo", x)
izlaz["strogo"] = {"trazeno": 0.8, "gustina": 0.7, "n": len(redovi), "ticks_limit": 300,
                   "nezadovoljnih": sorted(round(float(r["udio-nezadovoljnih"]), 4) for r in redovi),
                   "slicnih": sorted(round(float(r["prosjecno-slicnih"]), 4) for r in redovi),
                   "ticks": sorted(int(float(r["ticks"])) for r in redovi)}
print("strogo:", izlaz["strogo"])

put = os.path.join(MJERENJA, "podaci-b4.json")
json.dump(izlaz, open(put, "w", encoding="utf-8"), separators=(",", ":"))
print("napisano:", put, os.path.getsize(put) // 1024, "KB")
