// Provjera: daje li simulacija u web pregledniku isti obrazac kao NetLogo (mjerenja/rezultati.json).
// Pokretanje:  node test-sim.js
const Sim = require("./sim.js");
const rez = require("../../mjerenja/rezultati.json");

const med = v => { const a = [...v].sort((x, y) => x - y); const m = a.length >> 1; return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2; };
const opis = v => `med ${med(v).toFixed(3)}  min ${Math.min(...v).toFixed(3)}  max ${Math.max(...v).toFixed(3)}`;
const nl = (tab, k) => { const x = rez[tab][k]; return `NetLogo: med ${x.med}  min ${x.min}  max ${x.max}  (>0,9: ${x.iznad_0_9}/${x.n})`; };
let seed = 1;

console.log("BLOK 1 — broj grupa na ticku 500, bez medija (10 pokretanja)");
for (const prag of [0.1, 0.2, 0.3, 0.5, 1, 2]) {
  const v = [];
  for (let i = 0; i < 10; i++) {
    const s = Sim.b1Setup({ ...Sim.B1_ZADANO, prag }, Sim.rng(seed++));
    for (let t = 0; t < 500; t++) Sim.b1Go(s);
    v.push(s.brojGrupa);
  }
  console.log(`  prag ${prag}: ${opis(v)}   | ${nl("b1_grupe_500", `prag=${prag}`)}`);
}
console.log("BLOK 1 — udio za na ticku 150, s medijima (10 pokretanja)");
for (const prag of [0.2, 0.5, 1, 2]) {
  const v = [];
  for (let i = 0; i < 10; i++) {
    const s = Sim.b1Setup({ ...Sim.B1_ZADANO, prag, medijiRade: true }, Sim.rng(seed++));
    for (let t = 0; t < 150; t++) Sim.b1Go(s);
    v.push(s.udioZa);
  }
  console.log(`  prag ${prag}: ${opis(v)}   | ${nl("b1_udio_za_mediji_150", `prag=${prag}`)}`);
}

console.log("BLOK 2 — talas (udio > 0,9) od 50 pokretanja");
for (const ras of [0, 0.05, 0.1, 0.15, 0.3]) {
  let talas = 0;
  for (let i = 0; i < 50; i++) if (Sim.b2DoKraja({ ...Sim.B2_ZADANO, rasipanjePraga: ras }, Sim.rng(seed++)).udioAktivnih > 0.9) talas++;
  const x = rez.b2_rasipanje[`rasipanje-praga=${ras}`];
  console.log(`  rasipanje ${ras}: ${talas}/50   | NetLogo ${x.iznad_0_9}/${x.n}`);
}
for (const pok of [5, 10, 20, 40]) {
  let talas = 0;
  for (let i = 0; i < 50; i++) if (Sim.b2DoKraja({ ...Sim.B2_ZADANO, rasipanjePraga: 0.05, pokretaci: pok }, Sim.rng(seed++)).udioAktivnih > 0.9) talas++;
  const x = rez.b2_pokretaci[`pokretaci=${pok}`];
  console.log(`  pokretaci ${pok} (ras 0,05): ${talas}/50   | NetLogo ${x.iznad_0_9}/${x.n}`);
}

console.log("BLOK 3 — udio za na ticku 500 (20 pokretanja)");
for (const p of [0, 0.05, 0.2, 1]) {
  const v = [], poz = [];
  for (let i = 0; i < 20; i++) {
    const s = Sim.b3Setup({ ...Sim.B3_ZADANO, udioDalekihVeza: p }, Sim.rng(seed++));
    poz.push(s.ljudi.reduce((a, t) => a + t.veze.size, 0) / s.ljudi.length);
    for (let t = 0; t < 500; t++) Sim.b3Go(s);
    v.push(s.udioZa);
  }
  console.log(`  daleke ${p}: ${opis(v)}  poznanika ${(poz.reduce((a, b) => a + b) / poz.length).toFixed(2)}   | ${nl("b3_udio_za_500", `udio-dalekih-veza=${p}`)}`);
}

console.log("BLOK 4 — prosječno sličnih na kraju (10 pokretanja)");
for (const tr of [0.2, 0.3, 0.5, 0.75]) {
  const v = [], tk = [];
  for (let i = 0; i < 10; i++) {
    const s = Sim.b4Setup({ ...Sim.B4_ZADANO, trazeniUdioSlicnih: tr }, Sim.rng(seed++));
    while (s.ticks < 500 && Sim.b4Go(s)) {}
    v.push(s.prosjecnoSlicnih); tk.push(s.ticks);
  }
  console.log(`  traženo ${tr}: ${opis(v)}  ticks med ${med(tk)}   | ${nl("b4_slicnih_kraj", `trazeni-udio-slicnih=${tr}`)}  ticks ${rez.b4_ticks_kraj[`trazeni-udio-slicnih=${tr}`].med}`);
}
