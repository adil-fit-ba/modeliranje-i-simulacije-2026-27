// Prikaz: svijet na canvasu, klizači, monitori, grafikoni iz NetLogo mjerenja, kartice s kodom.
(() => {
  const $ = (sel, el = document) => el.querySelector(sel);
  const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];
  const css = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const fmt = (x, d = 2) => x.toFixed(d).replace(".", ",");
  const pct = x => `${Math.round(x * 100)}%`;

  // NetLogo boje (blue 105, red 15, gray 5, orange 25, sky 95, yellow 45)
  const NL = { blue: "#345da9", red: "#d73229", gray: "#8d8d8d", orange: "#f16a15",
               sky: "#2b8ccb", yellow: "#eded2f", sjediGray: "#3a3a3a" };
  const bojaStava = s => s > 0.2 ? NL.blue : s < -0.2 ? NL.red : NL.gray;

  // ---------- canvas ----------
  function pripremi(canvas) {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = canvas.clientWidth || 400;
    canvas.width = Math.round(w * dpr); canvas.height = Math.round(w * dpr);
    const g = canvas.getContext("2d");
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { g, w };
  }
  const tackaSvijeta = (x, y, w) => {               // NetLogo koordinate -> piksel (y raste prema gore)
    const k = w / Sim.VEL;
    return [(x - (Sim.MIN - 0.5)) * k, (Sim.MIN - 0.5 + Sim.VEL - y) * k, k];
  };

  function crtajLjude(canvas, s, veze) {
    const { g, w } = pripremi(canvas);
    g.fillStyle = "#000"; g.fillRect(0, 0, w, w);
    const k = w / Sim.VEL;
    if (veze) {
      g.strokeStyle = "rgba(150,150,150,0.35)"; g.lineWidth = 1;
      g.beginPath();
      for (const [a, b] of s.veze.values()) {
        let dx = b.x - a.x, dy = b.y - a.y;
        if (dx > Sim.VEL / 2) dx -= Sim.VEL; if (dx < -Sim.VEL / 2) dx += Sim.VEL;
        if (dy > Sim.VEL / 2) dy -= Sim.VEL; if (dy < -Sim.VEL / 2) dy += Sim.VEL;
        for (const [p, sgn] of [[a, 1], [b, -1]]) {   // preko ruba: crta se s obje strane
          const [x0, y0] = tackaSvijeta(p.x, p.y, w);
          g.moveTo(x0, y0); g.lineTo(x0 + sgn * dx * k, y0 - sgn * dy * k);
        }
      }
      g.stroke();
    }
    for (const m of s.mediji) {
      const [x, y] = tackaSvijeta(m.x, m.y, w);
      g.fillStyle = NL.yellow;
      g.beginPath(); g.moveTo(x, y - k * 1.3); g.lineTo(x + k * 1.2, y - k * 0.2); g.lineTo(x - k * 1.2, y - k * 0.2); g.fill();
      g.fillRect(x - k * 0.9, y - k * 0.2, k * 1.8, k * 1.2);
    }
    for (const t of s.ljudi) {
      const [x, y] = tackaSvijeta(t.x, t.y, w);
      g.fillStyle = bojaStava(t.stav);
      g.beginPath(); g.arc(x, y, Math.max(2, k * 0.42), 0, 2 * Math.PI); g.fill();
    }
  }

  function crtajMrezu(canvas, n, boja) {           // n × n mjesta, boja(i) -> string ili null
    const { g, w } = pripremi(canvas);
    g.fillStyle = "#000"; g.fillRect(0, 0, w, w);
    const k = w / n;
    for (let i = 0; i < n * n; i++) {
      const c = boja(i); if (!c) continue;
      const x = i % n, y = (i / n) | 0;
      g.fillStyle = c;
      g.fillRect(x * k + 0.5, (n - 1 - y) * k + 0.5, k - 1, k - 1);
    }
  }

  function crtajHistogram(canvas, vrijednosti) {    // histogram [ stav ] of ljudi, interval 0,05
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = canvas.clientWidth || 400, h = canvas.clientHeight || 90;
    canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
    const g = canvas.getContext("2d"); g.setTransform(dpr, 0, 0, dpr, 0, 0);
    g.clearRect(0, 0, w, h);
    const B = 40, kos = new Array(B).fill(0);
    for (const v of vrijednosti) kos[Math.min(B - 1, Math.max(0, Math.floor((v + 1) / 0.05)))]++;
    const max = Math.max(20, ...kos);
    const sw = w / B, dno = h - 14;
    for (let i = 0; i < B; i++) {
      const c = -1 + (i + 0.5) * 0.05;
      g.fillStyle = bojaStava(c);
      const bh = (kos[i] / max) * (dno - 4);
      g.fillRect(i * sw + 1, dno - bh, sw - 2, bh);
    }
    g.fillStyle = css("--siva"); g.font = `11px ${css("--f-mono")}`;
    g.textAlign = "left"; g.fillText("−1", 0, h - 2);
    g.textAlign = "center"; g.fillText("0", w / 2, h - 2);
    g.textAlign = "right"; g.fillText("+1", w, h - 2);
    g.strokeStyle = css("--linija"); g.beginPath(); g.moveTo(0, dno + 0.5); g.lineTo(w, dno + 0.5); g.stroke();
  }

  // ---------- zajednički dijelovi panela ----------
  function klizaci(panel, p, mapa, naPromjenu) {
    for (const inp of $$("input[type=range]", panel)) {
      const kljuc = mapa[inp.id];
      const out = $(`output[for="${inp.id}"]`, panel);
      const prikazi = () => { out.textContent = fmt(+inp.value, +inp.dataset.dec || 2); };
      inp.value = p[kljuc]; prikazi();
      inp.addEventListener("input", () => { p[kljuc] = +inp.value; prikazi(); naPromjenu && naPromjenu(kljuc); });
    }
    for (const inp of $$("input[type=checkbox]", panel)) {
      const kljuc = mapa[inp.id];
      inp.checked = !!p[kljuc];
      inp.addEventListener("change", () => { p[kljuc] = inp.checked; naPromjenu && naPromjenu(kljuc); });
    }
  }

  function petlja(korak, pauzaMs, dugmeGo, nakonZaustavljanja) {
    let radi = false, zadnje = 0;
    const okvir = vrijeme => {
      if (!radi) return;
      if (vrijeme - zadnje >= pauzaMs) {
        zadnje = vrijeme;
        if (korak() === false) { stani(); nakonZaustavljanja && nakonZaustavljanja(); return; }
      }
      requestAnimationFrame(okvir);
    };
    const stani = () => { radi = false; dugmeGo.textContent = "go"; dugmeGo.setAttribute("aria-pressed", "false"); };
    const kreni = () => { radi = true; dugmeGo.textContent = "pauza"; dugmeGo.setAttribute("aria-pressed", "true"); requestAnimationFrame(okvir); };
    dugmeGo.addEventListener("click", () => radi ? stani() : kreni());
    return { stani, get radi() { return radi; } };
  }

  let sjeme = 20261024;
  const noviRng = () => Sim.rng(sjeme++);

  const blokovi = [];   // četiri simulacije; pokreću se na kraju (vidi pokreniBlokove)

  // dug posao (500 tickova, 100 pokretanja) u dijelovima od ~40 ms, da stranica ostane živa
  // i da se vidi napredak; C# u web pregledniku je sporiji od JavaScripta
  function uDijelovima(korak, gotovo, poslije) {
    const dio = () => {
      const kraj = performance.now() + 40;
      while (!gotovo() && performance.now() < kraj) korak();
      poslije();
      if (!gotovo()) setTimeout(dio, 0);
    };
    dio();
  }
  function doSedmice500(dugme, stanje, korak, crtaj) {   // stanje() = trenutni s (setup ga zamijeni)
    const mojS = stanje();
    const gotovo = () => mojS !== stanje() || mojS.ticks >= 500;
    dugme.disabled = true;
    uDijelovima(() => korak(mojS), gotovo, () => { if (mojS === stanje()) crtaj(); if (gotovo()) dugme.disabled = false; });
  }

  // ============================================================
  // Blok 1
  // ============================================================
  blokovi.push(function blok1() {
    const panel = $("#sim1"); if (!panel) return;
    const p = { ...Sim.B1_ZADANO };
    let s;
    const svijet = $("canvas.svijet", panel), hist = $("canvas.hist", panel);
    const crtaj = () => {
      crtajLjude(svijet, s, false);
      crtajHistogram(hist, s.ljudi.map(t => t.stav));
      $("[data-m=ticks]", panel).textContent = s.ticks;
      $("[data-m=grupe]", panel).textContent = s.brojGrupa;
      $("[data-m=za]", panel).textContent = pct(s.udioZa);
    };
    const setup = () => { s = Sim.b1Setup(p, noviRng()); crtaj(); };
    klizaci(panel, p, { "b1-prag": "prag", "b1-mediji": "medijiRade" });
    const lp = petlja(() => { Sim.b1Go(s); Sim.b1Go(s); crtaj(); }, 0, $("[data-a=go]", panel));
    $("[data-a=setup]", panel).addEventListener("click", () => { lp.stani(); setup(); });
    $("[data-a=korak]", panel).addEventListener("click", () => { Sim.b1Go(s); crtaj(); });
    $("[data-a=do500]", panel).addEventListener("click", ev => {
      lp.stani(); doSedmice500(ev.currentTarget, () => s, x => Sim.b1Go(x), crtaj);
    });
    setup();
    window.addEventListener("resize", () => crtaj());
  });

  // ============================================================
  // Blok 2
  // ============================================================
  blokovi.push(function blok2() {
    const panel = $("#sim2"); if (!panel) return;
    const p = { ...Sim.B2_ZADANO };
    let s;
    const svijet = $("canvas.svijet", panel);
    const crtaj = () => {
      crtajMrezu(svijet, Sim.SALA, i => s.ljudi[i].aktivan ? NL.orange : NL.sjediGray);
      $("[data-m=ticks]", panel).textContent = s.ticks;
      $("[data-m=aktivni]", panel).textContent = pct(s.udioAktivnih);
      $("[data-m=stanje]", panel).textContent = s.gotovo ? "niko više ne ustaje" : "";
    };
    const setup = () => { s = Sim.b2Setup(p, noviRng()); crtaj(); };
    klizaci(panel, p, { "b2-prosjek": "prosjekPraga", "b2-rasipanje": "rasipanjePraga", "b2-pokretaci": "pokretaci" },
            () => { lp.stani(); setup(); $("[data-m=serija]", panel).textContent = ""; });
    const lp = petlja(() => { const dalje = Sim.b2Go(s); crtaj(); return dalje; }, 110, $("[data-a=go]", panel), crtaj);
    $("[data-a=setup]", panel).addEventListener("click", () => { lp.stani(); setup(); });
    $("[data-a=korak]", panel).addEventListener("click", () => { Sim.b2Go(s); crtaj(); });
    $("[data-a=serija]", panel).addEventListener("click", ev => {
      const dugme = ev.currentTarget, izlaz = $("[data-m=serija]", panel);
      const N = 100; let n = 0, talas = 0;
      dugme.disabled = true;
      uDijelovima(() => { if (Sim.b2DoKraja(p, noviRng()).udioAktivnih > 0.9) talas++; n++; }, () => n >= N,
                  () => { izlaz.textContent = `talas u ${talas} od ${n} pokretanja`; if (n >= N) dugme.disabled = false; });
    });
    setup();
    window.addEventListener("resize", () => crtaj());
  });

  // ============================================================
  // Blok 3
  // ============================================================
  blokovi.push(function blok3() {
    const panel = $("#sim3"); if (!panel) return;
    const p = { ...Sim.B3_ZADANO };
    let s, prikaziVeze = true;
    const svijet = $("canvas.svijet", panel);
    const crtaj = () => {
      crtajLjude(svijet, s, prikaziVeze);
      $("[data-m=ticks]", panel).textContent = s.ticks;
      $("[data-m=za]", panel).textContent = pct(s.udioZa);
      $("[data-m=poznanika]", panel).textContent = fmt(s.ljudi.reduce((a, t) => a + t.veze.size, 0) / s.ljudi.length, 1);
    };
    const setup = () => { s = Sim.b3Setup(p, noviRng()); crtaj(); };
    klizaci(panel, p, { "b3-daleke": "udioDalekihVeza", "b3-mediji": "medijiRade" },
            k => { if (k === "udioDalekihVeza") { lp.stani(); setup(); } });
    $("#b3-veze").addEventListener("change", e => { prikaziVeze = e.target.checked; crtaj(); });
    const lp = petlja(() => { Sim.b3Go(s); Sim.b3Go(s); crtaj(); }, 0, $("[data-a=go]", panel));
    $("[data-a=setup]", panel).addEventListener("click", () => { lp.stani(); setup(); });
    $("[data-a=korak]", panel).addEventListener("click", () => { Sim.b3Go(s); crtaj(); });
    $("[data-a=do500]", panel).addEventListener("click", ev => { lp.stani(); doSedmice500(ev.currentTarget, () => s, x => Sim.b3Go(x), crtaj); });
    setup();
    window.addEventListener("resize", () => crtaj());
  });

  // ============================================================
  // Blok 4
  // ============================================================
  blokovi.push(function blok4() {
    const panel = $("#sim4"); if (!panel) return;
    const p = { ...Sim.B4_ZADANO };
    let s;
    const svijet = $("canvas.svijet", panel);
    const crtaj = () => {
      crtajMrezu(svijet, Sim.VEL, i => { const t = s.mjesto[i]; return t ? (t.grupa ? NL.orange : NL.sky) : null; });
      $("[data-m=ticks]", panel).textContent = s.ticks;
      $("[data-m=slicnih]", panel).textContent = pct(s.prosjecnoSlicnih);
      $("[data-m=nezadovoljni]", panel).textContent = pct(s.udioNezadovoljnih);
      $("[data-m=stanje]", panel).textContent = s.gotovo ? "svi su zadovoljni" : "";
    };
    const setup = () => { s = Sim.b4Setup(p, noviRng()); crtaj(); };
    klizaci(panel, p, { "b4-trazeni": "trazeniUdioSlicnih", "b4-gustina": "gustina" },
            k => { lp.stani(); if (k === "gustina") setup(); else { s.gotovo = false; s.p = p; } });
    const lp = petlja(() => { const dalje = Sim.b4Go(s); crtaj(); return dalje; }, 160, $("[data-a=go]", panel), crtaj);
    $("[data-a=setup]", panel).addEventListener("click", () => { lp.stani(); setup(); });
    $("[data-a=korak]", panel).addEventListener("click", () => { Sim.b4Go(s); crtaj(); });
    setup();
    window.addEventListener("resize", () => crtaj());
  });

  // simulacije: odmah (JavaScript) ili kad se C# pokrene u web pregledniku (varijanta stranice s C#)
  const pokreniBlokove = () => blokovi.forEach(f => f());
  if (window.SimSpreman) window.SimSpreman.then(pokreniBlokove, () => {});
  else pokreniBlokove();

  // ============================================================
  // Grafikoni iz NetLogo mjerenja (SVG, boje iz tokena)
  // ============================================================
  const SVG = "http://www.w3.org/2000/svg";
  const el = (ime, atr = {}, tekst) => {
    const e = document.createElementNS(SVG, ime);
    for (const [k, v] of Object.entries(atr)) e.setAttribute(k, v);
    if (tekst !== undefined) e.textContent = tekst;
    return e;
  };

  // spec: { naslov, kategorije[], podaci[] ({med,min,max} ili {vrijednost}), yMin, yMax, yKoraci[], yFormat, xNaslov, tip, ref }
  function grafik(cilj, spec) {
    const W = 460, H = 250, L = 46, R = 12, T = 14, B = 46;
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": spec.naslov, class: "grafik" });
    const n = spec.kategorije.length, sirina = (W - L - R) / n;
    const x = i => L + sirina * (i + 0.5);
    const y = v => T + (H - T - B) * (1 - (v - spec.yMin) / (spec.yMax - spec.yMin));
    for (const v of spec.yKoraci) {
      svg.append(el("line", { x1: L, x2: W - R, y1: y(v), y2: y(v), class: "g-mreza" }));
      svg.append(el("text", { x: L - 6, y: y(v) + 4, "text-anchor": "end", class: "g-oznaka" }, spec.yFormat(v)));
    }
    if (spec.ref) {
      svg.append(el("line", { x1: L, x2: W - R, y1: y(spec.ref.v), y2: y(spec.ref.v), class: "g-ref" }));
      svg.append(el("text", { x: W - R, y: y(spec.ref.v) - 5, "text-anchor": "end", class: "g-ref-tekst" }, spec.ref.tekst));
    }
    if (spec.dijagonala) {                       // „traženo“: y = x za kategorije koje su brojevi
      const pts = spec.kategorije.map((k, i) => `${x(i)},${y(+k)}`).join(" ");
      svg.append(el("polyline", { points: pts, class: "g-ref", fill: "none" }));
      svg.append(el("text", { x: x(n - 1), y: y(+spec.kategorije[n - 1]) + 16, "text-anchor": "end", class: "g-ref-tekst" }, spec.dijagonala));
    }
    spec.podaci.forEach((d, i) => {
      if (spec.tip === "stupci") {
        const h0 = y(spec.yMin), h1 = y(d.vrijednost);
        svg.append(el("rect", { x: x(i) - sirina * 0.32, y: h1, width: sirina * 0.64, height: Math.max(0, h0 - h1), rx: 2, class: "g-stupac" }));
        svg.append(el("text", { x: x(i), y: h1 - 5, "text-anchor": "middle", class: "g-vrijednost" }, d.oznaka));
      } else {
        svg.append(el("line", { x1: x(i), x2: x(i), y1: y(d.min), y2: y(d.max), class: "g-raspon" }));
        svg.append(el("circle", { cx: x(i), cy: y(d.med), r: 5, class: "g-tacka" }));
        svg.append(el("text", { x: x(i) + 8, y: y(d.med) + 4, class: "g-vrijednost" }, spec.yFormat(d.med)));
      }
      svg.append(el("text", { x: x(i), y: H - B + 18, "text-anchor": "middle", class: "g-oznaka" }, spec.kategorije[i].replace(".", ",")));
    });
    svg.append(el("text", { x: L + (W - L - R) / 2, y: H - 6, "text-anchor": "middle", class: "g-naslov-x" }, spec.xNaslov));
    svg.append(el("line", { x1: L, x2: W - R, y1: y(spec.yMin), y2: y(spec.yMin), class: "g-os" }));
    cilj.append(svg);
  }

  const D = window.MJERENJA;
  const red = (tab, pref, kat) => kat.map(k => D[tab][`${pref}=${k}`]);
  const ucrtaj = (id, spec) => { const c = document.getElementById(id); if (c && D) grafik(c, spec); };
  const procenat = v => `${Math.round(v * 100)}%`;

  if (D) {
    const PR = ["0.1", "0.2", "0.3", "0.5", "1", "2"];
    ucrtaj("g1a", { naslov: "Broj grupa stavova na ticku 500, bez medija", kategorije: PR,
      podaci: red("b1_grupe_500", "prag", PR), yMin: 0, yMax: 9, yKoraci: [0, 2, 4, 6, 8], yFormat: v => `${Math.round(v)}`,
      xNaslov: "prag" });
    ucrtaj("g1b", { naslov: "Udio za na ticku 150, s medijima", kategorije: PR,
      podaci: red("b1_udio_za_mediji_150", "prag", PR), yMin: 0, yMax: 1, yKoraci: [0, 0.25, 0.5, 0.75, 1], yFormat: procenat,
      xNaslov: "prag", ref: { v: D.b1_udio_za_mediji_0["prag=0.5"].med, tekst: "na početku" } });

    const RAS = Object.keys(D.b2_rasipanje).map(k => k.split("=")[1]).sort((a, b) => a - b);
    ucrtaj("g2a", { naslov: "Udio pokretanja s talasom prema rasipanju praga", kategorije: RAS, tip: "stupci",
      podaci: RAS.map(k => { const x = D.b2_rasipanje[`rasipanje-praga=${k}`]; return { vrijednost: x.iznad_0_9 / x.n, oznaka: procenat(x.iznad_0_9 / x.n) }; }),
      yMin: 0, yMax: 1.12, yKoraci: [0, 0.5, 1], yFormat: procenat, xNaslov: "rasipanje praga (prosjek 0,3; 10 pokretača)" });
    const POK = Object.keys(D.b2_pokretaci).map(k => k.split("=")[1]).sort((a, b) => a - b);
    ucrtaj("g2b", { naslov: "Udio pokretanja s talasom prema broju pokretača", kategorije: POK, tip: "stupci",
      podaci: POK.map(k => { const x = D.b2_pokretaci[`pokretaci=${k}`]; return { vrijednost: x.iznad_0_9 / x.n, oznaka: procenat(x.iznad_0_9 / x.n) }; }),
      yMin: 0, yMax: 1.12, yKoraci: [0, 0.5, 1], yFormat: procenat, xNaslov: "broj pokretača (rasipanje 0,05)" });

    const DV = ["0", "0.05", "0.2", "1"];
    ucrtaj("g3a", { naslov: "Udio za na ticku 500 prema udjelu dalekih veza", kategorije: DV,
      podaci: red("b3_udio_za_500", "udio-dalekih-veza", DV), yMin: 0, yMax: 1, yKoraci: [0, 0.25, 0.5, 0.75, 1], yFormat: procenat,
      xNaslov: "udio dalekih veza", ref: { v: D.b3_udio_za_0["udio-dalekih-veza=0"].med, tekst: "na početku" } });

    const TR = ["0.2", "0.3", "0.4", "0.5", "0.6", "0.75"];
    ucrtaj("g4a", { naslov: "Prosječan udio sličnih susjeda na kraju", kategorije: TR,
      podaci: red("b4_slicnih_kraj", "trazeni-udio-slicnih", TR), yMin: 0, yMax: 1, yKoraci: [0, 0.25, 0.5, 0.75, 1], yFormat: procenat,
      xNaslov: "traženi udio sličnih", ref: { v: D.b4_slicnih_pocetak["trazeni-udio-slicnih=0.3"].med, tekst: "na početku" },
      dijagonala: "traženo" });
  }

  // ---------- kartice s kodom ----------
  for (const kartice of $$(".kod-kartice")) {
    const dugmad = $$("[role=tab]", kartice);
    dugmad.forEach(d => d.addEventListener("click", () => {
      dugmad.forEach(x => {
        const izabrano = x === d;
        x.setAttribute("aria-selected", izabrano);
        x.tabIndex = izabrano ? 0 : -1;
        document.getElementById(x.getAttribute("aria-controls")).hidden = !izabrano;
      });
    }));
  }
  for (const pre of $$("pre code")) {                // komentari svjetlije: ;; (NetLogo) i // (C#)
    pre.innerHTML = pre.innerHTML.split("\n").map(l => l.replace(/(;;.*|\/\/.*)$/, '<span class="kom">$1</span>')).join("\n");
  }

  // ---------- obrazac „model na papiru“: kopiranje ----------
  const kopiraj = $("#kopiraj-obrazac");
  if (kopiraj) kopiraj.addEventListener("click", async () => {
    const tekst = $("#obrazac-tekst").textContent;
    const poruka = $("#kopiraj-poruka");
    try { await navigator.clipboard.writeText(tekst); poruka.textContent = "Obrazac je kopiran."; }
    catch {
      const r = document.createRange(); r.selectNodeContents($("#obrazac-tekst"));
      const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r);
      poruka.textContent = "Obrazac je označen; kopirajte ga s Ctrl+C.";
    }
  });
})();
