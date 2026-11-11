"""Pravi početnu stranicu i indekse vježbi 3, 5 i 6 u istom izgledu kao vjezbe-02/index.html."""
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
def web(href, opis):
    return f'    <a href="{href}" target="_blank" rel="noopener"><b>Otvori u NetLogo Web</b><span>{opis}</span></a>\n'

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
        web("https://www.netlogoweb.org/launch#https://adil-fit-ba.github.io/modeliranje-i-simulacije-2026-27/vjezbe-02/modeli/v02-model-stav.nlogox", "u web pregledniku, bez instalacije. BehaviorSpace radi samo u NetLogu 7.0.4 na računaru."),
        k(p + "modeli/v02-zadatak.nlogox", "v02-zadatak.nlogox", "Model s praznim procedurama razgovaraj i slusaj-medije."),
        web("https://www.netlogoweb.org/launch#https://adil-fit-ba.github.io/modeliranje-i-simulacije-2026-27/vjezbe-02/modeli/v02-zadatak.nlogox", "u web pregledniku, bez instalacije. BehaviorSpace radi samo u NetLogu 7.0.4 na računaru.")]))

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
      + grupa("Isti modeli u NetLogo Webu (oko 5 MB po stranici)", [web(f"{p}netlogo-web/{m}.html", f"{n}. {t} — u web pregledniku, bez instalacije. BehaviorSpace radi samo u NetLogu 7.0.4 na računaru.") for n, _, m, t, _ in BLOKOVI])
      + grupa("Modeli za NetLogo 7.0.4", [k(f"{p}modeli/{m}.nlogox", f"{m}.nlogox", f"Blok {n}: {t.lower()}.") for n, _, m, t, _ in BLOKOVI]))

def v04(p):
    return grupa("Prezentacija", [
        k(p + "prezentacije/v04-tema-tri-naroda.html", "Društvo s više naroda", "Seobe i mješovitost mjesta, na primjeru BiH: kostur modela, 13 varijanti teme, simulacija zarade i etničke pripadnosti u web pregledniku (15 slajdova).")])

V05_CSS = """<style>
.tok-v05 { display: grid; gap: 0.8rem; margin: 1rem 0; padding: 0; list-style: none; }
.tok-v05 > li { padding: 1rem; background: var(--list); border: 1px solid var(--linija); border-radius: 6px; }
.tok-v05 h3 { margin: 0; }
.tok-v05 .satnica { display: block; margin-bottom: 0.25rem; color: var(--siva); font-size: 0.85rem; }
.tok-v05 a, .skok-na-v05 { color: var(--narandza); text-underline-offset: 0.16em; }
.tok-v05 .ulaz { display: inline-block; margin-top: 0.65rem; padding: 0.5rem 0.85rem;
  background: var(--narandza); color: var(--list); font-weight: 700; border-radius: 4px; }
.tok-v05 a:focus-visible, .skok-na-v05:focus-visible { outline: 2px solid var(--narandza); outline-offset: 3px; }
.tok-v05 .pratece { display: flex; flex-wrap: wrap; gap: 0.3rem 1rem; margin: 0.6rem 0 0;
  padding: 0; list-style: none; font-size: 0.92rem; }
</style>"""

def v05(p):
    deck = "prezentacije/v05-model-na-papiru-i-scenariji.html"
    koraci = [
        ("14:00–14:20", "Predviđanje i pravilo interakcije", "s1", "Počni ovdje · slajd 1", [
            (deck + "#v05-pravila", "Ilustracija pravila · slajd 2"),
            (deck + "#v05-raspodjele", "Raspodjele stavova · slajd 3"),
        ]),
        ("14:20–14:45", "Poređenje scenarija i BehaviorSpace", "s2", "Sastavljanje poređenja · slajd 4", [
            (deck + "#v05-uzorak", "Izvlačenje uzorka · slajd 5 (po potrebi)"),
            ("modeli/v05-model-stav-behaviorspace.nlogox", "NetLogo model"),
            ("https://www.netlogoweb.org/launch#https://adil-fit-ba.github.io/modeliranje-i-simulacije-2026-27/vjezbe-05/modeli/v05-model-stav-behaviorspace.nlogox", "Otvori u NetLogo Web"),
            (deck + "#s4", "Rezultati · slajd 7"),
        ]),
        ("14:45–15:15", "Model na papiru i lista provjere", "s5", "Primjer s alatom · slajd 8", [
            (deck + "#s7", "Ispravljeno poređenje · slajd 10"),
        ]),
        ("15:15–15:30", "Društvo s više naroda · samo za tu temu", "s9", "Uvod u završni blok · slajd 12", [
            (deck + "#s11", "Zajednički kontrolni scenarij · slajd 14"),
            (deck + "#s16", "Obrazac prijedloga · slajd 19"),
            (deck + "#s17", "Sljedeći koraci · slajd 20"),
        ]),
    ]
    dijelovi = [
        '  <p class="siva">Pratite blokove redom. Istaknuti link u svakom bloku otvara početni slajd.</p>',
        '  <ol class="tok-v05" role="list">',
    ]
    for broj, (vrijeme, naslov, slajd, ulaz, pratece) in enumerate(koraci, 1):
        veze = []
        for href, opis in pratece:
            if href.startswith("https://"):
                veze.append(f'        <li><a href="{href}" target="_blank" rel="noopener">{opis}</a>'
                            '<span> · u web pregledniku, bez instalacije. BehaviorSpace nije dostupan u NetLogo Webu. '
                            'Za eksperimente je potreban NetLogo 7.0.4 na računaru. Sam model možete istraživati u NetLogo Webu.</span></li>')
            else:
                veze.append(f'        <li><a href="{p}{href}">{opis}</a></li>')
        veze = "\n".join(veze)
        dijelovi.append(f"""    <li id="v05-blok-{broj}">
      <span class="satnica">{vrijeme}</span>
      <h3>{broj}. {naslov}</h3>
      <a class="ulaz" href="{p}{deck}#{slajd}">{ulaz}</a>
      <ul class="pratece" role="list">
{veze}
      </ul>
    </li>""")
    dijelovi.append("  </ol>")
    dijelovi.append(grupa("Za čitanje i pripremu", [
        k(p + "lekcija1-sta-pravilo-moze.html", "Lekcija 1 · Šta pravilo može proizvesti", "Pravilo interakcije, mjere i scenariji."),
        k(p + "lekcija2-jedno-pokretanje.html", "Lekcija 2 · Jedno pokretanje nije rezultat", "Slučajnost, ponavljanja i izvještavanje."),
        k(p + "upute-behaviorspace.html", "Upute za BehaviorSpace", "Postavke i pokretanje eksperimenta."),
        k(p + "mjerenja/v05-mediji.csv", "Mjerenja (CSV)", "Sačuvani rezultati eksperimenta."),
        k(p + "lista-provjere-model-na-papiru.html", "Lista provjere", "HTML lista za provjeru modela na papiru."),
        k(p + "lista-provjere-model-na-papiru.pdf", "Lista za štampu (PDF)", "Lista provjere u formatu A4."),
        k(p + "primjer-model-na-papiru-alat.html", "Primjer modela na papiru", "Pojednostavljen primjer (posuđivanje alata) i nedostaci koje treba riješiti."),
        k(p + "primjer-model-na-papiru-alat.pdf", "Primjer za štampu (PDF)", "Isti primjer na dvije strane A4."),
        k(p + "primjer-model-na-papiru-alat-prezentacija.html", "Primjer: prezentacija s ilustracijama", "Isti primjer redom kao dokument, sa simulacijom u web pregledniku."),
    ]).rstrip())
    return "\n".join(dijelovi) + "\n"

def v06(p):
    gore = "../" if p == "" else ""
    return grupa("Prezentacija", [
        k(p + "prezentacije/v06-od-papira-do-koda.html", "Od modela na papiru do koda", "Rečenica iz modela na papiru, kod i zašto baš tako, korak po korak A–E."),
    ]) + grupa("NetLogo modeli", [
        k(p + "modeli/v06-alat-pocetak.nlogox", "Početna datoteka", "Sučelje i procedure za dopunjavanje kroz korake A–E na času. Otvara se u NetLogu 7.0.4."),
        web("https://www.netlogoweb.org/launch#https://adil-fit-ba.github.io/modeliranje-i-simulacije-2026-27/vjezbe-06/modeli/v06-alat-pocetak.nlogox", "Početna datoteka u web pregledniku, bez instalacije. Za rad na času koristi se NetLogo 7.0.4 na računaru."),
        k(p + "modeli/v06-alat-svijet.nlogox", "Završena prva sedmica", "Svijet, centar, 100 domaćinstava, atributi i poznanstva. Služi za provjeru vlastite radne kopije."),
        web("https://www.netlogoweb.org/launch#https://adil-fit-ba.github.io/modeliranje-i-simulacije-2026-27/vjezbe-06/modeli/v06-alat-svijet.nlogox", "Završena prva sedmica u web pregledniku, bez instalacije. BehaviorSpace je dostupan samo u NetLogu 7.0.4 na računaru."),
        k(p + "modeli/v06-blokovi-za-lijepljenje.html", "Kod za copy-paste", "Tijela procedura za korake A–E, za nastavak rada u slučaju zaostajanja."),
    ]) + grupa("Za pripremu", [
        k(gore + "vjezbe-05/primjer-model-na-papiru-alat.html", "Primjer modela na papiru (vježbe 5)", "A4 opis primjera „Iznajmljivanje alata u naselju“ koji se kodira od vježbi 6."),
        k(gore + "vjezbe-05/primjer-model-na-papiru-alat-prezentacija.html", "Primjer: prezentacija s ilustracijama", "Prostor, akteri, tick i poređenja, sa simulacijom u web pregledniku."),
    ]) + '  <p class="siva">Pitanja o temama, prijavama, varijantama, sastavu timova i rokovima za teme šaljite Adilu Joldiću na adil@edu.fit.ba.</p>\n'

def stranica(naslov, opis, tijelo, oznaka="Modeliranje i simulacije · FIT UNMO 2026/27", dodatni_css=""):
    return f"""<!doctype html>
<html lang="bs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{naslov}</title>
<meta name="description" content="{opis}">
{CSS}{dodatni_css}
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
        + '  <p><a class="skok-na-v05" href="#vjezbe-05">Idi na tok vježbi 05</a></p>\n'
        + '  <h2>Vježbe 2 (17.10.2026.): ponavljanje i prvi model</h2>\n' + v02("vjezbe-02/")
        + '  <h2>Vježbe 3 (24.10.2026.): interakcije</h2>\n' + v03("vjezbe-03/")
        + '  <h2>Vježbe 4 (31.10.2026.): tema „Društvo s više naroda“</h2>\n' + v04("vjezbe-04/")
        + '  <h2 id="vjezbe-05">Vježbe 5 (07.11.2026.) · Model na papiru i scenariji</h2>\n' + v05("vjezbe-05/")
        + '  <h2 id="vjezbe-06">Vježbe 6 (13.11.2026.) · Kodiranje primjera: svijet i domaćinstva</h2>\n' + v06("vjezbe-06/"))
io.open(REPO + "/index.html", "w", encoding="utf-8", newline="\n").write(
    stranica("Modeliranje i simulacije 2026/27 — materijali s vježbi", "Materijali s vježbi: prezentacije, mini-prezentacije i NetLogo modeli.", root, "FIT UNMO · 2026/27", dodatni_css=V05_CSS))
io.open(REPO + "/vjezbe-03/index.html", "w", encoding="utf-8", newline="\n").write(
    stranica("Vježbe 3 — materijali", "Modeliranje i simulacije, FIT UNMO 2026/27: materijali vježbi 3.",
             '  <h1>Vježbe 3: materijali</h1>\n  <p class="siva">Subota, 24.10.2026. ' + uvod.split('siva">')[1] + v03("")))
io.open(REPO + "/vjezbe-05/index.html", "w", encoding="utf-8", newline="\n").write(
    stranica("Vježbe 5 — materijali", "Modeliranje i simulacije, FIT UNMO 2026/27. Model na papiru i scenariji.",
             '  <h1>Vježbe 5 · Model na papiru i scenariji</h1>\n  <p class="siva">Subota, 07.11.2026. u 14:00.</p>\n'
             + uvod + v05(""), dodatni_css=V05_CSS))
io.open(REPO + "/vjezbe-06/index.html", "w", encoding="utf-8", newline="\n").write(
    stranica("Vježbe 6 — materijali", "Modeliranje i simulacije, FIT UNMO 2026/27. Kodiranje primjera: svijet i domaćinstva.",
             '  <h1>Vježbe 6 · Kodiranje primjera: svijet i domaćinstva</h1>\n  <p class="siva">Petak, 13.11.2026. u 16:00. Vježbe drži asistent Adil Eminagić.</p>\n'
             + uvod + v06("")))
print("ok")
