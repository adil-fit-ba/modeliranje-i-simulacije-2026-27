"""Pravi samostalne NetLogo Web stranice za sve blokove (pravi NetLogo model u web pregledniku, bez instalacije).

Predložak je NetLogo Web „standalone“ stranica (https://www.netlogoweb.org/standalone, ~5 MB, sadrži cijeli
NetLogo Web). Model se upisuje u <script type="text/nlogo" id="nlogo-code">, isto kao kad NetLogo Web
sam izveze model u HTML.

Pokretanje:  python -I napravi_netlogo_web.py <putanja do standalone.html>
Izlaz:       ../../netlogo-web/v03-blok*.html
"""
import io, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
OVDJE = os.path.dirname(os.path.abspath(__file__))
MODELI = os.path.dirname(OVDJE)
IZLAZ = os.path.normpath(os.path.join(MODELI, "..", "netlogo-web"))
MJESTO = '<script type="text/nlogo" id="nlogo-code" data-filename="model.nlogox"></script>'
IMENA = sorted(f[:-7] for f in os.listdir(MODELI) if f.startswith("v03-blok") and f.endswith(".nlogox"))  # svi modeli blokova

predlozak = io.open(sys.argv[1], encoding="utf-8").read()
assert predlozak.count(MJESTO) == 1, "predložak nema očekivano mjesto za model"

# VS Code Live Server (i slični) ubacuju svoj skript ispred prvog </body> u fajlu. U NetLogo Webu se
# </body> i </head> pojavljuju i unutar JavaScript stringova (npr. Highcharts izvoz), pa bi ubačeni kod
# razbio JavaScript. Unutar <script> zato pišemo <\/body> i <\/head>: u JS stringu i regexu je to isto.
SKRIPTA = re.compile(r"(<script\b[^>]*>)(.*?)(</script>)", re.S | re.I)
OZNAKA = re.compile(r"</(body|head|html)>", re.I)

def zastiti_skripte(html):
    izlaz, poz = [], 0
    for m in SKRIPTA.finditer(html):
        tijelo = OZNAKA.sub(lambda t: "<\\/" + t.group(1) + ">", m.group(2))
        izlaz += [html[poz:m.start(2)], tijelo]
        poz = m.end(2)
    izlaz.append(html[poz:])
    return "".join(izlaz)

predlozak = zastiti_skripte(predlozak)
for oznaka in ("</body>", "</head>"):
    assert predlozak.lower().count(oznaka) == 1, f"{oznaka} se i dalje pojavljuje više puta"
os.makedirs(IZLAZ, exist_ok=True)
for ime in IMENA:
    model = io.open(os.path.join(MODELI, ime + ".nlogox"), encoding="utf-8").read()
    assert "</script" not in model.lower()
    html = predlozak.replace(MJESTO, f'<script type="text/nlogo" id="nlogo-code" data-filename="{ime}.nlogox">{model}</script>')
    put = os.path.join(IZLAZ, ime + ".html")
    io.open(put, "w", encoding="utf-8", newline="\n").write(html)
    print("napisano:", put, f"({len(html.encode('utf-8')) // 1024} KB)")
