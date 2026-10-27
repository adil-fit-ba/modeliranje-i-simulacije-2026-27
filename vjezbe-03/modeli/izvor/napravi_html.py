"""Sklapa stranicu „Blokovi interakcije“ iz html/stranica.html, html/sim.js, html/ui.js,
mjerenja/rezultati.json, NetLogo koda (napravi_modele.py) i C# koda (projekat netlogo-kroz-csharp).

Izlaz:
  ../../v03-blokovi-interakcije.html   samostalan fajl (za dijeljenje; radi i bez interneta, uz zamjenske fontove)
  <argument 1, ako je dat>             ista stranica bez <!doctype>/<html>/<head>/<body> (za objavu kao Artifact)
  --csharp                             varijanta u kojoj simulacije računa C# (.NET WebAssembly, projekat
                                       ../../../materijali/netlogo-kroz-csharp-wasm) → ../../v03-blokovi-interakcije-csharp.html
Pokretanje:  python -I napravi_html.py [--csharp] [putanja-za-artifact.html]
"""
import html, io, json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
OVDJE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, OVDJE)
import napravi_modele as M

V03 = os.path.normpath(os.path.join(OVDJE, "..", ".."))
CS = os.path.normpath(os.path.join(V03, "..", "materijali", "netlogo-kroz-csharp", "Blokovi"))
citaj = lambda p: io.open(p, encoding="utf-8").read()

def procedure(kod, imena):
    """Izdvaja `to ime ... end` (ili to-report) iz NetLogo koda, redom kako su navedena."""
    dijelovi = []
    for ime in imena:
        m = re.search(rf"^(to|to-report) {re.escape(ime)}\b.*?^end$", kod, re.M | re.S)
        assert m, ime
        dijelovi.append(m.group(0))
    return "\n\n".join(dijelovi)

def csharp(fajl, imena):
    """Izdvaja metode iz C# fajla po imenu (od reda s potpisom do zatvorene vitičaste zagrade na istom uvlačenju)."""
    put = os.path.join(CS, fajl)
    if not os.path.exists(put):
        return None
    redovi = citaj(put).split("\n")
    dijelovi = []
    for ime in imena:
        i = next((k for k, r in enumerate(redovi) if re.search(rf"\b{re.escape(ime)}\s*\(", r)
                  and re.search(r"\b(static|public|internal|private|void|bool|double|int)\b", r)), None)
        if i is None:
            return None
        # komentari neposredno iznad metode idu s njom
        poc = i
        while poc > 0 and redovi[poc - 1].strip().startswith("//"):
            poc -= 1
        uvlaka = len(redovi[i]) - len(redovi[i].lstrip())
        k = i
        kod = redovi[i].split("//")[0].rstrip()
        if kod.endswith("=>"):                          # metoda-izraz u više redova: do reda sa ;
            while not redovi[k].split("//")[0].rstrip().endswith(";"):
                k += 1
        elif not kod.endswith(";"):                     # tijelo metode u vitičastim zagradama
            while True:
                k += 1
                r = redovi[k]
                if r.strip() == "}" and len(r) - len(r.lstrip()) == uvlaka:
                    break
        blok = [r[uvlaka:] if r[:uvlaka].strip() == "" else r for r in redovi[poc:k + 1]]
        dijelovi.append("\n".join(blok))
    return "\n\n".join(dijelovi)

NL = {
    1: procedure(M.KOD_1, ["razgovaraj", "slusaj-medije"]),
    2: procedure(M.KOD_2, ["go", "udio-oko-mene"]),
    3: procedure(M.KOD_3, ["napravi-mrezu", "razgovaraj"]),
    4: procedure(M.KOD_4, ["go", "procijeni", "preseli-se"]),
}
CS_SPEC = json.loads(citaj(os.path.join(OVDJE, "html", "csharp-izvodi.json"))) \
    if os.path.exists(os.path.join(OVDJE, "html", "csharp-izvodi.json")) else {}
CSK = {}
for b in (1, 2, 3, 4):
    spec = CS_SPEC.get(str(b))
    CSK[b] = csharp(spec["fajl"], spec["metode"]) if spec else None
ima_cs = all(CSK.values())
for b in CSK:
    if not CSK[b]:
        CSK[b] = "// C# verzija ovog bloka je u projektu netlogo-kroz-csharp (Blokovi/)."

rez = json.loads(citaj(os.path.join(V03, "modeli", "mjerenja", "rezultati.json")))
POTREBNO = ["b1_grupe_500", "b1_udio_za_mediji_0", "b1_udio_za_mediji_150", "b2_rasipanje", "b2_pokretaci",
            "b3_udio_za_0", "b3_udio_za_500", "b4_slicnih_pocetak", "b4_slicnih_kraj"]
mjerenja = {k: rez[k] for k in POTREBNO}

stranica = citaj(os.path.join(OVDJE, "html", "stranica.html"))
zamjene = {
    "{{MJERENJA}}": json.dumps(mjerenja, ensure_ascii=False, separators=(",", ":")),
    "{{SIM}}": citaj(os.path.join(OVDJE, "html", "sim.js")),
    "{{UI}}": citaj(os.path.join(OVDJE, "html", "ui.js")),
    "{{CS_NAPOMENA}}": (
        "Isti blokovi nalaze se u C# projektu <code>netlogo-kroz-csharp</code> (mapa <code>Blokovi/</code>), koji koristi pojednostavljenu implementaciju NetLoga u C#. "
        "Naredba <code>dotnet run -- blokovi</code> ispisuje iste mjere kao u tabeli iznad, radi poređenja s NetLogom."
        if ima_cs else
        "C# verzija blokova se dodaje u projekat <code>netlogo-kroz-csharp</code> (mapa <code>Blokovi/</code>)."),
}
for b in (1, 2, 3, 4):
    zamjene[f"{{{{KOD_{b}_NL}}}}"] = html.escape(NL[b], quote=False)
    zamjene[f"{{{{KOD_{b}_CS}}}}"] = html.escape(CSK[b], quote=False)
for k, v in zamjene.items():
    assert k in stranica, k
    stranica = stranica.replace(k, v)
assert "{{" not in stranica.replace("{{{", ""), re.findall(r"\{\{[A-Z_0-9]+\}\}", stranica)

ARG = [a for a in sys.argv[1:] if not a.startswith("--")]
SA_CSHARP = "--csharp" in sys.argv[1:]

# ---------- varijanta s C#: simulacije računa C# (.NET WebAssembly) umjesto sim.js ----------
# Pokretanje:  python -I napravi_html.py --csharp   →  ../../v03-blokovi-interakcije-csharp.html
WASM = os.path.normpath(os.path.join(V03, "..", "materijali", "netlogo-kroz-csharp-wasm"))
WASM_IZLAZ = os.path.join(os.environ.get("LOCALAPPDATA", os.path.join(OVDJE, "..", "..")), "VSBuild", "NetLogoWasm", "publish")

# rečenice koje u varijanti s C# moraju reći ko računa simulaciju (razmaci i prelomi reda se zanemaruju)
CSHARP_TEKST = [
    ("Simulacije na ovoj stranici rade u web pregledniku i prate isti kod kao NetLogo modeli.",
     "Simulacije na ovoj stranici računa C# kod iz projekta <code>netlogo-kroz-csharp</code> (MiniNetLogo i "
     "<code>Blokovi/</code>), preveden da radi u web pregledniku (.NET WebAssembly)."),
    ("Simulacija u web pregledniku je provjerena prema ovim mjerenjima i daje isti obrazac; njen kod je u izvoru stranice.",
     "Simulacije na ovoj stranici računa isti C# kod kao <code>dotnet run -- blokovi</code> u projektu "
     "<code>netlogo-kroz-csharp</code>, preveden za web preglednik; C# daje iste raspone kao NetLogo."),
]

def csharp_resursi():
    """Objavi WASM projekat i vrati JS koji ugrađuje sve njegove datoteke (gzip + base64)."""
    import base64, gzip, subprocess
    # projekat izričito: u mapi je i NetLogoWasm.sln, pa bi dotnet bez imena javio MSB1011
    r = subprocess.run(["dotnet", "publish", "NetLogoWasm.csproj", "-c", "Release", "-o", WASM_IZLAZ], cwd=WASM,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SystemExit("dotnet publish nije uspio:\n" + r.stdout[-3000:] + r.stderr[-3000:])
    fw = os.path.join(WASM_IZLAZ, "wwwroot", "_framework")
    boot = json.loads(citaj(os.path.join(fw, "blazor.boot.json")))
    res = boot["resources"]
    imena = ["dotnet.js"] + [i for g in ("jsModuleNative", "jsModuleRuntime", "wasmNative", "assembly") for i in res.get(g, {})]
    ugradjeno = {}
    for ime in imena:
        sirovo = io.open(os.path.join(fw, ime), "rb").read()
        ugradjeno[ime] = base64.b64encode(gzip.compress(sirovo, 9, mtime=0)).decode("ascii")
    print("C#: ugrađeno", len(imena), "datoteka,", sum(len(v) for v in ugradjeno.values()) // 1024, "KB (base64)")
    return ("window.CS_BOOT = " + json.dumps(boot, separators=(",", ":")) + ";\n"
            "window.CS_RESURSI = " + json.dumps(ugradjeno, separators=(",", ":")) + ";\n")

def zamijeni_tekst(s, staro, novo):
    uzorak = r"\s+".join(re.escape(rijec) for rijec in staro.split())
    s2, n = re.subn(uzorak, novo, s)
    if n != 1:
        print(f"UPOZORENJE: rečenica nije nađena tačno jednom ({n}): {staro[:60]} …")
    return s2

if SA_CSHARP:
    pocetak_sim = stranica.index(zamjene["{{SIM}}"])
    stranica = (stranica[:pocetak_sim] + csharp_resursi() + citaj(os.path.join(OVDJE, "html", "sim-csharp.js"))
                + stranica[pocetak_sim + len(zamjene["{{SIM}}"]):])
    for staro, novo in CSHARP_TEKST:
        stranica = zamijeni_tekst(stranica, staro, novo)

glava, tijelo = stranica.split("<!--TIJELO-->")
samostalno = ('<!doctype html>\n<html lang="bs">\n<head>\n<meta charset="utf-8">\n'
              '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
              + glava + '</head>\n<body>\n' + tijelo + '</body>\n</html>\n')
izlaz = os.path.join(V03, "v03-blokovi-interakcije-csharp.html" if SA_CSHARP else "v03-blokovi-interakcije.html")
io.open(izlaz, "w", encoding="utf-8", newline="\n").write(samostalno)
print("napisano:", izlaz, f"({len(samostalno.encode('utf-8')) // 1024} KB)", "C#:", "da" if ima_cs else "ne",
      "| simulacije:", "C# (WebAssembly)" if SA_CSHARP else "JavaScript")
if ARG:
    io.open(ARG[0], "w", encoding="utf-8", newline="\n").write(glava + tijelo)
    print("napisano:", ARG[0])
