"""Putanje stava za blok 1: stav svakog čovjeka kroz vrijeme, jedno pokretanje po uslovu (fiksni random-seed).

Pokretanje:  python -I putanje_b1.py
Izlaz:       ../mjerenja/putanje-b1.json
  { "uslovi": [ { "kljuc", "prag", "mediji", "seed", "korak", "ticks": [...],
                  "stav": [[stav čovjeka 0 u svakom koraku × 100, cijeli broj], ...],
                  "broj_grupa": n, "udio_za": x } ] }
"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mjeri import pokreni, xml_eksperiment, MJERENJA

KORAK = 4                      # svaki četvrti tick (500 tickova → 126 tačaka)
TICKS = 500
SEED = 1
USLOVI = [("p02", 0.2, False), ("p05", 0.5, False), ("p2", 2, False), ("p03m", 0.3, True), ("p2m", 2, True)]

izlaz = []
for kljuc, prag, mediji in USLOVI:
    x = xml_eksperiment(f"put-{kljuc}", 1, TICKS,
                        ["map [ t -> precision [ stav ] of t 3 ] sort ljudi", "broj-grupa", "udio-za"],
                        [("prag", [prag]), ("mediji-rade?", ["true" if mediji else "false"])],
                        svaki_korak=True, setup=f"random-seed {SEED} setup")
    redovi = pokreni("v03-blok1-povjerenje.nlogox", f"put-{kljuc}", x)
    stupac = "map [ t -> precision [ stav ] of t 3 ] sort ljudi"
    koraci = [r for r in redovi if int(r["[step]"]) % KORAK == 0]
    matrica = [[round(float(v) * 100) for v in r[stupac].strip("[]").split()] for r in koraci]
    n = len(matrica[0])
    izlaz.append({"kljuc": kljuc, "prag": prag, "mediji": mediji, "seed": SEED, "korak": KORAK,
                  "ticks": [int(r["[step]"]) for r in koraci],
                  "stav": [[red[i] for red in matrica] for i in range(n)],
                  "broj_grupa": int(float(redovi[-1]["broj-grupa"])), "udio_za": float(redovi[-1]["udio-za"])})
    print(kljuc, "tačaka:", len(koraci), "ljudi:", n, "grupa na kraju:", izlaz[-1]["broj_grupa"], "udio za:", izlaz[-1]["udio_za"])

put = os.path.join(MJERENJA, "putanje-b1.json")
json.dump({"model": "v03-blok1-povjerenje.nlogox", "netlogo": "7.0.4", "uslovi": izlaz}, open(put, "w", encoding="utf-8"),
          separators=(",", ":"))
print("napisano:", put, os.path.getsize(put) // 1024, "KB")
