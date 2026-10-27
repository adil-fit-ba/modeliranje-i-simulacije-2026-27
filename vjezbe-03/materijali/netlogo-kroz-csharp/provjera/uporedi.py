# Poređenje NetLogo i C# pokretanja Wolf Sheep Predation (verzija s travom).
# Upotreba: python uporedi.py rezultati-netlogo.csv [rezultati-csharp.csv ...]
# Čita BehaviorSpace tabelu (NetLogo) ili CSV iz "dotnet run -- eksperiment" (C#).
import csv, sys, statistics as st
sys.stdout.reconfigure(encoding="utf-8")


def ucitaj(put):
    with open(put, encoding="utf-8") as f:
        redovi = list(csv.reader(f))
    if redovi[0][0].startswith("BehaviorSpace"):
        zag = redovi[6]
        i_run, i_t = zag.index("[run number]"), zag.index("[step]")
        i_s, i_w, i_g = zag.index("count sheep"), zag.index("count wolves"), zag.index("count grass")
        podaci = redovi[7:]
    else:
        zag = redovi[0]
        i_run, i_t, i_s, i_w, i_g = (zag.index(k) for k in ("run", "tick", "sheep", "wolves", "grass"))
        podaci = redovi[1:]
    runs = {}
    for r in podaci:
        runs.setdefault(int(r[i_run]), {})[int(r[i_t])] = (int(r[i_s]), int(r[i_w]), int(r[i_g]))
    return runs


def sazetak(ime, runs):
    od = 100  # prvih 100 tickova je prelazni period od početnog stanja
    s_m, w_m, g_m, s_mx, s_mn, w_mx, w_mn, izumrli, kraj = [], [], [], [], [], [], [], 0, []
    for r, serija in sorted(runs.items()):
        t = [k for k in sorted(serija) if k >= od]
        s = [serija[k][0] for k in t]; w = [serija[k][1] for k in t]; g = [serija[k][2] for k in t]
        s_m.append(st.mean(s)); w_m.append(st.mean(w)); g_m.append(st.mean(g))
        s_mx.append(max(s)); s_mn.append(min(s)); w_mx.append(max(w)); w_mn.append(min(w))
        zadnji = max(serija)
        kraj.append(zadnji)
        if serija[zadnji][1] == 0:
            izumrli += 1
    # kašnjenje vukova za ovcama: pomak (u tickovima) s najvećom korelacijom ovce(t) i vukovi(t + pomak)
    kasnjenja = []
    for r, serija in sorted(runs.items()):
        t = [k for k in sorted(serija) if k >= od]
        s = [serija[k][0] for k in t]; w = [serija[k][1] for k in t]
        kasnjenja.append(max(range(0, 101), key=lambda d: st.correlation(s[:len(s) - d], w[d:])))
    n = len(runs)
    print(f"== {ime}: {n} pokretanja, zadnji tick {min(kraj)}–{max(kraj)}; vrijednosti od ticka {od}")
    print(f"  vukovi kasne za ovcama (tickova): {min(kasnjenja)}–{max(kasnjenja)} (sredina {st.mean(kasnjenja):.0f})")
    f = lambda a: f"{min(a):.0f}–{max(a):.0f} (sredina {st.mean(a):.0f})"
    print(f"  prosjek ovaca po pokretanju : {f(s_m)}")
    print(f"  prosjek vukova po pokretanju: {f(w_m)}")
    print(f"  prosjek trave po pokretanju : {f(g_m)}")
    print(f"  najviše ovaca               : {f(s_mx)}")
    print(f"  najmanje ovaca              : {f(s_mn)}")
    print(f"  najviše vukova              : {f(w_mx)}")
    print(f"  najmanje vukova             : {f(w_mn)}")
    print(f"  vukovi izumrli do kraja     : {izumrli} od {n}")


for put in sys.argv[1:]:
    sazetak(put, ucitaj(put))
