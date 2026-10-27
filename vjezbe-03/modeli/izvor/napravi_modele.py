"""Pravi četiri modela blokova interakcije za vježbe 3 (NetLogo 7.0.4, .nlogox).

Oblici (turtle i link shapes) preuzimaju se iz ../../v02/modeli/v02-model-stav.nlogox.
Pokretanje:  python -I napravi_modele.py
"""
import io, os, re, sys
from xml.sax.saxutils import escape, quoteattr

sys.stdout.reconfigure(encoding="utf-8")
OVDJE = os.path.dirname(os.path.abspath(__file__))
MODELI = os.path.dirname(OVDJE)
BAZA = os.path.join(MODELI, "..", "..", "v02", "modeli", "v02-model-stav.nlogox")

baza = io.open(BAZA, encoding="utf-8").read()
OBLICI = re.search(r"  <turtleShapes>.*?</linkShapes>\n", baza, re.S).group(0)


# ---------- widgeti ----------

def slider(var, mn, mx, step, default, y, units="", x=9):
    return (f'    <slider x="{x}" step="{step}" y="{y}" max="{mx}" width="205" display="{var}" height="50" '
            f'min="{mn}" direction="Horizontal" default="{default}" variable="{var}" units="{units}"></slider>')

def switch(var, on, y, x=9):
    return (f'    <switch x="{x}" y="{y}" height="40" on="{"true" if on else "false"}" variable="{var}" '
            f'width="205" display="{var}"></switch>')

def buttons(y):
    return (f'    <button x="9" y="{y}" height="40" disableUntilTicks="false" forever="false" kind="Observer" width="95" display="SETUP">setup</button>\n'
            f'    <button x="112" y="{y}" height="40" disableUntilTicks="true" forever="true" kind="Observer" width="95" display="GO">go</button>')

def view(min_c=-20, max_c=20, patch=11.0, label="sedmica", wrap=True):
    size = int((max_c - min_c + 1) * patch) + 1
    w = "true" if wrap else "false"
    return (f'    <view x="230" wrappingAllowedX="{w}" y="10" frameRate="30.0" minPycor="{min_c}" height="{size}" '
            f'showTickCounter="true" patchSize="{patch}" fontSize="10" wrappingAllowedY="{w}" width="{size}" '
            f'tickCounterLabel="{label}" maxPycor="{max_c}" updateMode="1" maxPxcor="{max_c}" minPxcor="{min_c}"></view>')

def plot(title, y, pens, ymin=0.0, ymax=1.0, xmin=0.0, xmax=150.0, xaxis="tick", yaxis="",
         auto_x=True, auto_y=False, x=740, h=190, setup=""):
    p = "\n".join(
        f'      <pen interval="{iv}" mode="{mode}" display={quoteattr(name)} color="{color}" legend="true">\n'
        f'        <setup></setup>\n        <update>{escape(upd)}</update>\n      </pen>'
        for name, upd, color, mode, iv in pens)
    return (f'    <plot x="{x}" autoPlotX="{str(auto_x).lower()}" yMax="{ymax}" autoPlotY="{str(auto_y).lower()}" '
            f'yAxis="{yaxis}" y="{y}" xMin="{xmin}" height="{h}" legend="{"true" if len(pens) > 1 else "false"}" '
            f'xMax="{xmax}" yMin="{ymin}" width="330" xAxis="{xaxis}" display={quoteattr(title)}>\n'
            f'      <setup>{escape(setup)}</setup>\n      <update></update>\n{p}\n    </plot>')

def monitor(title, expr, x, y, prec=3):
    return (f'    <monitor x="{x}" precision="{prec}" y="{y}" height="60" fontSize="11" width="160" '
            f'display={quoteattr(title)}>{escape(expr)}</monitor>')

def experiment(name, reps, limit, metrics, values, every=False, setup="setup"):
    m = "\n".join(f"        <metric>{escape(x)}</metric>" for x in metrics)
    v = "\n".join(
        f'          <enumeratedValueSet variable="{var}">\n' +
        "\n".join(f'            <value value={quoteattr(str(val))}></value>' for val in vals) +
        "\n          </enumeratedValueSet>"
        for var, vals in values)
    return (f'    <experiment name="{name}" repetitions="{reps}" sequentialRunOrder="true" '
            f'runMetricsEveryStep="{str(every).lower()}" timeLimit="{limit}">\n'
            f'      <setup>{escape(setup)}</setup>\n      <go>go</go>\n      <metrics>\n{m}\n      </metrics>\n'
            f'      <subExperiments>\n        <subExperiment>\n{v}\n        </subExperiment>\n      </subExperiments>\n'
            f'    </experiment>')

def model(code, widgets, info, experiments, preview="setup repeat 100 [ go ]"):
    return ('<?xml version="1.0" encoding="utf-8"?>\n<model version="NetLogo 7.0.4" snapToGrid="false">\n'
            f'  <code><![CDATA[{code.strip()}\n]]></code>\n  <widgets>\n' + "\n".join(widgets) +
            f'\n  </widgets>\n  <info><![CDATA[{info.strip()}\n]]></info>\n' + OBLICI +
            f'  <previewCommands>{escape(preview)}</previewCommands>\n'
            '  <experiments>\n' + "\n".join(experiments) + '\n  </experiments>\n</model>\n')

def sliders_from(spec, y0=10):
    out, y = [], y0
    for var, mn, mx, step, default, *units in spec:
        out.append(slider(var, mn, mx, step, default, y, *units))
        y += 53
    return out, y

PLAVA, ZELENA, NARANDZASTA, CRVENA, SIVA = -13345367, -10899396, -955883, -2674135, -7500403


# ============================================================
# BLOK 1 — OGRANIČENO POVJERENJE
# ============================================================

KOD_1 = r"""
;; ============================================================
;; VJEŽBE 3 — BLOK 1: OGRANIČENO POVJERENJE
;; Modeliranje i simulacije, FIT UNMO, 2026/27
;; Polazi od modela stava s vježbi 2, uz tačku 3 zadatka (mijenja se i sagovornik).
;; Novo pravilo: razgovor mijenja stav samo ako se stavovi razlikuju manje od praga.
;; Ideja: Deffuant, Neau, Amblard i Weisbuch (2000)
;; Jedan tick = jedna sedmica
;; ============================================================

breed [ ljudi covjek ]      ;; pokretni agenti
breed [ mediji medij ]      ;; stacionarni agenti (izvor poruke)

ljudi-own [
  stav          ;; -1 (protiv) do +1 (za)
  integritet    ;; 0 (lako se mijenja) do 1 (ne mijenja se)
]

globals [
  prosjecan-stav
  udio-za
  broj-grupa
]

;; ---------- postavljanje ----------

to setup
  clear-all
  create-ljudi broj-ljudi [
    setxy random-xcor random-ycor
    set shape "person"
    set size 1.5
    set stav (random-float 2) - 1
    set integritet random-float 1
    oboji
  ]
  create-mediji broj-medija [
    setxy random-xcor random-ycor
    set shape "house"
    set size 3
    set color yellow
  ]
  update-mjere
  reset-ticks
end

;; ---------- jedan korak vremena ----------

to go
  ask ljudi [
    kreni
    razgovaraj
    if mediji-rade? [ slusaj-medije ]
    oboji
  ]
  update-mjere
  tick
end

;; ---------- ponašanje ----------

to kreni
  right random 360
  forward 1
end

to razgovaraj
  let sagovornik one-of other ljudi in-radius domet
  if sagovornik != nobody [
    let razlika ([ stav ] of sagovornik) - stav
    if abs razlika < prag [                       ;; NOVO: samo ako su stavovi dovoljno blizu
      let moj-stav stav                           ;; sačuvati prije promjene (tačka 3)
      set stav stav + razlika * (1 - integritet) * uticaj
      ask sagovornik [
        set stav stav + (moj-stav - stav) * (1 - integritet) * uticaj
        oboji
      ]
    ]
  ]
end

to slusaj-medije
  if any? mediji in-radius domet-medija [
    if abs (poruka-medija - stav) < prag [        ;; NOVO: isto pravilo vrijedi i za poruku medija
      set stav stav + (poruka-medija - stav) * (1 - integritet) * snaga-medija
    ]
  ]
end

to oboji
  ifelse stav > 0.2
    [ set color blue ]
    [ ifelse stav < -0.2
        [ set color red ]
        [ set color gray ] ]
end

;; ---------- mjere (izlaz modela) ----------

to update-mjere
  set prosjecan-stav mean [ stav ] of ljudi
  set udio-za (count ljudi with [ stav > 0.2 ]) / (count ljudi)
  set broj-grupa izbroji-grupe
end

;; Grupa = niz stavova (poredanih po veličini) u kojem su susjedne vrijednosti bliže od 0,1.
;; Broje se samo grupe s barem 5% ljudi.
to-report izbroji-grupe
  let s sort [ stav ] of ljudi
  let najmanje 0.05 * length s
  let grupe 0
  let velicina 1
  let i 1
  while [ i < length s ] [
    ifelse (item i s) - (item (i - 1) s) < 0.1
      [ set velicina velicina + 1 ]
      [ if velicina >= najmanje [ set grupe grupe + 1 ]
        set velicina 1 ]
    set i i + 1
  ]
  if velicina >= najmanje [ set grupe grupe + 1 ]
  report grupe
end
"""

INFO_1 = """
## Blok 1: ograničeno povjerenje

**Pravilo (model na papiru):** Kada čovjek sretne čovjeka: ako se njihovi stavovi razlikuju manje od `prag`, oba se približe jedan drugom, zavisno od svog integriteta; inače se ništa ne mijenja. Isto pravilo vrijedi i za poruku medija.

**Šta pokazuje:** mali prag daje više odvojenih grupa stavova, a veliki jednu. Mediji ne mijenjaju one čiji je stav daleko od poruke.

Model polazi od modela stava s vježbi 2 (tačka 3 zadatka: mijenja se i sagovornik). Novo je samo `if abs razlika < prag`.

Mjere: `udio-za` (stav > 0,2), `prosjecan-stav`, `broj-grupa` (grupe s barem 5% ljudi, susjedni stavovi bliže od 0,1).

Ideja: G. Deffuant, D. Neau, F. Amblard, G. Weisbuch (2000), Mixing beliefs among interacting agents, Advances in Complex Systems 3, 87-98.

Vježbe 3, Modeliranje i simulacije, FIT UNMO, 2026/27.
"""

s1, y = sliders_from([
    ("prag", 0.05, 2, 0.05, 0.5),
    ("broj-ljudi", 10, 500, 10, 200),
    ("broj-medija", 0, 10, 1, 4),
    ("domet", 1, 10, 0.5, 3, "patches"),
    ("uticaj", 0, 1, 0.05, 0.2),
    ("poruka-medija", -1, 1, 0.1, 1),
    ("snaga-medija", 0, 1, 0.05, 0.1),
    ("domet-medija", 1, 20, 1, 8, "patches"),
])
W1 = [view()] + s1 + [buttons(y + 5), switch("mediji-rade?", False, y + 55),
    plot("raspodjela stava", 10, [("stav", "histogram [ stav ] of ljudi", PLAVA, 1, 0.05)],
         ymin=0, ymax=40, xmin=-1, xmax=1, xaxis="stav", yaxis="broj ljudi", auto_x=False, auto_y=True),
    plot("udio za", 210, [("udio za", "plot udio-za", ZELENA, 0, 1.0)], yaxis="udio"),
    monitor("broj grupa", "broj-grupa", 740, 410, 0),
    monitor("udio za", "udio-za", 910, 410),
    monitor("prosjecan stav", "prosjecan-stav", 740, 475),
    monitor("ticks (sedmica)", "ticks", 910, 475, 0)]
E1 = [experiment("grupe", 2, 500, ["broj-grupa", "udio-za"],
                 [("prag", [0.1, 0.2, 0.5, 2]), ("mediji-rade?", ["false"])]),
      experiment("mediji", 2, 150, ["udio-za"],
                 [("prag", [0.2, 0.5, 2]), ("mediji-rade?", ["true"])])]


# ============================================================
# BLOK 2 — PRAG I KASKADA
# ============================================================

KOD_2 = r"""
;; ============================================================
;; VJEŽBE 3 — BLOK 2: PRAG I KASKADA
;; Modeliranje i simulacije, FIT UNMO, 2026/27
;; Sala: na svakom mjestu sjedi jedan čovjek i vidi svojih (do) 8 susjeda.
;; Pravilo: čovjek ustane kad je udio susjeda koji stoje barem njegov prag; ostaje stajati.
;; Ideja: Granovetter (1978)
;; Jedan tick = jedan krug odluke (nekoliko sekundi)
;; ============================================================

breed [ ljudi covjek ]

ljudi-own [
  aktivan?      ;; true kad je ustao (ostaje stajati)
  moj-prag      ;; udio susjeda koji stoje potreban da ustanem, 0 do 1
]

globals [
  udio-aktivnih
]

;; ---------- postavljanje ----------

to setup
  clear-all
  ask patches [
    sprout-ljudi 1 [
      set shape "person"
      set moj-prag ogranici (random-normal prosjek-praga rasipanje-praga)
      set aktivan? false
    ]
  ]
  ask n-of pokretaci ljudi [ set aktivan? true ]   ;; nekoliko ljudi ustane bez obzira na druge
  ask ljudi [ oboji ]
  update-mjere
  reset-ticks
end

to-report ogranici [ x ]
  report max (list 0 (min (list 1 x)))
end

;; ---------- jedan korak vremena ----------

to go
  ;; with prvo izabere sve koji ustaju (prema stanju na početku kruga), pa ih tek onda pita
  let ustaju ljudi with [ not aktivan? and udio-oko-mene >= moj-prag ]
  if not any? ustaju [ stop ]
  ask ustaju [
    set aktivan? true
    oboji
  ]
  update-mjere
  tick
end

;; ---------- ponašanje ----------

to-report udio-oko-mene
  let oko-mene ljudi-on neighbors
  report (count oko-mene with [ aktivan? ]) / (count oko-mene)
end

to oboji
  set color ifelse-value aktivan? [ orange ] [ gray - 2 ]
end

;; ---------- mjere (izlaz modela) ----------

to update-mjere
  set udio-aktivnih (count ljudi with [ aktivan? ]) / (count ljudi)
end
"""

INFO_2 = """
## Blok 2: prag i kaskada

**Pravilo (model na papiru):** U sali na svakom mjestu sjedi jedan čovjek i vidi svojih (do) 8 susjeda. Kada je udio susjeda koji stoje barem njegov `moj-prag`, i on ustane i ostaje stajati. Nekoliko pokretača ustane bez obzira na druge.

**Šta pokazuje:** isti prosječni prag može dati ili talas koji zahvati gotovo cijelu salu, ili gotovo ništa. Odlučuje raspodjela pragova (`rasipanje-praga`), ne samo prosjek.

Pragovi se dodjeljuju iz normalne raspodjele (`prosjek-praga`, `rasipanje-praga`), ograničeni na 0 do 1. Sala nema omotavanje: ljudi na rubu imaju manje susjeda. Model se zaustavi kad više niko ne ustaje.

Primjeri pojava s pragom: stojeći aplauz, pridruživanje protestu (Granovetterov primjer).

Ideja: M. Granovetter (1978), Threshold Models of Collective Behavior, American Journal of Sociology 83(6), 1420-1443.

Vježbe 3, Modeliranje i simulacije, FIT UNMO, 2026/27.
"""

s2, y = sliders_from([
    ("prosjek-praga", 0, 1, 0.05, 0.3),
    ("rasipanje-praga", 0, 0.5, 0.01, 0.1),
    ("pokretaci", 0, 100, 1, 10),
])
W2 = [view(-15, 15, 15.0, label="krug", wrap=False)] + s2 + [buttons(y + 5),
    plot("udio aktivnih", 10, [("udio aktivnih", "plot udio-aktivnih", NARANDZASTA, 0, 1.0)],
         xmax=30.0, yaxis="udio"),
    plot("raspodjela pragova", 210, [("prag", "histogram [ moj-prag ] of ljudi", SIVA, 1, 0.05)],
         ymin=0, ymax=300, xmin=0, xmax=1, xaxis="prag", yaxis="broj ljudi", auto_x=False, auto_y=True),
    monitor("udio aktivnih", "udio-aktivnih", 740, 410),
    monitor("ticks (krug)", "ticks", 910, 410, 0)]
E2 = [experiment("rasipanje", 2, 200, ["udio-aktivnih", "ticks"],
                 [("rasipanje-praga", [0.05, 0.1, 0.2, 0.3])])]

# ============================================================
# BLOK 3 — MREŽA POZNANSTAVA
# ============================================================

KOD_3 = r"""
;; ============================================================
;; VJEŽBE 3 — BLOK 3: MREŽA POZNANSTAVA (links)
;; Modeliranje i simulacije, FIT UNMO, 2026/27
;; Polazi od modela stava s vježbi 2. Ljudi ne šetaju; razgovaraju samo s poznanicima.
;; Poznanici su najbliži ljudi; dio veza vodi do nekoga bilo gdje u svijetu.
;; Ideja (daleke veze): Watts i Strogatz (1998)
;; Jedan tick = jedna sedmica
;; ============================================================

breed [ ljudi covjek ]      ;; ljudi stoje (kuća, posao)
breed [ mediji medij ]      ;; stacionarni agenti (izvor poruke)

ljudi-own [
  stav          ;; -1 (protiv) do +1 (za)
  integritet    ;; 0 (lako se mijenja) do 1 (ne mijenja se)
]

globals [
  prosjecan-stav
  udio-za
]

;; ---------- postavljanje ----------

to setup
  clear-all
  create-ljudi broj-ljudi [
    setxy random-xcor random-ycor
    set shape "person"
    set size 1.5
    set stav (random-float 2) - 1
    set integritet random-float 1
    oboji
  ]
  napravi-mrezu
  create-mediji broj-medija [
    setxy random-xcor random-ycor
    set shape "house"
    set size 3
    set color yellow
  ]
  update-mjere
  reset-ticks
end

to napravi-mrezu
  ;; svako se upozna s nekoliko najbližih ljudi (myself = onaj koji traži poznanike)
  ask ljudi [
    create-links-with min-n-of broj-veza other ljudi [ distance myself ]
  ]
  ;; dio veza se zamijeni vezom s nekim bilo gdje u svijetu
  ask links [
    if random-float 1 < udio-dalekih-veza [
      let a end1
      let novi one-of ljudi with [ self != a and not link-neighbor? a ]
      if novi != nobody [
        ask a [ create-link-with novi ]
        die
      ]
    ]
  ]
  ask links [
    set color gray - 2
    set hidden? not prikazi-veze?
  ]
end

;; ---------- jedan korak vremena ----------

to go
  ask ljudi [
    razgovaraj
    if mediji-rade? [ slusaj-medije ]
    oboji
  ]
  update-mjere
  tick
end

;; ---------- ponašanje ----------

to razgovaraj
  let sagovornik one-of link-neighbors            ;; NOVO: poznanik, a ne ko prođe blizu
  if sagovornik != nobody [
    let razlika ([ stav ] of sagovornik) - stav
    set stav stav + razlika * (1 - integritet) * uticaj
  ]
end

to slusaj-medije
  if any? mediji in-radius domet-medija [
    set stav stav + (poruka-medija - stav) * (1 - integritet) * snaga-medija
  ]
end

to oboji
  ifelse stav > 0.2
    [ set color blue ]
    [ ifelse stav < -0.2
        [ set color red ]
        [ set color gray ] ]
end

;; ---------- mjere (izlaz modela) ----------

to update-mjere
  set prosjecan-stav mean [ stav ] of ljudi
  set udio-za (count ljudi with [ stav > 0.2 ]) / (count ljudi)
end
"""

INFO_3 = """
## Blok 3: mreža poznanstava (links)

**Pravilo (model na papiru):** Ljudi ne šetaju. Svako ima poznanike: najbliže ljude, a dio veza (`udio-dalekih-veza`) vodi do nekoga bilo gdje u svijetu. Kada čovjek razgovara, sagovornik je jedan od njegovih poznanika, a ne neko ko prođe blizu. Poruku medija čuju samo oni koji žive blizu kuće.

**Šta pokazuje:** mali udio dalekih veza prenosi poruku daleko od izvora. Ko je s kim povezan je odluka modela i traži podatke.

Novi NetLogo pojmovi: `links`, `create-links-with`, `link-neighbors`, `link-neighbor?`, `end1`, `min-n-of ... [ distance myself ]`.

Ideja dalekih veza: D. J. Watts, S. H. Strogatz (1998), Collective dynamics of 'small-world' networks, Nature 393, 440-442.

Vježbe 3, Modeliranje i simulacije, FIT UNMO, 2026/27.
"""

s3, y = sliders_from([
    ("udio-dalekih-veza", 0, 1, 0.01, 0),
    ("broj-veza", 1, 10, 1, 3),
    ("broj-ljudi", 10, 500, 10, 200),
    ("broj-medija", 0, 10, 1, 2),
    ("uticaj", 0, 1, 0.05, 0.2),
    ("poruka-medija", -1, 1, 0.1, 1),
    ("snaga-medija", 0, 1, 0.05, 0.1),
    ("domet-medija", 1, 20, 1, 5, "patches"),
])
W3 = [view()] + s3 + [buttons(y + 5), switch("mediji-rade?", True, y + 55), switch("prikazi-veze?", True, y + 100),
    plot("udio za", 10, [("udio za", "plot udio-za", ZELENA, 0, 1.0)], yaxis="udio"),
    plot("prosjecan stav", 210, [("prosjecan stav", "plot prosjecan-stav", PLAVA, 0, 1.0)],
         ymin=-1.0, yaxis="stav"),
    monitor("udio za", "udio-za", 740, 410),
    monitor("prosjecan stav", "prosjecan-stav", 910, 410),
    monitor("poznanika po osobi", "mean [ count link-neighbors ] of ljudi", 740, 475, 1),
    monitor("ticks (sedmica)", "ticks", 910, 475, 0)]
E3 = [experiment("daleke-veze", 2, 500, ["udio-za"],
                 [("udio-dalekih-veza", [0, 0.05, 0.2, 1])])]


# ============================================================
# BLOK 4 — PRESELJENJE
# ============================================================

KOD_4 = r"""
;; ============================================================
;; VJEŽBE 3 — BLOK 4: PRESELJENJE
;; Modeliranje i simulacije, FIT UNMO, 2026/27
;; Pravilo: ko među susjedima ima manje sličnih od traženog udjela, preseli se.
;; Ideja: Schelling (1971); sličan model je u Models Library: Social Science > Segregation
;; Jedan tick = jedan mjesec
;; ============================================================

breed [ ljudi covjek ]

ljudi-own [
  grupa             ;; 0 ili 1 (bilo koja osobina po kojoj se ljudi razlikuju)
  slicnih           ;; broj susjeda iz iste grupe
  susjeda           ;; ukupan broj susjeda
  zadovoljan?
]

globals [
  prosjecno-slicnih     ;; prosječan udio sličnih među susjedima
  udio-nezadovoljnih
]

;; ---------- postavljanje ----------

to setup
  clear-all
  ask n-of (round (gustina * count patches)) patches [
    sprout-ljudi 1 [
      set shape "square"
      set grupa random 2
      set color ifelse-value grupa = 0 [ sky ] [ orange ]
    ]
  ]
  procijeni
  update-mjere
  reset-ticks
end

;; ---------- jedan korak vremena ----------

to go
  if not any? ljudi with [ not zadovoljan? ] [ stop ]
  ask ljudi with [ not zadovoljan? ] [ preseli-se ]
  procijeni
  update-mjere
  tick
end

;; ---------- ponašanje ----------

to procijeni
  ask ljudi [
    let oko-mene ljudi-on neighbors
    set susjeda count oko-mene
    set slicnih count oko-mene with [ grupa = [ grupa ] of myself ]
    set zadovoljan? slicnih >= trazeni-udio-slicnih * susjeda
  ]
end

to preseli-se
  move-to one-of patches with [ not any? ljudi-here ]
end

;; ---------- mjere (izlaz modela) ----------

to update-mjere
  let sa-susjedima ljudi with [ susjeda > 0 ]
  set prosjecno-slicnih mean [ slicnih / susjeda ] of sa-susjedima
  set udio-nezadovoljnih (count ljudi with [ not zadovoljan? ]) / (count ljudi)
end
"""

INFO_4 = """
## Blok 4: preseljenje

**Pravilo (model na papiru):** Svaki čovjek pripada jednoj od dvije grupe. Kada među svojih (do 8) susjeda ima manje sličnih od `trazeni-udio-slicnih`, preseli se na slučajno prazno mjesto.

**Šta pokazuje:** i blaga sklonost (npr. „želim da barem trećina susjeda bude kao ja“) daje susjedstva u kojima je velika većina iz iste grupe. Mjera je `prosjecno-slicnih`.

Model se zaustavi kad su svi zadovoljni.

Ideja: T. C. Schelling (1971), Dynamic Models of Segregation, Journal of Mathematical Sociology 1(2), 143-186. Sličan model je u NetLogo Models Library: Social Science > Segregation (U. Wilensky, 1997).

Vježbe 3, Modeliranje i simulacije, FIT UNMO, 2026/27.
"""

s4, y = sliders_from([
    ("trazeni-udio-slicnih", 0, 1, 0.05, 0.3),
    ("gustina", 0.5, 0.95, 0.05, 0.7),
])
W4 = [view(label="mjesec")] + s4 + [buttons(y + 5),
    plot("prosjecno slicnih", 10, [("slicnih", "plot prosjecno-slicnih", PLAVA, 0, 1.0)],
         xmax=50.0, yaxis="udio"),
    plot("udio nezadovoljnih", 210, [("nezadovoljni", "plot udio-nezadovoljnih", CRVENA, 0, 1.0)],
         xmax=50.0, yaxis="udio"),
    monitor("prosjecno slicnih", "prosjecno-slicnih", 740, 410),
    monitor("udio nezadovoljnih", "udio-nezadovoljnih", 910, 410),
    monitor("ticks (mjesec)", "ticks", 740, 475, 0)]
E4 = [experiment("trazeni-udio", 2, 300, ["prosjecno-slicnih", "udio-nezadovoljnih", "ticks"],
                 [("trazeni-udio-slicnih", [0.3, 0.5, 0.75])])]


MODELI_SPEC = [
    ("v03-blok1-povjerenje.nlogox", KOD_1, W1, INFO_1, E1),
    ("v03-blok2-prag.nlogox", KOD_2, W2, INFO_2, E2),
    ("v03-blok3-mreza.nlogox", KOD_3, W3, INFO_3, E3),
    ("v03-blok4-preseljenje.nlogox", KOD_4, W4, INFO_4, E4),
]

if __name__ == "__main__":
    for ime, kod, w, info, e in MODELI_SPEC:
        put = os.path.join(MODELI, ime)
        io.open(put, "w", encoding="utf-8", newline="\n").write(model(kod, w, info, e))
        print("napravljen", ime)
