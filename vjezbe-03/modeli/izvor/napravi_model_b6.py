"""Pravi model bloka 6 (kontrola i kazna) za vježbe 3: ../v03-blok6-kazna.nlogox (NetLogo 7.0.4).

Widgeti, oblici i XML dolaze iz napravi_modele.py (isti izgled kao blokovi 1–4).
Pokretanje:  python -I napravi_model_b6.py
"""
import io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import napravi_modele as M

KOD_6 = r"""
;; ============================================================
;; VJEŽBE 3 — BLOK 6: KONTROLA I KAZNA
;; Modeliranje i simulacije, FIT UNMO, 2026/27
;; Pravilo: ko prekrši pravilo, može biti kažnjen. Kazna smanjuje sklonost kršenju,
;; a prekršaj bez kazne je povećava.
;; Ideja: Becker (1968), odvraćanje kaznom
;; Jedan tick = jedna sedmica (jedna prilika za prekršaj po čovjeku)
;; ============================================================

breed [ ljudi covjek ]      ;; pokretni agenti

ljudi-own [
  sklonost      ;; 0 do 1: vjerovatnoća da čovjek prekrši pravilo kad ima priliku
  integritet    ;; 0 (lako se mijenja) do 1 (ne mijenja se)
  prekrsio?     ;; true ako je prekršio pravilo u ovom ticku
  kaznjen?      ;; true ako je u ovom ticku kažnjen
]

globals [
  prosjecna-sklonost
  udio-prekrsaja    ;; udio ljudi koji su prekršili pravilo u ovom ticku
  broj-kaznjenih    ;; broj kažnjenih u ovom ticku
]

;; ---------- postavljanje ----------

to setup
  clear-all
  create-ljudi broj-ljudi [
    setxy random-xcor random-ycor
    set shape "person"
    set size 1.5
    set sklonost random-float 1
    set integritet random-float 1
    set prekrsio? false
    set kaznjen? false
    oboji
  ]
  update-mjere
  reset-ticks
end

;; ---------- jedan korak vremena ----------

to go
  ask ljudi [
    kreni
    if razgovor? [ razgovaraj ]
    prilika
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

;; jedna prilika za prekršaj: prekrši? → kontrola? → kazna ili prekršaj bez kazne
to prilika
  set prekrsio? false
  set kaznjen? false
  if random-float 1 < sklonost [                      ;; prekrši s vjerovatnoćom sklonost
    set prekrsio? true
    ifelse random-float 1 < vjerovatnoca-kontrole [   ;; kontrola ga otkrije
      set kaznjen? true
      set sklonost max (list 0 (sklonost - jacina-kazne * (1 - integritet)))
    ] [                                               ;; prekršaj bez kazne
      set sklonost min (list 1 (sklonost + pomak-bez-kazne * (1 - integritet)))
    ]
  ]
end

;; razgovor kao u modelu stava s vježbi 2: sklonost se približi sklonosti sagovornika
to razgovaraj
  let sagovornik one-of other ljudi in-radius domet
  if sagovornik != nobody [
    let razlika ([ sklonost ] of sagovornik) - sklonost
    set sklonost sklonost + razlika * (1 - integritet) * uticaj
  ]
end

to oboji
  ifelse kaznjen?
    [ set color yellow ]
    [ ifelse sklonost > 0.75
        [ set color red ]
        [ ifelse sklonost < 0.25
            [ set color sky ]
            [ set color gray ] ] ]
end

;; ---------- mjere (izlaz modela) ----------

to update-mjere
  set prosjecna-sklonost mean [ sklonost ] of ljudi
  set udio-prekrsaja (count ljudi with [ prekrsio? ]) / (count ljudi)
  set broj-kaznjenih count ljudi with [ kaznjen? ]
end
"""

INFO_6 = """
## Blok 6: kontrola i kazna

**Pravilo (model na papiru):** Svake sedmice čovjek ima priliku da prekrši neko pravilo (npr. kućni red u zgradi ili zabranu pušenja u zatvorenom). Prekrši ga s vjerovatnoćom `sklonost`. Ako je prekršio, kontrola ga otkrije s vjerovatnoćom `vjerovatnoca-kontrole`: tada mu sklonost padne za `jacina-kazne` × (1 − integritet). Ako ga ne otkrije, sklonost mu poraste za `pomak-bez-kazne` × (1 − integritet).

**Šta pokazuje:** postoji prag u vjerovatnoći kontrole. Ispod praga sklonost raste, iznad praga pada. Prag zavisi od omjera: `pomak-bez-kazne` / (`pomak-bez-kazne` + `jacina-kazne`). Uz zadane vrijednosti (0,02 i 0,1) to je 0,02 / 0,12 ≈ 0,17.

Žuto: kažnjen u ovom ticku. Crveno: sklonost > 0,75. Plavo: sklonost < 0,25.

Ideja: G. S. Becker (1968), Crime and Punishment: An Economic Approach, Journal of Political Economy 76(2), 169-217.

Vježbe 3, Modeliranje i simulacije, FIT UNMO, 2026/27.
"""

s6, y = M.sliders_from([
    ("vjerovatnoca-kontrole", 0, 1, 0.01, 0.1),
    ("jacina-kazne", 0, 0.5, 0.01, 0.1),
    ("pomak-bez-kazne", 0, 0.2, 0.005, 0.02),
    ("broj-ljudi", 10, 500, 10, 200),
    ("domet", 1, 10, 0.5, 3, "patches"),
    ("uticaj", 0, 1, 0.05, 0.2),
])
W6 = [M.view()] + s6 + [M.buttons(y + 5), M.switch("razgovor?", False, y + 55),
    M.plot("prosjecna sklonost", 10, [("sklonost", "plot prosjecna-sklonost", M.CRVENA, 0, 1.0)], yaxis="sklonost"),
    M.plot("raspodjela sklonosti", 210, [("sklonost", "histogram [ sklonost ] of ljudi", M.SIVA, 1, 0.05)],
           ymin=0, ymax=40, xmin=0, xmax=1, xaxis="sklonost", yaxis="broj ljudi", auto_x=False, auto_y=True),
    M.monitor("prosjecna sklonost", "prosjecna-sklonost", 740, 410),
    M.monitor("udio prekrsaja", "udio-prekrsaja", 910, 410),
    M.monitor("kaznjenih (tick)", "broj-kaznjenih", 740, 475, 0),
    M.monitor("ticks (sedmica)", "ticks", 910, 475, 0)]
E6 = [M.experiment("kontrola", 2, 150, ["prosjecna-sklonost", "udio-prekrsaja"],
                   [("vjerovatnoca-kontrole", [0.05, 0.1, 0.2, 0.3])])]

if __name__ == "__main__":
    put = os.path.join(M.MODELI, "v03-blok6-kazna.nlogox")
    io.open(put, "w", encoding="utf-8", newline="\n").write(M.model(KOD_6, W6, INFO_6, E6))
    print("napravljen", put)
