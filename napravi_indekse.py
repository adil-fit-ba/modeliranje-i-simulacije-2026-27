"""Pravi početnu stranicu repozitorija i vjezbe-03/index.html u istom izgledu kao vjezbe-02/index.html."""
import io, sys
REPO = sys.argv[1] if len(sys.argv) > 1 else __import__("os").path.dirname(__import__("os").path.abspath(__file__))
CSS = """<style>
:root { --papir: #eef1f4; --list: #fff; --tinta: #17212b; --siva: #56636f; --linija: #d3dae1; --narandza: #b9531a;
  --f-naslov: Cambria, Georgia, serif; --f-tekst: "Segoe UI", "Helvetica Neue", Arial, sans-serif; }
@media (prefers-color-scheme: dark) { :root { --papir: #10161c; --list: #18212a; --tinta: #e3e9ee; --siva: #9ba8b4; --linija: #2a3540; --narandza: #f0894a; color-scheme: dark; } }
* { box-sizing: border-box; }
body { margin: 0; background: var(--papir); color: var(--tinta); font: 17px/1.5 var(--f-tekst); }
main { max-width: 960px; margin: 0 auto; padding: 2rem max(16px, env(safe-area-inset-left)) 3rem; }
h1, h2, h3 { font-family: var(--f-naslov); line-height: 1.2; margin: 0 0 0.4rem; }
h1 { font-size: 2.1rem; } h2 { font-size: 1.6rem; margin-top: 2.6rem; padding-top: 1.2rem; border-top: 1px solid var(--linija); }
h3 { font-size: 1.2rem; margin-top: 1.6rem; }
.oznaka { font-size: 0.8rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--narandza); }
.siva { color: var(--siva); }
.veze { display: grid; gap: 0.7rem; grid-template-columns: repeat(auto-fit, minmax(min(100%, 17rem), 1fr)); margin-top: 0.8rem; }
.veze a { display: block; text-decoration: none; background: var(--list); border: 1px solid var(--linija); border-radius: 6px; padding: 0.8rem 1rem; color: var(--tinta); }
.veze a:hover, .veze a:focus-visible { border-color: var(--narandza); }
.veze b { color: var(--narandza); }
.veze span { display: block; color: var(--siva); font-size: 0.9rem; }
footer { margin-top: 2.5rem; font-size: 0.85rem; color: var(--siva); border-top: 1px solid var(--linija); padding-top: 0.8rem; }
</style>"""
k = lambda href, naslov, opis: f'    <a href="{href}"><b>{naslov}</b><span>{opis}</span></a>\n'
grupa = lambda naslov, kartice: f'  <h3>{naslov}</h3>\n  <div class="veze">\n{"".join(kartice)}  </div>\n'

def v02(p):
    return (grupa("Prezentacije", [
        k(p + "prezentacije/v02a-ponavljanje.html", "Ponavljanje", "Vježbe 1, predavanje, četiri modela izmjerena u NetLogu, NetLogo kroz C#, headless i LLM (58 slajdova)."),
        k(p + "prezentacije/v02b-v03-gradimo-model.html", "Gradimo model: širenje stava u društvu", "Jedan model u pet koraka, rezultat iz NetLoga, zadatak i samostalna vježba (31 slajd).")])
      + grupa("Mini-prezentacije", [
        k(p + "mini/model-stava.html", "Model stava", "Agenti, atributi, razgovor, mediji, mjere i rezultat; simulacija u web pregledniku."),
        k(p + "mini/netlogo-kroz-csharp.html", "NetLogo kroz C#", "Sedam pojmova NetLoga objašnjenih kodom u C#."),
        k(p + "mini/fire.html", "Fire", "Prag gustine i rasipanje ishoda na pragu."),
        k(p + "mini/segregation.html", "Segregation", "Blaga preferencija pojedinca, jaka segregacija u cjelini."),
        k(p + "mini/wolf-sheep.html", "Wolf Sheep Predation", "Ovce, vukovi i trava: oscilacije i izumiranje."),
        k(p + "mini/rps.html", "Rock Paper Scissors", "Ciklična dominacija bez trajnog pobjednika.")])
      + grupa("Modeli", [
        k(p + "modeli/v02-model-stav.nlogox", "v02-model-stav.nlogox", "Kompletan model stava (NetLogo 7.0.4)."),
        k(p + "modeli/v02-zadatak.nlogox", "v02-zadatak.nlogox", "Model s praznim procedurama razgovaraj i slusaj-medije.")]))

BLOKOVI = [("1", "blok1-ograniceno-povjerenje", "v03-blok1-povjerenje", "Ograničeno povjerenje", "Razgovor mijenja stav samo kada je razlika stavova dovoljno mala."),
           ("2", "blok2-prag-i-kaskada", "v03-blok2-prag", "Prag i kaskada", "Čovjek ustaje kada udio susjeda koji stoje dostigne njegov prag."),
           ("3", "blok3-mreza-poznanstava", "v03-blok3-mreza", "Mreža poznanstava", "Uticaj se prenosi preko poznanika, a ne preko slučajnih prolaznika."),
           ("4", "blok4-preseljenje", "v03-blok4-preseljenje", "Preseljenje", "Čovjek se preseljava ako je udio sličnih susjeda manji od traženog."),
           ("5", "blok5-ustanova", "v03-blok5-ustanova", "Iskustvo s ustanovom", "Iskustvo s ustanovom stiče se posjetom; razgovor prenosi informacije o njemu."),
           ("6", "blok6-kazna", "v03-blok6-kazna", "Kontrola i kazna", "Prekršaj bez kazne povećava sklonost kršenju, a kazna je smanjuje.")]

def v03(p):
    return (grupa("Prezentacije i materijali", [
        k(p + "prezentacije/v03-interakcije.html", "Interakcije u modelu", "Rezultat i zadatak modela stava, C# (this i myself), četiri bloka interakcije, model na papiru (28 slajdova)."),
        k(p + "v03-blokovi-interakcije.html", "Blokovi interakcije", "Šest tipičnih interakcija: simulacije, mjerenja, kod u NetLogu i C#, obrazac za model na papiru."),
        k(p + "MiS-vjezbe-03-v3.zip", "Svi materijali (ZIP, 17 MB)", "Stranice, prezentacija (PPTX i PDF), NetLogo modeli, mjerenja i C# projekat netlogo-kroz-csharp.")])
      + grupa("Mini-prezentacije", [k(f"{p}blokovi/{b}.html", f"{n}. {t}", o) for n, b, _, t, o in BLOKOVI])
      + grupa("Isti modeli u NetLogo Webu (oko 5 MB po stranici)", [k(f"{p}netlogo-web/{m}.html", f"{n}. {t}", "Model se pokreće u web pregledniku, bez instalacije.") for n, _, m, t, _ in BLOKOVI])
      + grupa("Modeli za NetLogo 7.0.4", [k(f"{p}modeli/{m}.nlogox", f"{m}.nlogox", f"Blok {n}: {t.lower()}.") for n, _, m, t, _ in BLOKOVI]))

def v04(p):
    return grupa("Prezentacija", [
        k(p + "prezentacije/v04-tema-tri-naroda.html", "Društvo s više naroda", "Seobe i mješovitost mjesta, na primjeru BiH: kostur modela, 12 varijanti teme, simulacija zarade i etničke pripadnosti u web pregledniku (15 slajdova).")])

def stranica(naslov, opis, tijelo, oznaka="Modeliranje i simulacije · FIT UNMO 2026/27"):
    return f"""<!doctype html>
<html lang="bs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{naslov}</title>
<meta name="description" content="{opis}">
{CSS}
</head>
<body>
<main>
  <span class="oznaka">{oznaka}</span>
{tijelo}
  <footer>Modeliranje i simulacije, Fakultet informacijskih tehnologija, Univerzitet „Džemal Bijedić“ u Mostaru, 2026/27.</footer>
</main>
</body>
</html>
"""
uvod = '  <p class="siva">Stranice rade u web pregledniku, bez instalacije. Prezentacije se listaju strelicama ← →; opcija „Čitanje“ prikazuje sve slajdove na jednoj stranici. Modeli se otvaraju u NetLogu 7.0.4.</p>\n'
root = ('  <h1>Modeliranje i simulacije: materijali s vježbi</h1>\n' + uvod
        + '  <h2>Vježbe 2 (17.10.2026.): ponavljanje i prvi model</h2>\n' + v02("vjezbe-02/")
        + '  <h2>Vježbe 3 (24.10.2026.): interakcije</h2>\n' + v03("vjezbe-03/")
        + '  <h2>Vježbe 4 (31.10.2026.): tema „Društvo s više naroda“</h2>\n' + v04("vjezbe-04/"))
io.open(REPO + "/index.html", "w", encoding="utf-8", newline="\n").write(
    stranica("Modeliranje i simulacije 2026/27 — materijali s vježbi", "Materijali s vježbi: prezentacije, mini-prezentacije i NetLogo modeli.", root, "FIT UNMO · 2026/27"))
io.open(REPO + "/vjezbe-03/index.html", "w", encoding="utf-8", newline="\n").write(
    stranica("Vježbe 3 — materijali", "Modeliranje i simulacije, FIT UNMO 2026/27: materijali vježbi 3.",
             '  <h1>Vježbe 3: materijali</h1>\n  <p class="siva">Subota, 24.10.2026. ' + uvod.split('siva">')[1] + v03("")))
print("ok")
