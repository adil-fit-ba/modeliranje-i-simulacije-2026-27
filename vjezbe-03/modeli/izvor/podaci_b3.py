"""Podaci za mini-prezentaciju bloka 3: mreža i stav kroz vrijeme iz pravih NetLogo pokretanja (fiksni random-seed).

Pokretanje:  python -I podaci_b3.py
Izlaz:       ../mjerenja/podaci-b3.json
  { "zapisi": [ { "kljuc", "daleke", "seed", "ljudi": [[x, y], ...] (indeks = who),
                  "veze": [[who1, who2], ...], "mediji": [[x, y], ...], "korak", "ticks": [...],
                  "stav": [[stav čovjeka i u svakom koraku × 100], ...], "udio_za": [...po koraku] } ] }
"""
import json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mjeri import pokreni, xml_eksperiment, MJERENJA

MODEL, SEED, KORAK = "v03-blok3-mreza.nlogox", 2, 5
POZ = "map [ t -> (list precision [ xcor ] of t 2 precision [ ycor ] of t 2) ] sort ljudi"
VEZE = "[ (list [ who ] of end1 [ who ] of end2) ] of links"
MED = "map [ m -> (list precision [ xcor ] of m 2 precision [ ycor ] of m 2) ] sort mediji"
STAV = "map [ t -> round (100 * [ stav ] of t) ] sort ljudi"
brojevi = lambda s: [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?(?:E-?\d+)?", s)]
parovi = lambda s: [brojevi(p) for p in re.findall(r"\[([^\[\]]*)\]", s)]

def zapis(kljuc, daleke):
    x = xml_eksperiment(f"p3-{kljuc}", 1, 500, [POZ, VEZE, MED, STAV, "udio-za"],
                        [("udio-dalekih-veza", [daleke]), ("broj-medija", [2])],
                        svaki_korak=True, setup=f"random-seed {SEED} setup")
    redovi = pokreni(MODEL, f"p3-{kljuc}", x)
    koraci = [r for r in redovi if int(r["[step]"]) % KORAK == 0]
    matrica = [[int(v) for v in brojevi(r[STAV])] for r in koraci]
    return {"kljuc": kljuc, "daleke": daleke, "seed": SEED, "korak": KORAK,
            "ljudi": parovi(redovi[0][POZ]), "veze": [[int(a), int(b)] for a, b in parovi(redovi[0][VEZE])],
            "mediji": parovi(redovi[0][MED]), "ticks": [int(r["[step]"]) for r in koraci],
            "stav": [[red[i] for red in matrica] for i in range(len(matrica[0]))],
            "udio_za": [round(float(r["udio-za"]), 3) for r in koraci]}

zapisi = [zapis("d0", 0), zapis("d02", 0.2)]
for z in zapisi:
    print(z["kljuc"], "ljudi", len(z["ljudi"]), "veza", len(z["veze"]), "kuća", len(z["mediji"]),
          "udio za na 0 / 500:", z["udio_za"][0], z["udio_za"][-1])
put = os.path.join(MJERENJA, "podaci-b3.json")
json.dump({"model": MODEL, "netlogo": "7.0.4", "zapisi": zapisi}, open(put, "w", encoding="utf-8"), separators=(",", ":"))
print("napisano:", put, os.path.getsize(put) // 1024, "KB")
