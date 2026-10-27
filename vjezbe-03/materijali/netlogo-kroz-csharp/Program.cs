// Ulazna tačka. Pokretanje iz foldera projekta:
//   dotnet run -- pojmovi
//   dotnet run -- model [--seed 1] [--ticks 500] [--mapa 100] [--sinhrono]
//   dotnet run -- eksperiment [--ponavljanja 20] [--ticks 500] [--sinhrono]
//   dotnet run -- blokovi [--blok 1..6] [--ponavljanja n] [--seed 1]

using System.Diagnostics;
using System.Globalization;
using System.Text;
using MiniNetLogo;
using NetLogoKrozCSharp;
using WolfSheep;
using static MiniNetLogo.Color;
using B1 = Blokovi.Povjerenje;
using B2 = Blokovi.Prag;
using B3 = Blokovi.Mreza;
using B4 = Blokovi.Preseljenje;
using B5 = Blokovi.Ustanova;
using B6 = Blokovi.Kazna;

Console.OutputEncoding = Encoding.UTF8;
CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;   // decimalna tačka, kao u NetLogo

var argumenti = args.ToList();
Globals.Sinhrono = argumenti.Contains("--sinhrono");

switch (argumenti.FirstOrDefault())
{
    case "pojmovi":
        Pojmovi.Pokreni();
        break;
    case "model":
        JednoPokretanje(Opcija("--seed", 1), Opcija("--ticks", 500), Opcija("--mapa", 0));
        break;
    case "eksperiment":
        Eksperiment(Opcija("--ponavljanja", 20), Opcija("--ticks", 500));
        break;
    case "blokovi":
        MjerenjaBlokova(Opcija("--blok", 0), Opcija("--ponavljanja", 0), Opcija("--seed", 1));
        break;
    default:
        Console.WriteLine("Upotreba:");
        Console.WriteLine("  dotnet run -- pojmovi         kratki primjeri: ask, with/if, die, hatch, torus, patch-here, nobody");
        Console.WriteLine("  dotnet run -- model           jedno pokretanje Wolf Sheep Predation (s travom)");
        Console.WriteLine("        --seed 1 --ticks 500 --mapa 100 --sinhrono");
        Console.WriteLine("  dotnet run -- eksperiment     više pokretanja u CSV, kao BehaviorSpace");
        Console.WriteLine("        --ponavljanja 20 --ticks 500 --sinhrono");
        Console.WriteLine("  dotnet run -- blokovi         blokovi interakcije s vježbi 3: mala mjerenja za svaki blok");
        Console.WriteLine("        --blok 1..6 (zadano svi) --ponavljanja n --seed 1");
        break;
}

int Opcija(string ime, int zadano)
{
    int i = argumenti.IndexOf(ime);
    return i >= 0 && i + 1 < argumenti.Count ? int.Parse(argumenti[i + 1]) : zadano;
}

// Jedno pokretanje: setup, pa go dok model ne kaže stop ili dok ne prođe zadani broj tickova.
// To je isto što i dugmad setup i go (forever) u NetLogo.
void JednoPokretanje(int seed, int ticks, int mapa)
{
    World.RandomSeed(seed);
    WolfSheepPredation.Setup();
    Console.WriteLine($"Wolf Sheep Predation (s travom), seed {seed}{(Globals.Sinhrono ? ", sinhrono" : "")}");
    Mapa();
    Console.WriteLine(" tick   ovce  vukovi  trava   o = 10 ovaca, W = 10 vukova");
    IspisiRed();
    while (World.Ticks < ticks && WolfSheepPredation.Go())
    {
        if (World.Ticks % 10 == 0) IspisiRed();
        if (mapa > 0 && World.Ticks % mapa == 0) Mapa();
    }
    if (World.Ticks % 10 != 0) IspisiRed();
    if (mapa == 0 || World.Ticks % mapa != 0) Mapa();
}

void IspisiRed()
{
    int s = WolfSheepPredation.CountSheep, w = WolfSheepPredation.CountWolves;
    Console.WriteLine($"{World.Ticks,5} {s,6} {w,7} {WolfSheepPredation.CountGrass,6}   " +
                      $"{new string('o', s / 10),-32}{new string('W', w / 10)}");
}

// Mapa svijeta: W vuk, o ovca, . trava, razmak smeđa parcela. Gornji red je max-pycor.
void Mapa()
{
    var znak = new Dictionary<Patch, char>();
    foreach (var t in World.Turtles)
        if (t is Wolf || !znak.ContainsKey(t.PatchHere)) znak[t.PatchHere] = t is Wolf ? 'W' : 'o';
    Console.WriteLine($"-- tick {World.Ticks}: W vuk, o ovca, . trava");
    for (int py = World.MaxPycor; py >= World.MinPycor; py--)
    {
        var red = new StringBuilder();
        for (int px = World.MinPxcor; px <= World.MaxPxcor; px++)
        {
            var p = World.PatchAt(px, py);
            red.Append(znak.TryGetValue(p, out var z) ? z : p.Pcolor == Green ? '.' : ' ');
        }
        Console.WriteLine("   |" + red + "|");
    }
}

// Više pokretanja s različitim seed (1, 2, ...), svaki tick jedan red u CSV. Kao BehaviorSpace sa
// "Measure runs at every step" i metrikama count sheep, count wolves, count grass.
void Eksperiment(int ponavljanja, int ticks)
{
    Directory.CreateDirectory("rezultati");
    string put = Path.Combine("rezultati", Globals.Sinhrono ? "eksperiment-csharp-sinhrono.csv" : "eksperiment-csharp.csv");
    var sat = Stopwatch.StartNew();
    using (var csv = new StreamWriter(put))
    {
        csv.WriteLine("run,tick,sheep,wolves,grass");
        void Upisi(int run) => csv.WriteLine($"{run},{World.Ticks},{WolfSheepPredation.CountSheep}," +
                                             $"{WolfSheepPredation.CountWolves},{WolfSheepPredation.CountGrass}");
        for (int run = 1; run <= ponavljanja; run++)
        {
            World.RandomSeed(run);
            WolfSheepPredation.Setup();
            Upisi(run);
            while (World.Ticks < ticks && WolfSheepPredation.Go()) Upisi(run);
            Console.WriteLine($"pokretanje {run,2}: tick {World.Ticks}, ovce {WolfSheepPredation.CountSheep}, " +
                              $"vukovi {WolfSheepPredation.CountWolves}, trava {WolfSheepPredation.CountGrass}");
        }
    }
    Console.WriteLine($"Zapisano u {put} ({sat.Elapsed.TotalSeconds:0.0} s)");
}

// ---------- Blokovi interakcije (vježbe 3) ----------
// Za svaki blok mali eksperiment, kao BehaviorSpace: nekoliko vrijednosti jednog parametra, svaka s
// više pokretanja. Pokretanje r ima seed (seed + r - 1), pa svaka vrijednost parametra dobije iste
// seedove. Zadana ponavljanja: blok 1 i 4 po 10, blok 2 i 3 po 20. Rezultati idu u rezultati/blokN-csharp.csv.
void MjerenjaBlokova(int blok, int ponavljanja, int seed)
{
    Directory.CreateDirectory("rezultati");
    var sat = Stopwatch.StartNew();
    if (blok is 0 or 1) Blok1(ponavljanja > 0 ? ponavljanja : 10, seed);
    if (blok is 0 or 2) Blok2(ponavljanja > 0 ? ponavljanja : 20, seed);
    if (blok is 0 or 3) Blok3(ponavljanja > 0 ? ponavljanja : 20, seed);
    if (blok is 0 or 4) Blok4(ponavljanja > 0 ? ponavljanja : 10, seed);
    if (blok is 0 or 5) Blok5(ponavljanja > 0 ? ponavljanja : 20, seed);
    if (blok is 0 or 6) Blok6(ponavljanja > 0 ? ponavljanja : 20, seed);
    Console.WriteLine($"\nUkupno {sat.Elapsed.TotalSeconds:0.0} s; CSV u rezultati/blok1-csharp.csv … blok6-csharp.csv");
}

// sredina, medijan i raspon
string Opis(List<double> v, string f = "0.000")
{
    var s = v.OrderBy(x => x).ToList();
    double med = s.Count % 2 == 1 ? s[s.Count / 2] : (s[s.Count / 2 - 1] + s[s.Count / 2]) / 2;
    return $"sred {s.Average().ToString(f)}, med {med.ToString(f)} ({s[0].ToString(f)}–{s[^1].ToString(f)})";
}

// Blok 1: broj grupa nakon 500 tickova bez medija i udio „za“ nakon 150 tickova s medijima
void Blok1(int n, int seed)
{
    Console.WriteLine($"\nBlok 1, ograničeno povjerenje ({n} pokretanja po vrijednosti)");
    Console.WriteLine($"  {"prag",4}   {"broj grupa, tick 500, bez medija",-38} udio za, tick 150, s medijima");
    using var csv = new StreamWriter(Path.Combine("rezultati", "blok1-csharp.csv"));
    csv.WriteLine("prag,mediji,run,seed,tick,broj_grupa,udio_za,prosjecan_stav");
    foreach (double prag in new[] { 0.1, 0.2, 0.3, 0.5, 1, 2 })
    {
        var grupe = new List<double>();
        var udio = new List<double>();
        foreach (bool mediji in new[] { false, true })
            for (int r = 1; r <= n; r++)
            {
                World.RandomSeed(seed + r - 1);
                B1.Globals.Prag = prag;
                B1.Globals.MedijiRade = mediji;
                B1.Blok1Povjerenje.Setup();
                int ticks = mediji ? 150 : 500;
                while (World.Ticks < ticks) B1.Blok1Povjerenje.Go();
                if (mediji) udio.Add(B1.Globals.UdioZa); else grupe.Add(B1.Globals.BrojGrupa);
                csv.WriteLine($"{prag},{mediji.ToString().ToLower()},{r},{seed + r - 1},{World.Ticks}," +
                              $"{B1.Globals.BrojGrupa},{B1.Globals.UdioZa},{B1.Globals.ProsjecanStav}");
            }
        Console.WriteLine($"  {prag,4}   {Opis(grupe, "0.0"),-38} {Opis(udio)}");
    }
    B1.Globals.Prag = 0.5;
    B1.Globals.MedijiRade = false;
}

// Blok 2: udio onih koji stoje kad više niko ne ustaje (najviše 200 krugova), prosjek praga 0,3
void Blok2(int n, int seed)
{
    Console.WriteLine($"\nBlok 2, prag i kaskada: prosjek praga 0.3, 10 pokretača ({n} pokretanja po vrijednosti)");
    Console.WriteLine($"  {"rasipanje",9}   {"udio aktivnih na kraju",-38} {"> 0.9",5} {"< 0.1",5}   krugova (medijan)");
    using var csv = new StreamWriter(Path.Combine("rezultati", "blok2-csharp.csv"));
    csv.WriteLine("prosjek_praga,rasipanje_praga,pokretaci,run,seed,tick,udio_aktivnih");
    foreach (double rasipanje in new[] { 0, 0.05, 0.1, 0.2 })
    {
        var udio = new List<double>();
        var krugova = new List<double>();
        for (int r = 1; r <= n; r++)
        {
            World.RandomSeed(seed + r - 1);
            B2.Globals.ProsjekPraga = 0.3;
            B2.Globals.RasipanjePraga = rasipanje;
            B2.Globals.Pokretaci = 10;
            B2.Blok2Prag.Setup();
            while (World.Ticks < 200 && B2.Blok2Prag.Go()) { }
            udio.Add(B2.Globals.UdioAktivnih);
            krugova.Add(World.Ticks);
            csv.WriteLine($"0.3,{rasipanje},10,{r},{seed + r - 1},{World.Ticks},{B2.Globals.UdioAktivnih}");
        }
        var k = krugova.OrderBy(x => x).ToList();
        Console.WriteLine($"  {rasipanje,9}   {Opis(udio),-38} {udio.Count(u => u > 0.9),5} {udio.Count(u => u < 0.1),5}   {k[k.Count / 2]}");
    }
    B2.Globals.RasipanjePraga = 0.1;
}

// Blok 3: udio „za“ nakon 150 i 500 tickova, 2 kuće medija
void Blok3(int n, int seed)
{
    Console.WriteLine($"\nBlok 3, mreža poznanstava: 2 kuće medija ({n} pokretanja po vrijednosti)");
    Console.WriteLine($"  {"daleke veze",11}   {"udio za, tick 150",-38} udio za, tick 500");
    using var csv = new StreamWriter(Path.Combine("rezultati", "blok3-csharp.csv"));
    csv.WriteLine("udio_dalekih_veza,run,seed,tick,udio_za,prosjecan_stav,poznanika_po_osobi");
    foreach (double daleke in new[] { 0, 0.05, 0.2, 1 })
    {
        var u150 = new List<double>();
        var u500 = new List<double>();
        for (int r = 1; r <= n; r++)
        {
            World.RandomSeed(seed + r - 1);
            B3.Globals.UdioDalekihVeza = daleke;
            B3.Globals.BrojMedija = 2;
            B3.Blok3Mreza.Setup();
            double poznanika = B3.Blok3Mreza.PoznanikaPoOsobi;
            while (World.Ticks < 500)
            {
                B3.Blok3Mreza.Go();
                if (World.Ticks is 150 or 300 or 500)
                    csv.WriteLine($"{daleke},{r},{seed + r - 1},{World.Ticks},{B3.Globals.UdioZa},{B3.Globals.ProsjecanStav},{poznanika}");
                if (World.Ticks == 150) u150.Add(B3.Globals.UdioZa);
            }
            u500.Add(B3.Globals.UdioZa);
        }
        Console.WriteLine($"  {daleke,11}   {Opis(u150),-38} {Opis(u500)}");
    }
    B3.Globals.UdioDalekihVeza = 0;
}

// Blok 4: prosječan udio sličnih susjeda kad su svi zadovoljni (najviše 300 mjeseci)
void Blok4(int n, int seed)
{
    Console.WriteLine($"\nBlok 4, preseljenje: gustina 0.7 ({n} pokretanja po vrijednosti)");
    Console.WriteLine($"  {"traženi udio",12}   {"prosječno sličnih na početku",-38} {"na kraju",-38} mjeseci (medijan)");
    using var csv = new StreamWriter(Path.Combine("rezultati", "blok4-csharp.csv"));
    csv.WriteLine("trazeni_udio_slicnih,run,seed,tick,prosjecno_slicnih_pocetak,prosjecno_slicnih,udio_nezadovoljnih");
    foreach (double trazeni in new[] { 0.3, 0.5, 0.75 })
    {
        var pocetak = new List<double>();
        var kraj = new List<double>();
        var mjeseci = new List<double>();
        for (int r = 1; r <= n; r++)
        {
            World.RandomSeed(seed + r - 1);
            B4.Globals.TrazeniUdioSlicnih = trazeni;
            B4.Blok4Preseljenje.Setup();
            double p0 = B4.Globals.ProsjecnoSlicnih;
            while (World.Ticks < 300 && B4.Blok4Preseljenje.Go()) { }
            pocetak.Add(p0);
            kraj.Add(B4.Globals.ProsjecnoSlicnih);
            mjeseci.Add(World.Ticks);
            csv.WriteLine($"{trazeni},{r},{seed + r - 1},{World.Ticks},{p0},{B4.Globals.ProsjecnoSlicnih},{B4.Globals.UdioNezadovoljnih}");
        }
        var m = mjeseci.OrderBy(x => x).ToList();
        Console.WriteLine($"  {trazeni,12}   {Opis(pocetak),-38} {Opis(kraj),-38} {m[m.Count / 2]}");
    }
    B4.Globals.TrazeniUdioSlicnih = 0.3;
}

// Blok 5: povjerenje nakon 150 sedmica, bez razgovora i s razgovorom (20 ustanova)
void Blok5(int n, int seed)
{
    Console.WriteLine($"\nBlok 5, mjesto s iskustvom: 20 ustanova, tick 150 ({n} pokretanja po vrijednosti)");
    Console.WriteLine($"  {"loših",6} {"razgovor",8}   {"prosječno povjerenje",-38} {"bili u ustanovi",-38} nisu bili");
    using var csv = new StreamWriter(Path.Combine("rezultati", "blok5-csharp.csv"));
    csv.WriteLine("udio_losih_iskustava,razgovor,run,seed,prosjecno_povjerenje,povjerenje_posjetilaca,povjerenje_ostalih,udio_posjetilaca");
    foreach (double p in new[] { 0.0, 0.3, 0.7, 1.0 })
    foreach (bool razgovor in new[] { false, true })
    {
        var prosjek = new List<double>();
        var bili = new List<double>();
        var nisu = new List<double>();
        for (int r = 1; r <= n; r++)
        {
            World.RandomSeed(seed + r - 1);
            B5.Globals.UdioLosihIskustava = p;
            B5.Globals.Razgovor = razgovor;
            B5.Blok5Ustanova.Setup();
            while (World.Ticks < 150) B5.Blok5Ustanova.Go();
            prosjek.Add(B5.Globals.ProsjecnoPovjerenje);
            bili.Add(B5.Blok5Ustanova.PovjerenjePosjetilaca());
            nisu.Add(B5.Blok5Ustanova.PovjerenjeOstalih());
            csv.WriteLine($"{p},{razgovor},{r},{seed + r - 1},{prosjek[^1]},{bili[^1]},{nisu[^1]},{B5.Globals.UdioPosjetilaca}");
        }
        Console.WriteLine($"  {p,6} {razgovor,8}   {Opis(prosjek),-38} {Opis(bili),-38} {Opis(nisu)}");
    }
    B5.Globals.UdioLosihIskustava = 0.7;
    B5.Globals.Razgovor = true;
}

// Blok 6: prosječna sklonost nakon 150 sedmica prema vjerovatnoći kontrole (jačina kazne 0,1)
void Blok6(int n, int seed)
{
    Console.WriteLine($"\nBlok 6, kontrola i kazna: jačina kazne 0,1, tick 150 ({n} pokretanja po vrijednosti)");
    Console.WriteLine($"  {"kontrola",8}   prosječna sklonost");
    using var csv = new StreamWriter(Path.Combine("rezultati", "blok6-csharp.csv"));
    csv.WriteLine("vjerovatnoca_kontrole,run,seed,prosjecna_sklonost");
    B6.Globals.JacinaKazne = 0.1;
    B6.Globals.Razgovor = false;
    foreach (double q in new[] { 0.05, 0.1, 0.15, 0.17, 0.2, 0.3 })
    {
        var sklonost = new List<double>();
        for (int r = 1; r <= n; r++)
        {
            World.RandomSeed(seed + r - 1);
            B6.Globals.VjerovatnocaKontrole = q;
            B6.Blok6Kazna.Setup();
            while (World.Ticks < 150) B6.Blok6Kazna.Go();
            sklonost.Add(B6.Globals.ProsjecnaSklonost);
            csv.WriteLine($"{q},{r},{seed + r - 1},{sklonost[^1]}");
        }
        Console.WriteLine($"  {q,8}   {Opis(sklonost)}");
    }
    B6.Globals.VjerovatnocaKontrole = 0.1;
}
