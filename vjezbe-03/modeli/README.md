# Modeli blokova interakcije (vježbe 3)

| Fajl | Blok | BehaviorSpace u modelu |
|---|---|---|
| `v03-blok1-povjerenje.nlogox` | ograničeno povjerenje: model stava + obostran razgovor + `if abs razlika < prag` | `grupe` (500 tickova), `mediji` |
| `v03-blok2-prag.nlogox` | prag i kaskada: sala 31 × 31 bez omotavanja, svako vidi do 8 susjeda | `rasipanje` |
| `v03-blok3-mreza.nlogox` | mreža poznanstava: ljudi stoje; razgovor preko `link-neighbors` | `daleke-veze` (500 tickova) |
| `v03-blok4-preseljenje.nlogox` | preseljenje (Schelling): torus 41 × 41, gustina 70% | `trazeni-udio` |
| `v03-blok5-ustanova.nlogox` | mjesto s iskustvom: ustanove su patchevi (`patches-own [ ustanova? ]`); generator `izvor/napravi_model_b5.py` | `iskustva` |
| `v03-blok6-kazna.nlogox` | kontrola i kazna: sklonost kršenju pravila, vjerovatnoća kontrole; generator `izvor/napravi_model_b6.py` | `kontrola` |

Eksperimenti u modelima imaju po 2 pokretanja i služe za provjeru uživo. Brojke za materijale su iz
`mjerenja/` (10–200 pokretanja po vrijednosti).

## izvor/

| Skripta | Šta radi |
|---|---|
| `napravi_modele.py` | pravi sva četiri `.nlogox`; NetLogo kod je u njoj (`KOD_1` … `KOD_4`); oblici se uzimaju iz `v02-model-stav.nlogox` (u ovoj mapi) |
| `mjeri.py` | pokreće BehaviorSpace headless (`NetLogo_Console.exe`) i čita tabelu |
| `mjerenja.py` | sva konačna mjerenja i slike (`export-view`, fiksni random-seed) → `mjerenja/rezultati.json`, `rezultati.md`, `slike/` |
| `napravi_html.py` | sklapa `../v03-blokovi-interakcije.html` iz `html/stranica.html`, `html/sim.js`, `html/ui.js`, mjerenja, NetLogo koda i C# koda iz `../materijali/netlogo-kroz-csharp/Blokovi/` (`html/csharp-izvodi.json`) |
| `html/test-sim.js` | `node test-sim.js`: poredi simulaciju u web pregledniku (JavaScript) s NetLogo mjerenjima |

Redoslijed nakon izmjene modela: `napravi_modele.py` → `mjerenja.py` → `napravi_html.py`; C# u
`netlogo-kroz-csharp/Blokovi/` uskladiti ručno.

## Napomene

- **Simulacija u web pregledniku je ilustracija:** isti kod prepisan u JavaScript (`html/sim.js`),
  bez NetLoga u pozadini. Prema `test-sim.js` daje iste raspone kao NetLogo; brojke u tekstu i na
  grafikonima stranice su iz NetLoga.
- **Blok 2 traži velike uzorke:** ishod je „sve ili ništa“, pa je vjerovatnoća talasa mjerena na
  200 pokretanja po vrijednosti. Uz 50 pokretanja isti uslov je dao 27/50, a uz 200 dao je 76/200
  i 92/200.
- **Tačka 3 zadatka v02 (obostran razgovor):** `t3_*` u `rezultati.json`, 20 pokretanja. Razlika
  prema jednosmjernom razgovoru je manja od rasipanja između pokretanja.

## Mini-prezentacije i NetLogo Web (24.10.2026.)

- `../blokovi/blokN-*.html`: samostalna mini-prezentacija za svaki od šest blokova (10–11 slajdova; „Prezentacija“ i
  „Čitanje“). Šabloni su `izvor/blokovi/blokN.html`, a sklapa ih `izvor/napravi_blokove.py` (dogovor o šablonu je u
  zaglavlju skripta). Podaci: `izvor/putanje_b1.py`, `izvor/podaci_b2.py`, `podaci_b3.py`, `podaci_b4.py` →
  `mjerenja/putanje-b1.json`, `podaci-b2…b4.json`; blokovi 5 i 6 imaju svoje skripte (`mjerenja_b5.py`,
  `mjerenja_b6.py`) i rezultate (`mjerenja/rezultati-b5.json`, `rezultati-b6.json`, `podaci-b5.json`, `podaci-b6.json`).
- `../netlogo-web/v03-blokN-*.html`: isti modeli u NetLogo Webu (pravi NetLogo u web pregledniku, bez interneta). Pravi ih
  `izvor/napravi_netlogo_web.py <standalone.html>` za sve `v03-blok*.nlogox`; predložak je
  https://www.netlogoweb.org/standalone (~5 MB).
- Slike i zapisi u mini-prezentacijama su pojedinačna NetLogo pokretanja s navedenim random-seed; brojke u tekstu su iz
  mjerenja (10–200 pokretanja po vrijednosti).
- VS Code Live Server ubacuje svoj skript ispred prvog `</body>` u fajlu. U NetLogo Webu se `</body>` pojavljuje i u
  JavaScript stringovima, pa je to razbijalo stranicu („Ractive is not defined“). `napravi_netlogo_web.py` zato
  unutar `<script>` piše `<\/body>` i `<\/head>` i provjerava da u fajlu ostane samo jedan pravi `</body>`
  (ispravljeno 24.10.2026., provjereno kroz Live Server).
