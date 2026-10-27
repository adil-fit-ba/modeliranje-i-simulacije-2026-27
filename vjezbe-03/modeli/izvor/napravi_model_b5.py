"""Pravi model bloka 5 (mjesto s iskustvom: ustanova kao patch) za vježbe 3 (NetLogo 7.0.4, .nlogox).

Pomoćne funkcije (widgeti, oblici, eksperimenti) su iz napravi_modele.py; uvoz tog modula ne piše fajlove.
Pokretanje:  python -I napravi_model_b5.py
"""
import io, os, sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from napravi_modele import (MODELI, model, view, switch, buttons, plot, monitor, experiment, sliders_from,
                            PLAVA, ZELENA, CRVENA, SIVA)

KOD_5 = r"""
;; ============================================================
;; VJEŽBE 3 — BLOK 5: MJESTO S ISKUSTVOM (ustanova kao patch)
;; Modeliranje i simulacije, FIT UNMO, 2026/27
;; Ustanove su patchevi (mjesta koja stoje). Ko stane na ustanovu, ima iskustvo:
;; loše s vjerovatnoćom udio-losih-iskustava, inače dobro. Iskustvo mijenja povjerenje.
;; Razgovor (kao u modelu stava s vježbi 2) prenosi iskustvo i na one koji u ustanovi nisu bili.
;; Jedan tick = jedna sedmica
;; ============================================================

breed [ ljudi covjek ]      ;; pokretni agenti

patches-own [
  ustanova?     ;; true na mjestu ustanove (šalter, ambulanta, ured)
]

ljudi-own [
  povjerenje    ;; 0 (nema povjerenja u ustanove) do 1 (puno povjerenje)
  integritet    ;; 0 (lako se mijenja) do 1 (ne mijenja se)
  posjeta       ;; koliko puta je čovjek bio u ustanovi
]

globals [
  prosjecno-povjerenje
  udio-povjerljivih     ;; povjerenje > 0,6
  udio-posjetilaca      ;; bar jednom bili u ustanovi
]

;; ---------- postavljanje ----------

to setup
  clear-all
  ask patches [ set ustanova? false ]
  ask n-of broj-ustanova patches [
    set ustanova? true
    set pcolor orange
  ]
  create-ljudi broj-ljudi [
    setxy random-xcor random-ycor
    set shape "person"
    set size 1.5
    set povjerenje pocetno-povjerenje     ;; niko još nema iskustva s ustanovom
    set integritet random-float 1
    set posjeta 0
    oboji
  ]
  update-mjere
  reset-ticks
end

;; ---------- jedan korak vremena ----------

to go
  ask ljudi [
    kreni
    if [ ustanova? ] of patch-here [ iskustvo ]    ;; patch ispod čovjeka
    if razgovor? [ razgovaraj ]
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

to iskustvo
  set posjeta posjeta + 1
  ifelse random-float 1 < udio-losih-iskustava
    [ set povjerenje povjerenje + (0 - povjerenje) * (1 - integritet) * snaga-iskustva ]   ;; loše: prema 0
    [ set povjerenje povjerenje + (1 - povjerenje) * (1 - integritet) * snaga-iskustva ]   ;; dobro: prema 1
end

to razgovaraj
  let sagovornik one-of other ljudi in-radius domet
  if sagovornik != nobody [
    let razlika ([ povjerenje ] of sagovornik) - povjerenje
    set povjerenje povjerenje + razlika * (1 - integritet) * uticaj
  ]
end

to oboji
  ifelse povjerenje > 0.6
    [ set color blue ]
    [ ifelse povjerenje < 0.4
        [ set color red ]
        [ set color gray ] ]
end

;; ---------- mjere (izlaz modela) ----------

to update-mjere
  set prosjecno-povjerenje mean [ povjerenje ] of ljudi
  set udio-povjerljivih (count ljudi with [ povjerenje > 0.6 ]) / (count ljudi)
  set udio-posjetilaca (count ljudi with [ posjeta > 0 ]) / (count ljudi)
end

;; prosječno povjerenje onih koji su bili u ustanovi i onih koji nisu (−1 ako takvih nema)
to-report povjerenje-posjetilaca
  let p ljudi with [ posjeta > 0 ]
  report ifelse-value any? p [ mean [ povjerenje ] of p ] [ -1 ]
end

to-report povjerenje-ostalih
  let p ljudi with [ posjeta = 0 ]
  report ifelse-value any? p [ mean [ povjerenje ] of p ] [ -1 ]
end
"""

INFO_5 = """
## Blok 5: mjesto s iskustvom (ustanova kao patch)

**Pravilo (model na papiru):** Kada čovjek stane na mjesto ustanove (šalter, ambulanta, ured): s vjerovatnoćom `udio-losih-iskustava` iskustvo je loše i povjerenje mu se približi 0; inače je dobro i povjerenje se približi 1, zavisno od integriteta. Uz uključen `razgovor?` ljudi razgovaraju kao u modelu stava s vježbi 2, pa se iskustvo prenosi i na one koji u ustanovi nisu bili.

**Šta pokazuje:** iskustvo ima samo onaj ko dođe u ustanovu, a razgovor ga širi na cijelo društvo.

Ustanove su patchevi: mjesta koja stoje i imaju svoju varijablu (`patches-own [ ustanova? ]`). Čovjek pita patch ispod sebe: `[ ustanova? ] of patch-here`.

Mjere: `prosjecno-povjerenje`, `udio-povjerljivih` (povjerenje > 0,6), `udio-posjetilaca` (bar jednom u ustanovi), reporteri `povjerenje-posjetilaca` i `povjerenje-ostalih`.

Vježbe 3, Modeliranje i simulacije, FIT UNMO, 2026/27.
"""

s5, y = sliders_from([
    ("udio-losih-iskustava", 0, 1, 0.05, 0.7),
    ("pocetno-povjerenje", 0, 1, 0.05, 0.5),
    ("broj-ustanova", 1, 40, 1, 20),
    ("snaga-iskustva", 0, 1, 0.05, 0.6),
    ("broj-ljudi", 10, 500, 10, 200),
    ("domet", 1, 10, 0.5, 3, "patches"),
    ("uticaj", 0, 1, 0.05, 0.2),
])
W5 = [view()] + s5 + [buttons(y + 5), switch("razgovor?", True, y + 55),
    plot("prosjecno povjerenje", 10, [("svi", "plot prosjecno-povjerenje", PLAVA, 0, 1.0),
                                      ("bili u ustanovi", "if povjerenje-posjetilaca >= 0 [ plot povjerenje-posjetilaca ]", ZELENA, 0, 1.0),
                                      ("nisu bili", "if povjerenje-ostalih >= 0 [ plot povjerenje-ostalih ]", SIVA, 0, 1.0)],
         yaxis="povjerenje"),
    plot("udio", 210, [("povjerljivi (> 0,6)", "plot udio-povjerljivih", PLAVA, 0, 1.0),
                       ("bili u ustanovi", "plot udio-posjetilaca", CRVENA, 0, 1.0)], yaxis="udio"),
    monitor("prosjecno povjerenje", "prosjecno-povjerenje", 740, 410),
    monitor("udio povjerljivih", "udio-povjerljivih", 910, 410),
    monitor("bili u ustanovi", "udio-posjetilaca", 740, 475),
    monitor("ticks (sedmica)", "ticks", 910, 475, 0)]
E5 = [experiment("iskustva", 2, 150, ["prosjecno-povjerenje", "udio-posjetilaca", "povjerenje-posjetilaca", "povjerenje-ostalih"],
                 [("udio-losih-iskustava", [0.3, 0.7]), ("razgovor?", ["false", "true"])])]

if __name__ == "__main__":
    put = os.path.join(MODELI, "v03-blok5-ustanova.nlogox")
    io.open(put, "w", encoding="utf-8", newline="\n").write(model(KOD_5, W5, INFO_5, E5))
    print("napravljen", put)
