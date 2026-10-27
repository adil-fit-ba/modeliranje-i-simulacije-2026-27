"""Mjerenja za blok 6 (kontrola i kazna), NetLogo 7.0.4 headless.

Pokretanje:  python -I mjerenja_b6.py [mreza razgovor putanje]   (bez argumenata: sve)
Izlaz:  ../mjerenja/rezultati-b6.json i .md  (prosječna sklonost prema vjerovatnoći kontrole, uticaj razgovora)
        ../mjerenja/podaci-b6.json           (sklonost svakog čovjeka kroz vrijeme, jedno pokretanje po uslovu)
"""
import io, json, os, statistics as st, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mjeri import pokreni, xml_eksperiment, MJERENJA

MODEL = "v03-blok6-kazna.nlogox"
JSON = os.path.join(MJERENJA, "rezultati-b6.json")
rez = json.load(open(JSON, encoding="utf-8")) if os.path.exists(JSON) else {}
koji = sys.argv[1:] or ["mreza", "razgovor", "putanje"]
PON = 20


def sazetak(v):
    v = sorted(v)
    return {"n": len(v), "sred": round(st.mean(v), 4), "med": round(st.median(v), 4),
            "min": round(v[0], 4), "max": round(v[-1], 4)}

def po_uslovu(redovi, kljucevi, mjera, step):
    g = collections.defaultdict(list)
    for r in redovi:
        if r["[step]"] == str(step):
            g[" | ".join(f"{k}={r[k]}" for k in kljucevi)].append(float(r[mjera]))
    return {k: sazetak(v) for k, v in sorted(g.items(), key=lambda kv: [float(x.split("=")[1]) if x.split("=")[1][0].isdigit() else x for x in kv[0].split(" | ")])}

def presjek(tab, start):
    """Vjerovatnoća kontrole na kojoj medijan prosječne sklonosti siječe početnu vrijednost (linearna interpolacija)."""
    tacke = sorted((float(k.split("=")[1]), v["med"]) for k, v in tab.items())
    for (q0, s0), (q1, s1) in zip(tacke, tacke[1:]):
        if (s0 - start) * (s1 - start) <= 0 and s0 != s1:
            return round(q0 + (start - s0) * (q1 - q0) / (s1 - s0), 4)
    return None


if "mreza" in koji:
    for oznaka, kazna, mreza in (("k01", 0.1, [0, 0.05, 0.1, 0.12, 0.14, 0.15, 0.16, 0.17, 0.18, 0.2, 0.25, 0.3, 0.4, 0.5]),
                                 ("k03", 0.3, [0, 0.02, 0.04, 0.05, 0.06, 0.07, 0.08, 0.1, 0.15, 0.2, 0.3])):
        r = pokreni(MODEL, f"m-{oznaka}",
                    xml_eksperiment(f"m-{oznaka}", PON, 300, ["prosjecna-sklonost"],
                                    [("vjerovatnoca-kontrole", mreza), ("jacina-kazne", [kazna]), ("pomak-bez-kazne", [0.02]),
                                     ("razgovor?", ["false"])], svaki_korak=True))
        for t in (0, 150, 300):
            rez[f"{oznaka}_t{t}"] = po_uslovu(r, ["vjerovatnoca-kontrole"], "prosjecna-sklonost", t)
        start = st.median(v["med"] for v in rez[f"{oznaka}_t0"].values())
        rez[f"{oznaka}_prag"] = {"teorija": round(0.02 / (0.02 + kazna), 4), "pocetak": round(start, 4),
                                 "presjek_t150": presjek(rez[f"{oznaka}_t150"], start),
                                 "presjek_t300": presjek(rez[f"{oznaka}_t300"], start)}
        print(oznaka, rez[f"{oznaka}_prag"])

if "razgovor" in koji:
    r = pokreni(MODEL, "m-razgovor",
                xml_eksperiment("m-razgovor", PON, 150, ["prosjecna-sklonost", "standard-deviation [ sklonost ] of ljudi"],
                                [("vjerovatnoca-kontrole", [0.05, 0.1, 0.15, 0.17, 0.2, 0.3]), ("jacina-kazne", [0.1]),
                                 ("pomak-bez-kazne", [0.02]), ("razgovor?", ["false", "true"])]))
    rez["razgovor_t150"] = po_uslovu(r, ["razgovor?", "vjerovatnoca-kontrole"], "prosjecna-sklonost", 150)
    rez["razgovor_sd_t150"] = po_uslovu(r, ["razgovor?", "vjerovatnoca-kontrole"], "standard-deviation [ sklonost ] of ljudi", 150)
    print("razgovor gotov")

json.dump(rez, open(JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if "putanje" in koji:
    KORAK, TICKS, SEED = 3, 150, 1
    uslovi = [("q01", 0.1, False), ("q03", 0.3, False), ("q01r", 0.1, True), ("q03r", 0.3, True)]
    izlaz = []
    stupac = "map [ t -> precision [ sklonost ] of t 3 ] sort ljudi"
    for kljuc, q, razg in uslovi:
        x = xml_eksperiment(f"put-{kljuc}", 1, TICKS, [stupac, "prosjecna-sklonost", "udio-prekrsaja"],
                            [("vjerovatnoca-kontrole", [q]), ("jacina-kazne", [0.1]), ("pomak-bez-kazne", [0.02]),
                             ("razgovor?", ["true" if razg else "false"])],
                            svaki_korak=True, setup=f"random-seed {SEED} setup")
        redovi = pokreni(MODEL, f"put-{kljuc}", x)
        koraci = [r for r in redovi if int(r["[step]"]) % KORAK == 0]
        matrica = [[round(float(v) * 100) for v in r[stupac].strip("[]").split()] for r in koraci]
        izlaz.append({"kljuc": kljuc, "q": q, "kazna": 0.1, "pomak": 0.02, "razgovor": razg, "seed": SEED, "korak": KORAK,
                      "ticks": [int(r["[step]"]) for r in koraci],
                      "sklonost": [[red[i] for red in matrica] for i in range(len(matrica[0]))],
                      "prosjek": [round(float(r["prosjecna-sklonost"]), 4) for r in koraci],
                      "prosjek_kraj": round(float(redovi[-1]["prosjecna-sklonost"]), 4),
                      "udio_prekrsaja_kraj": round(float(redovi[-1]["udio-prekrsaja"]), 4)})
        print(kljuc, "prosjek na kraju", izlaz[-1]["prosjek_kraj"])
    put = os.path.join(MJERENJA, "podaci-b6.json")
    json.dump({"model": MODEL, "netlogo": "7.0.4", "uslovi": izlaz}, open(put, "w", encoding="utf-8"), separators=(",", ":"))
    print("napisano:", put, os.path.getsize(put) // 1024, "KB")

# ---------- čitljiv sažetak ----------
L = ["# Mjerenja bloka 6 (kontrola i kazna)", "",
     f"NetLogo 7.0.4 headless, skript `izvor/mjerenja_b6.py`. {PON} pokretanja po vrijednosti; pomak-bez-kazne 0,02;",
     "ostali klizači na zadanim vrijednostima. Mjera: prosječna sklonost (medijan i raspon po pokretanjima).", ""]
for kljuc, tab in rez.items():
    if kljuc.endswith("_prag"):
        L += [f"## {kljuc}", "", "```", json.dumps(tab, ensure_ascii=False), "```", ""]
        continue
    L += [f"## {kljuc}", "", "| uslov | n | prosjek | medijan | min | max |", "|---|---|---|---|---|---|"]
    for uslov, x in tab.items():
        L.append(f"| {uslov} | {x['n']} | {x['sred']} | {x['med']} | {x['min']} | {x['max']} |")
    L.append("")
io.open(os.path.join(MJERENJA, "rezultati-b6.md"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
print("rezultati-b6.md napisan")
