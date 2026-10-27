"""Mjerenja bloka 5 (mjesto s iskustvom), NetLogo 7.0.4 headless.

Pokretanje:  python -I mjerenja_b5.py [mjerenja] [podaci]   (bez argumenata: oboje)
Izlaz:  ../mjerenja/rezultati-b5.json i .md   — mjerenja (20 pokretanja po vrijednosti)
        ../mjerenja/podaci-b5.json             — jedno pokretanje po uslovu (random-seed 5): putanje povjerenja,
                                                 sedmica prve posjete, slika svijeta (export-view)
"""
import base64, io, json, os, re, statistics as st, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mjeri import pokreni, xml_eksperiment, MJERENJA

MODEL = "v03-blok5-ustanova.nlogox"
koji = sys.argv[1:] or ["mjerenja", "podaci"]
M = ["prosjecno-povjerenje", "udio-povjerljivih", "udio-posjetilaca", "povjerenje-posjetilaca", "povjerenje-ostalih"]

def sazetak(v):
    v = sorted(v)
    return {"n": len(v), "sred": round(st.mean(v), 4), "med": round(st.median(v), 4), "min": round(v[0], 4), "max": round(v[-1], 4)}

def grupe(redovi, kljucevi, mjera, step=None):
    g = collections.defaultdict(list)
    for r in redovi:
        if step is None or r["[step]"] == str(step):
            g[" | ".join(f"{k}={r[k]}" for k in kljucevi)].append(float(r[mjera]))
    return {k: sazetak(v) for k, v in sorted(g.items())}

if "mjerenja" in koji:
    rez = {}
    P = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    r = pokreni(MODEL, "m5-iskustva", xml_eksperiment("m5-iskustva", 20, 150, M,
                [("udio-losih-iskustava", P), ("razgovor?", ["false", "true"])], svaki_korak=True))
    for m in M:
        rez[f"b5_{m}_150"] = grupe(r, ["razgovor?", "udio-losih-iskustava"], m, 150)
    rez["b5_prosjecno-povjerenje_50"] = grupe(r, ["razgovor?", "udio-losih-iskustava"], "prosjecno-povjerenje", 50)
    # vremenski tok (prosjek 20 pokretanja) za udio loših 0,7
    tok = collections.defaultdict(lambda: collections.defaultdict(list))
    for x in r:
        if x["udio-losih-iskustava"] == "0.7" and int(x["[step]"]) % 5 == 0:
            for m in ("prosjecno-povjerenje", "povjerenje-posjetilaca", "povjerenje-ostalih", "udio-posjetilaca"):
                v = float(x[m])
                if v >= 0:
                    tok[(x["razgovor?"], m)][int(x["[step]"])].append(v)
    rez["b5_tok_07"] = {f"{k[0]}|{k[1]}": [[t, round(st.mean(v), 4)] for t, v in sorted(d.items())] for k, d in tok.items()}
    r = pokreni(MODEL, "m5-ustanove", xml_eksperiment("m5-ustanove", 20, 150, M,
                [("broj-ustanova", [5, 10, 20, 40]), ("udio-losih-iskustava", [0.7]), ("razgovor?", ["false", "true"])]))
    for m in ("udio-posjetilaca", "prosjecno-povjerenje", "povjerenje-ostalih"):
        rez[f"b5_ustanove_{m}"] = grupe(r, ["razgovor?", "broj-ustanova"], m)
    json.dump(rez, open(os.path.join(MJERENJA, "rezultati-b5.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L = ["# Mjerenja bloka 5 (mjesto s iskustvom)", "",
         "NetLogo 7.0.4 headless, skript `izvor/mjerenja_b5.py`. Zadane vrijednosti: 200 ljudi, 20 ustanova, snaga iskustva 0,6,",
         "početno povjerenje 0,5, domet 3, uticaj 0,2. Kolone: n, prosjek, medijan, min, max. −1 znači da takvih ljudi nema.", ""]
    for k, tab in rez.items():
        if k == "b5_tok_07":
            continue
        L += [f"## {k}", "", "| uslov | n | prosjek | medijan | min | max |", "|---|---|---|---|---|---|"]
        L += [f"| {u} | {x['n']} | {x['sred']} | {x['med']} | {x['min']} | {x['max']} |" for u, x in tab.items()] + [""]
    io.open(os.path.join(MJERENJA, "rezultati-b5.md"), "w", encoding="utf-8", newline="\n").write("\n".join(L))
    print("mjerenja gotova")

if "podaci" in koji:
    SEED, KORAK, TICKS = 5, 2, 150
    uslovi = []
    for kljuc, razgovor in (("bez", "false"), ("sa", "true")):
        slika = os.path.join(MJERENJA, "slike", f"b5-{kljuc}-razgovora.png").replace("\\", "/")
        os.makedirs(os.path.dirname(slika), exist_ok=True)
        stupac = "map [ t -> (list precision [ povjerenje ] of t 3 [ posjeta ] of t) ] sort ljudi"
        x = xml_eksperiment(f"p5-{kljuc}", 1, TICKS, [stupac, "prosjecno-povjerenje", "udio-posjetilaca",
                            "povjerenje-posjetilaca", "povjerenje-ostalih",
                            "[ (list pxcor pycor) ] of patches with [ ustanova? ]"],
                            [("udio-losih-iskustava", [0.7]), ("razgovor?", [razgovor])], svaki_korak=True,
                            setup=f"random-seed {SEED} setup", final=f'export-view "{slika}"')
        redovi = pokreni(MODEL, f"p5-{kljuc}", x)
        def parsiraj(tekst):          # "[[0.5 0] [0.43 1] ...]" -> [(0.5, 0), (0.43, 1), ...]
            return [(float(a), int(float(b))) for a, b in re.findall(r"\[([-\d.E]+) ([-\d.E]+)\]", tekst)]
        koraci = [rd for rd in redovi if int(rd["[step]"]) % KORAK == 0]
        matrica = [parsiraj(rd[stupac]) for rd in koraci]
        n = len(matrica[0])
        # sedmica prve posjete svakog čovjeka (−1: nikad), iz svakog ticka
        sve = [parsiraj(rd[stupac]) for rd in redovi]
        prva = [next((int(redovi[k]["[step]"]) for k in range(len(redovi)) if sve[k][i][1] > 0), -1) for i in range(n)]
        ustanove = [[int(float(a)), int(float(b))] for a, b in re.findall(r"\[([-\d.]+) ([-\d.]+)\]", redovi[-1]["[ (list pxcor pycor) ] of patches with [ ustanova? ]"])]
        kraj = redovi[-1]
        uslovi.append({"kljuc": kljuc, "razgovor": razgovor == "true", "udio_losih": 0.7, "seed": SEED, "korak": KORAK,
                       "ticks": [int(rd["[step]"]) for rd in koraci],
                       "povjerenje": [[round(matrica[k][i][0] * 100) for k in range(len(matrica))] for i in range(n)],
                       "prva_posjeta": prva, "ustanove": ustanove,
                       "kraj": {m: float(kraj[m]) for m in ("prosjecno-povjerenje", "udio-posjetilaca", "povjerenje-posjetilaca", "povjerenje-ostalih")},
                       "slika": "data:image/png;base64," + base64.b64encode(open(slika, "rb").read()).decode()})
        print(kljuc, "ljudi:", n, "tačaka:", len(koraci), "kraj:", uslovi[-1]["kraj"])
    put = os.path.join(MJERENJA, "podaci-b5.json")
    json.dump({"model": MODEL, "netlogo": "7.0.4", "uslovi": uslovi}, open(put, "w", encoding="utf-8"), separators=(",", ":"))
    print("napisano:", put, os.path.getsize(put) // 1024, "KB")
