"""Pokreće BehaviorSpace eksperiment headless (NetLogo 7.0.4) i čita tabelu rezultata.

Upotreba iz drugog skripta:
    from mjeri import pokreni
    redovi = pokreni("v03-blok1-povjerenje.nlogox", "pragovi")             # eksperiment iz modela
    redovi = pokreni("v03-blok1-povjerenje.nlogox", "x", xml=TEKST_XML)    # eksperiment iz XML-a
"""
import csv, io, os, subprocess, sys

NETLOGO = r"C:\Program Files\NetLogo 7.0.4\NetLogo_Console.exe"
OVDJE = os.path.dirname(os.path.abspath(__file__))
MODELI = os.path.dirname(OVDJE)
MJERENJA = os.path.join(MODELI, "mjerenja")


def pokreni(model, ime, xml=None, threads=4, folder=MJERENJA):
    """Vraća listu redova (dict) iz tabele; CSV ostaje u mjerenja/."""
    tabela = os.path.join(folder, f"{os.path.splitext(os.path.basename(model))[0]}-{ime}.csv")
    args = [NETLOGO, "--headless", "--model", os.path.join(MODELI, model),
            "--table", tabela, "--threads", str(threads)]
    if xml is not None:
        postavke = os.path.join(folder, f"{os.path.splitext(os.path.basename(model))[0]}-{ime}.xml")
        io.open(postavke, "w", encoding="utf-8").write(xml)
        args += ["--setup-file", postavke]
    args += ["--experiment", ime]
    if os.path.exists(tabela):
        os.remove(tabela)
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0 or not os.path.exists(tabela):
        raise RuntimeError(f"NetLogo nije uspio ({r.returncode}):\n{r.stdout}\n{r.stderr}")
    redovi = list(csv.reader(io.open(tabela, encoding="utf-8")))
    zaglavlje = redovi[6]
    podaci = [dict(zip(zaglavlje, red)) for red in redovi[7:]]
    if not podaci:
        raise RuntimeError(f"Tabela je prazna (model je vjerovatno pao):\n{r.stdout}\n{r.stderr}")
    return podaci


def xml_eksperiment(ime, ponavljanja, ticks, metrike, vrijednosti, svaki_korak=False, setup="setup", final=""):
    esc = lambda x: x.replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;')
    m = "".join(f"<metric>{esc(x)}</metric>" for x in metrike)
    setup, final = esc(setup), esc(final)
    v = "".join(
        f'<enumeratedValueSet variable="{var}">' +
        "".join(f'<value value="{val}"/>' for val in vals) + "</enumeratedValueSet>"
        for var, vals in vrijednosti)
    return (f'<experiments><experiment name="{ime}" repetitions="{ponavljanja}" sequentialRunOrder="true" '
            f'runMetricsEveryStep="{str(svaki_korak).lower()}" timeLimit="{ticks}">'
            f'<setup>{setup}</setup><go>go</go>{f'<postRun>{final}</postRun>' if final else ''}<metrics>{m}</metrics>'
            f'<constants>{v}</constants></experiment></experiments>')


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    model, ime = sys.argv[1], sys.argv[2]
    for red in pokreni(model, ime):
        print(red)
