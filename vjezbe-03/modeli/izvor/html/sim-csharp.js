// Simulacije blokova interakcije, varijanta s C#: računa ih C# kod iz projekta netlogo-kroz-csharp
// (MiniNetLogo + Blokovi), preveden za .NET WebAssembly (projekat netlogo-kroz-csharp-wasm).
// Ovaj fajl daje isti interfejs kao sim.js (window.Sim), pa prikaz (ui.js) ostaje isti.
//
// Sve datoteke .NET-a su ugrađene u stranicu (window.CS_RESURSI: gzip + base64, window.CS_BOOT),
// pa stranica radi i bez interneta i kad se otvori dvoklikom s diska.
(() => {
  const VEL = 41, MIN = -20, SALA = 31;
  const B1_ZADANO = { prag: 0.5, brojLjudi: 200, brojMedija: 4, domet: 3, uticaj: 0.2,
                      porukaMedija: 1, snagaMedija: 0.1, dometMedija: 8, medijiRade: false };
  const B2_ZADANO = { prosjekPraga: 0.3, rasipanjePraga: 0.1, pokretaci: 10 };
  const B3_ZADANO = { udioDalekihVeza: 0, brojVeza: 3, brojLjudi: 200, brojMedija: 2, uticaj: 0.2,
                      porukaMedija: 1, snagaMedija: 0.1, dometMedija: 5, medijiRade: true };
  const B4_ZADANO = { trazeniUdioSlicnih: 0.3, gustina: 0.7 };

  // ---------- stanje pokretanja u svakom panelu ----------
  const poruke = [];
  function poruka(tekst, greska) {
    for (const panel of document.querySelectorAll(".sim[id^=sim]")) {
      let p = panel.querySelector(".cs-stanje");
      if (!p) {
        p = document.createElement("p");
        p.className = "stanje cs-stanje";
        p.setAttribute("aria-live", "polite");
        panel.insertBefore(p, panel.children[1] || null);
        poruke.push(p);
      }
      p.textContent = tekst;
      if (greska) p.style.color = "var(--tinta)";
    }
  }

  // ---------- ugrađene datoteke ----------
  async function bajtovi(ime) {
    const b64 = window.CS_RESURSI[ime];
    if (!b64) throw new Error(`nema ugrađene datoteke ${ime}`);
    const bin = atob(b64), u = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
    const tok = new Blob([u]).stream().pipeThrough(new DecompressionStream("gzip"));
    return new Uint8Array(await new Response(tok).arrayBuffer());
  }
  const jsUrl = async (ime, zamjena) => {
    let kod = new TextDecoder().decode(await bajtovi(ime));
    if (zamjena) kod = zamjena(kod);
    return URL.createObjectURL(new Blob([kod], { type: "text/javascript" }));
  };

  let C = null;   // exports.NetLogoWasm.Blokovi

  async function pokreni() {
    if (typeof DecompressionStream === "undefined") throw new Error("web preglednik je prestar (nema DecompressionStream)");
    poruka("Pokrećem C# (.NET u web pregledniku) …");
    const boot = window.CS_BOOT;
    const res = boot.resources;
    // dotnet.js računa putanje ostalih datoteka iz svoje adrese; blob: adresa ne može biti osnova,
    // pa mu se daje izmišljena osnova. Sve datoteke ionako dolaze iz stranice (withResourceLoader).
    const dotnetUrl = await jsUrl("dotnet.js", k => k.replace("const t=import.meta.url", 'const t="http://localhost/_framework/dotnet.js"'));
    const moduli = {};
    for (const ime of [...Object.keys(res.jsModuleNative), ...Object.keys(res.jsModuleRuntime)])
      moduli[ime] = await jsUrl(ime, k => k.replaceAll("import.meta.url", '"http://localhost/_framework/' + ime + '"'));
    const { dotnet } = await import(dotnetUrl);
    const runtime = await dotnet
      .withConfig(Object.assign({}, boot, { cacheBootResources: false, disableIntegrityCheck: true }))
      .withResourceLoader((tip, ime) => {
        if (tip === "dotnetjs") return moduli[ime];                      // ES modul: adresa (blob:)
        const vrsta = tip === "dotnetwasm" ? "application/wasm" : "application/octet-stream";
        return bajtovi(ime).then(b => new Response(b, { headers: { "content-type": vrsta } }));
      })
      .create();
    const izvoz = await runtime.getAssemblyExports(boot.mainAssemblyName + ".dll");
    C = izvoz.NetLogoWasm.Blokovi;
    for (const p of poruke) p.remove();
  }

  const rng = seed => ({ seed: seed | 0 });   // ui: Sim.rng(sjeme) → setup pozove World.RandomSeed(sjeme)

  // stanje se čita iz C# tek kad ga prikaz zatraži (petlja „do sedmice 500“ ne čita ništa)
  function lijeno(s, citaj, imena) {
    s._staro = true;
    for (const ime of imena)
      Object.defineProperty(s, ime, { get() { if (s._staro) { citaj(s); s._staro = false; } return s["_" + ime]; } });
  }

  // ============================================================ blok 1
  const b1Niz = p => [p.prag, p.brojLjudi, p.brojMedija, p.domet, p.uticaj, p.porukaMedija, p.snagaMedija, p.dometMedija, p.medijiRade ? 1 : 0];
  function b1Citaj(s) {
    const r = C.B1Stanje();
    s.ticks = r[0]; s._udioZa = r[1]; s._brojGrupa = r[2];
    const n = r[3], m = r[4]; let k = 5;
    s._ljudi = new Array(n);
    for (let i = 0; i < n; i++, k += 3) s._ljudi[i] = { x: r[k], y: r[k + 1], stav: r[k + 2] };
    s._mediji = new Array(m);
    for (let i = 0; i < m; i++, k += 2) s._mediji[i] = { x: r[k], y: r[k + 1] };
  }
  function b1Setup(p, r) {
    C.B1Setup(r.seed, b1Niz(p));
    const s = { p, ticks: 0 };
    lijeno(s, b1Citaj, ["ljudi", "mediji", "udioZa", "brojGrupa"]);
    return s;
  }
  function b1Go(s) { C.B1Go(1, b1Niz(s.p)); s.ticks++; s._staro = true; }

  // ============================================================ blok 2
  const b2Niz = p => [p.prosjekPraga, p.rasipanjePraga, p.pokretaci];
  function b2Citaj(s) {
    const r = C.B2Stanje();
    s.ticks = r[0]; s.udioAktivnih = r[1];
    for (let i = 0; i < s.ljudi.length; i++) s.ljudi[i].aktivan = r[2 + i] === 1;
  }
  function b2Setup(p, r) {
    C.B2Setup(r.seed, b2Niz(p));
    const s = { p, ticks: 0, gotovo: false, ljudi: Array.from({ length: SALA * SALA }, () => ({ aktivan: false })) };
    b2Citaj(s);
    return s;
  }
  function b2Go(s) {
    if (s.gotovo) return false;
    if (!C.B2Go()) { s.gotovo = true; return false; }        // if not any? ustaju [ stop ]
    b2Citaj(s);
    return true;
  }
  const b2DoKraja = (p, r) => ({ udioAktivnih: C.B2DoKraja(r.seed, b2Niz(p)) });

  // ============================================================ blok 3
  const b3Niz = p => [p.udioDalekihVeza, p.brojVeza, p.brojLjudi, p.brojMedija, p.uticaj, p.porukaMedija, p.snagaMedija, p.dometMedija, p.medijiRade ? 1 : 0];
  function b3Citaj(s) {
    const r = C.B3Stanje();
    s.ticks = r[0]; s._udioZa = r[1];
    for (let i = 0; i < s._ljudi.length; i++) s._ljudi[i].stav = r[2 + i];
  }
  function b3Setup(p, r) {
    C.B3Setup(r.seed, b3Niz(p));
    const g = C.B3Geometrija();                               // ljudi i veze se poslije setup ne mijenjaju
    const n = g[0], m = g[1], v = g[2]; let k = 3;
    const ljudi = new Array(n), mediji = new Array(m), veze = new Map();
    for (let i = 0; i < n; i++, k += 2) ljudi[i] = { who: i, x: g[k], y: g[k + 1], stav: 0, veze: new Set() };
    for (let i = 0; i < m; i++, k += 2) mediji[i] = { x: g[k], y: g[k + 1] };
    for (let i = 0; i < v; i++, k += 2) {
      const a = ljudi[g[k]], b = ljudi[g[k + 1]];
      veze.set(`${a.who}-${b.who}`, [a, b]); a.veze.add(b); b.veze.add(a);
    }
    const s = { p, ticks: 0, mediji, veze, _ljudi: ljudi };
    lijeno(s, b3Citaj, ["ljudi", "udioZa"]);
    return s;
  }
  function b3Go(s) { C.B3Go(1, b3Niz(s.p)); s.ticks++; s._staro = true; }

  // ============================================================ blok 4
  function b4Citaj(s) {
    const r = C.B4Stanje();
    s.ticks = r[0]; s.prosjecnoSlicnih = r[1]; s.udioNezadovoljnih = r[2];
    for (let i = 0; i < VEL * VEL; i++) { const g = r[3 + i]; s.mjesto[i] = g ? s._grupe[g - 1] : null; }
  }
  function b4Setup(p, r) {
    C.B4Setup(r.seed, [p.trazeniUdioSlicnih, p.gustina]);
    const s = { p, ticks: 0, gotovo: false, mjesto: new Array(VEL * VEL), _grupe: [{ grupa: 0 }, { grupa: 1 }] };
    b4Citaj(s);
    return s;
  }
  function b4Go(s) {
    if (s.gotovo) return false;
    if (!C.B4Go(s.p.trazeniUdioSlicnih)) { s.gotovo = true; return false; }   // svi su zadovoljni: stop
    b4Citaj(s);
    return true;
  }

  window.Sim = { rng, VEL, MIN, SALA,
                 B1_ZADANO, b1Setup, b1Go, B2_ZADANO, b2Setup, b2Go, b2DoKraja,
                 B3_ZADANO, b3Setup, b3Go, B4_ZADANO, b4Setup, b4Go };
  window.SimSpreman = pokreni().catch(e => {
    console.error("C# se nije pokrenuo:", e);
    poruka("C# se nije pokrenuo u ovom web pregledniku: " + (e && e.message ? e.message : e), true);
    throw e;
  });
})();
