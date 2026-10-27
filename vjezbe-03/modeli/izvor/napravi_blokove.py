"""Sklapa samostalne mini-prezentacije blokova: svaki blokovi/blok*.html postaje jedan HTML fajl.

Dogovor za šablon (blokovi/blokN.html):
  - prvi red:            <!--IZLAZ: ime-fajla.html-->            ime izlaza u ../../blokovi/
  - podaci iz fajla:     {{JSON:mjerenja/ime.json}}              putanja relativna na ../ (mapa modeli/)
  - podaci iz mjerenja:  {{MJERENJA:kljuc1,kljuc2}}              podskup mjerenja/rezultati.json
  - <!--TIJELO-->        dijeli <head> dio (title, style) od tijela

Izlaz:  ../../blokovi/<IZLAZ>  (samostalan; linkovi vode u ../netlogo-web/, ../modeli/)
        uz --artifact <folder>: ista stranica bez <!doctype>/<html>/<head>/<body> za objavu kao Artifact
Pokretanje:  python -I napravi_blokove.py [blok1 blok2 ...] [--artifact <folder>]
"""
import io, json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
OVDJE = os.path.dirname(os.path.abspath(__file__))
MODELI = os.path.dirname(OVDJE)
V03 = os.path.dirname(MODELI)
citaj = lambda p: io.open(p, encoding="utf-8").read()

arg = sys.argv[1:]
artifact = None
if "--artifact" in arg:
    i = arg.index("--artifact"); artifact = arg[i + 1]; del arg[i:i + 2]
rez = json.loads(citaj(os.path.join(MODELI, "mjerenja", "rezultati.json")))
sabloni = sorted(f for f in os.listdir(os.path.join(OVDJE, "blokovi")) if re.fullmatch(r"blok\d+\.html", f))
if arg:
    sabloni = [f for f in sabloni if f[:-5] in arg]

for f in sabloni:
    s = citaj(os.path.join(OVDJE, "blokovi", f))
    m = re.match(r"<!--IZLAZ: ([\w.-]+\.html)-->\n", s)
    assert m, f"{f}: prvi red mora biti <!--IZLAZ: ime.html-->"
    ime, s = m.group(1), s[m.end():]
    s = re.sub(r"\{\{JSON:([^}]+)\}\}",
               lambda x: json.dumps(json.loads(citaj(os.path.join(MODELI, x.group(1)))), ensure_ascii=False, separators=(",", ":")), s)
    s = re.sub(r"\{\{MJERENJA:([^}]+)\}\}",
               lambda x: json.dumps({k: rez[k] for k in x.group(1).split(",")}, ensure_ascii=False, separators=(",", ":")), s)
    ostalo = re.findall(r"\{\{[A-Z]+:[^}]*\}\}", s)
    assert not ostalo, (f, ostalo)
    glava, tijelo = s.split("<!--TIJELO-->")
    samostalno = ('<!doctype html>\n<html lang="bs">\n<head>\n<meta charset="utf-8">\n'
                  '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                  + glava + '</head>\n<body>\n' + tijelo + '</body>\n</html>\n')
    izlaz = os.path.join(V03, "blokovi", ime)
    os.makedirs(os.path.dirname(izlaz), exist_ok=True)
    io.open(izlaz, "w", encoding="utf-8", newline="\n").write(samostalno)
    print("napisano:", izlaz, f"({len(samostalno.encode('utf-8')) // 1024} KB)")
    if artifact:
        os.makedirs(artifact, exist_ok=True)
        put = os.path.join(artifact, ime)
        io.open(put, "w", encoding="utf-8", newline="\n").write(glava + tijelo)
        print("   za artifact:", put)
