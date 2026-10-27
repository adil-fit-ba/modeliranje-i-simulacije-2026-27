// Simulacije blokova interakcije za web preglednik (ilustracija).
// Svaka funkcija prati NetLogo kod iz ../napravi_modele.py, red po red gdje je moguće.
// Brojke na stranici dolaze iz NetLoga (mjerenja/rezultati.json); ovaj kod služi za prikaz.
// Bez DOM-a, pa se može provjeriti i u Node-u (test-sim.js).

const Sim = (() => {
  // ---------- slučajni brojevi (sjeme radi provjere) ----------
  function rng(seed) {                       // mulberry32
    let a = (seed >>> 0) || 1;
    const f = () => {
      a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
    f.int = n => Math.floor(f() * n);                         // random n
    f.normal = (m, s) => {                                    // random-normal m s
      let u = 0; while (u === 0) u = f();
      return m + s * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * f());
    };
    f.shuffle = arr => {                                      // ask: novi slučajan redoslijed
      const a2 = arr.slice();
      for (let i = a2.length - 1; i > 0; i--) { const j = f.int(i + 1); [a2[i], a2[j]] = [a2[j], a2[i]]; }
      return a2;
    };
    f.oneOf = arr => arr.length ? arr[f.int(arr.length)] : null;  // one-of (null = nobody)
    f.nOf = (n, arr) => f.shuffle(arr).slice(0, n);               // n-of
    return f;
  }

  // ---------- torus -20 .. 20 (41 × 41 patcheva) ----------
  const MIN = -20, VEL = 41;
  const wrap = v => { let x = (v - (MIN - 0.5)) % VEL; if (x < 0) x += VEL; return x + MIN - 0.5; };
  const randomCor = r => MIN - 0.5 + r() * VEL;               // random-xcor
  function dist(a, b) {                                        // distance na torusu
    let dx = Math.abs(a.x - b.x), dy = Math.abs(a.y - b.y);
    if (dx > VEL / 2) dx = VEL - dx;
    if (dy > VEL / 2) dy = VEL - dy;
    return Math.sqrt(dx * dx + dy * dy);
  }
  function kreni(t, r) {                                       // right random 360  forward 1
    t.h = (t.h + r.int(360)) % 360;
    const rad = t.h * Math.PI / 180;
    t.x = wrap(t.x + Math.sin(rad));
    t.y = wrap(t.y + Math.cos(rad));
  }
  const inRadius = (t, skup, d) => skup.filter(o => o !== t && dist(t, o) <= d);  // other ... in-radius

  // ============================================================
  // BLOK 1 — ograničeno povjerenje
  // ============================================================
  const B1_ZADANO = { prag: 0.5, brojLjudi: 200, brojMedija: 4, domet: 3, uticaj: 0.2,
                      porukaMedija: 1, snagaMedija: 0.1, dometMedija: 8, medijiRade: false };

  function b1Setup(p, r) {
    const s = { p, r, ticks: 0 };
    s.ljudi = Array.from({ length: p.brojLjudi }, () => ({
      x: randomCor(r), y: randomCor(r), h: r.int(360),
      stav: r() * 2 - 1, integritet: r() }));
    s.mediji = Array.from({ length: p.brojMedija }, () => ({ x: randomCor(r), y: randomCor(r) }));
    b1Mjere(s);
    return s;
  }
  function b1Go(s) {
    const { p, r } = s;
    for (const t of r.shuffle(s.ljudi)) {                      // ask ljudi [
      kreni(t, r);
      const sag = r.oneOf(inRadius(t, s.ljudi, p.domet));      // let sagovornik one-of other ljudi in-radius domet
      if (sag) {
        const razlika = sag.stav - t.stav;
        if (Math.abs(razlika) < p.prag) {                      // if abs razlika < prag [
          const mojStav = t.stav;
          t.stav += razlika * (1 - t.integritet) * p.uticaj;
          sag.stav += (mojStav - sag.stav) * (1 - sag.integritet) * p.uticaj;
        }
      }
      if (p.medijiRade && s.mediji.some(m => dist(t, m) <= p.dometMedija)
          && Math.abs(p.porukaMedija - t.stav) < p.prag)
        t.stav += (p.porukaMedija - t.stav) * (1 - t.integritet) * p.snagaMedija;
    }
    s.ticks++;
    b1Mjere(s);
  }
  function b1Grupe(ljudi) {                                    // to-report izbroji-grupe
    const st = ljudi.map(t => t.stav).sort((a, b) => a - b);
    const najmanje = 0.05 * st.length;
    let grupe = 0, vel = 1;
    for (let i = 1; i < st.length; i++) {
      if (st[i] - st[i - 1] < 0.1) vel++;
      else { if (vel >= najmanje) grupe++; vel = 1; }
    }
    if (vel >= najmanje) grupe++;
    return grupe;
  }
  function b1Mjere(s) {
    s.udioZa = s.ljudi.filter(t => t.stav > 0.2).length / s.ljudi.length;
    s.brojGrupa = b1Grupe(s.ljudi);
  }

  // ============================================================
  // BLOK 2 — prag i kaskada (sala 31 × 31, bez omotavanja)
  // ============================================================
  const B2_ZADANO = { prosjekPraga: 0.3, rasipanjePraga: 0.1, pokretaci: 10 };
  const SALA = 31, SALA_MIN = -15;

  function b2Setup(p, r) {
    const s = { p, r, ticks: 0, gotovo: false };
    s.ljudi = [];
    for (let y = 0; y < SALA; y++) for (let x = 0; x < SALA; x++)
      s.ljudi.push({ x, y, aktivan: false,
                     prag: Math.max(0, Math.min(1, r.normal(p.prosjekPraga, p.rasipanjePraga))) });
    for (const t of s.ljudi) {                                 // ljudi-on neighbors (do 8, bez omotavanja)
      t.susjedi = [];
      for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
        if (!dx && !dy) continue;
        const nx = t.x + dx, ny = t.y + dy;
        if (nx >= 0 && ny >= 0 && nx < SALA && ny < SALA) t.susjedi.push(s.ljudi[ny * SALA + nx]);
      }
    }
    for (const t of r.nOf(p.pokretaci, s.ljudi)) t.aktivan = true;
    b2Mjere(s);
    return s;
  }
  const udioOkoMene = t => t.susjedi.filter(o => o.aktivan).length / t.susjedi.length;
  function b2Go(s) {
    if (s.gotovo) return false;
    // with prvo izabere sve koji ustaju (prema stanju na početku kruga), pa ih tek onda pita
    const ustaju = s.ljudi.filter(t => !t.aktivan && udioOkoMene(t) >= t.prag);
    if (!ustaju.length) { s.gotovo = true; return false; }     // if not any? ustaju [ stop ]
    for (const t of ustaju) t.aktivan = true;
    s.ticks++;
    b2Mjere(s);
    return true;
  }
  function b2Mjere(s) { s.udioAktivnih = s.ljudi.filter(t => t.aktivan).length / s.ljudi.length; }
  function b2DoKraja(p, r) {                                   // jedno pokretanje do zaustavljanja
    const s = b2Setup(p, r);
    while (s.ticks < 200 && b2Go(s)) {}
    return s;
  }

  // ============================================================
  // BLOK 3 — mreža poznanstava
  // ============================================================
  const B3_ZADANO = { udioDalekihVeza: 0, brojVeza: 3, brojLjudi: 200, brojMedija: 2, uticaj: 0.2,
                      porukaMedija: 1, snagaMedija: 0.1, dometMedija: 5, medijiRade: true };

  function b3Setup(p, r) {
    const s = { p, r, ticks: 0 };
    s.ljudi = Array.from({ length: p.brojLjudi }, (_, who) => ({
      who, x: randomCor(r), y: randomCor(r), stav: r() * 2 - 1, integritet: r(), veze: new Set() }));
    s.veze = new Map();                                        // ključ "a-b" (a < b) -> [a, b]
    const kljuc = (a, b) => a.who < b.who ? `${a.who}-${b.who}` : `${b.who}-${a.who}`;
    const poveži = (a, b) => {                                 // create-link-with (bez duplikata)
      const k = kljuc(a, b);
      if (s.veze.has(k)) return;
      s.veze.set(k, a.who < b.who ? [a, b] : [b, a]);
      a.veze.add(b); b.veze.add(a);
    };
    for (const t of r.shuffle(s.ljudi)) {                      // ask ljudi [ create-links-with min-n-of broj-veza ...
      const ostali = r.shuffle(s.ljudi.filter(o => o !== t))   // izjednačenja se rješavaju slučajno
        .map(o => [dist(t, o), o]).sort((a, b) => a[0] - b[0]);
      for (let i = 0; i < p.brojVeza; i++) poveži(t, ostali[i][1]);
    }
    for (const [k, [a, b]] of r.shuffle([...s.veze.entries()])) {   // ask links [
      if (r() < p.udioDalekihVeza) {
        const novi = r.oneOf(s.ljudi.filter(o => o !== a && !a.veze.has(o)));  // end1 = a
        if (novi) {
          poveži(a, novi);
          s.veze.delete(k); a.veze.delete(b); b.veze.delete(a);  // die
        }
      }
    }
    s.mediji = Array.from({ length: p.brojMedija }, () => ({ x: randomCor(r), y: randomCor(r) }));
    b3Mjere(s);
    return s;
  }
  function b3Go(s) {
    const { p, r } = s;
    for (const t of r.shuffle(s.ljudi)) {
      const sag = r.oneOf([...t.veze]);                        // one-of link-neighbors
      if (sag) t.stav += (sag.stav - t.stav) * (1 - t.integritet) * p.uticaj;
      if (p.medijiRade && s.mediji.some(m => dist(t, m) <= p.dometMedija))
        t.stav += (p.porukaMedija - t.stav) * (1 - t.integritet) * p.snagaMedija;
    }
    s.ticks++;
    b3Mjere(s);
  }
  function b3Mjere(s) { s.udioZa = s.ljudi.filter(t => t.stav > 0.2).length / s.ljudi.length; }

  // ============================================================
  // BLOK 4 — preseljenje (torus 41 × 41)
  // ============================================================
  const B4_ZADANO = { trazeniUdioSlicnih: 0.3, gustina: 0.7 };
  const N4 = VEL * VEL;

  function b4Setup(p, r) {
    const s = { p, r, ticks: 0, gotovo: false };
    s.mjesto = new Array(N4).fill(null);                       // patch -> covjek ili null
    s.ljudi = [];
    const sva = [...Array(N4).keys()];
    for (const i of r.nOf(Math.round(p.gustina * N4), sva)) {  // ask n-of ... patches [ sprout-ljudi 1
      const t = { i, grupa: r.int(2) };
      s.mjesto[i] = t; s.ljudi.push(t);
    }
    s.prazna = sva.filter(i => !s.mjesto[i]);
    b4Procijeni(s); b4Mjere(s);
    return s;
  }
  const susjedi4 = i => {
    const x = i % VEL, y = (i / VEL) | 0, out = [];
    for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++)
      if (dx || dy) out.push(((y + dy + VEL) % VEL) * VEL + ((x + dx + VEL) % VEL));
    return out;
  };
  function b4Procijeni(s) {
    for (const t of s.ljudi) {
      let sus = 0, sli = 0;
      for (const j of susjedi4(t.i)) { const o = s.mjesto[j]; if (o) { sus++; if (o.grupa === t.grupa) sli++; } }
      t.susjeda = sus; t.slicnih = sli;
      t.zadovoljan = sli >= s.p.trazeniUdioSlicnih * sus;
    }
  }
  function b4Go(s) {
    if (s.gotovo) return false;
    const nez = s.ljudi.filter(t => !t.zadovoljan);
    if (!nez.length) { s.gotovo = true; return false; }
    for (const t of s.r.shuffle(nez)) {                        // ask ljudi with [ not zadovoljan? ] [ preseli-se ]
      const k = s.r.int(s.prazna.length);                      // move-to one-of patches with [ not any? ljudi-here ]
      const novo = s.prazna[k];
      s.prazna[k] = t.i;
      s.mjesto[t.i] = null; s.mjesto[novo] = t; t.i = novo;
    }
    b4Procijeni(s);
    s.ticks++;
    b4Mjere(s);
    return true;
  }
  function b4Mjere(s) {
    const sa = s.ljudi.filter(t => t.susjeda > 0);
    s.prosjecnoSlicnih = sa.reduce((a, t) => a + t.slicnih / t.susjeda, 0) / sa.length;
    s.udioNezadovoljnih = s.ljudi.filter(t => !t.zadovoljan).length / s.ljudi.length;
  }

  return { rng, VEL, MIN, SALA, dist,
           B1_ZADANO, b1Setup, b1Go, B2_ZADANO, b2Setup, b2Go, b2DoKraja,
           B3_ZADANO, b3Setup, b3Go, B4_ZADANO, b4Setup, b4Go };
})();

if (typeof module !== "undefined") module.exports = Sim;
