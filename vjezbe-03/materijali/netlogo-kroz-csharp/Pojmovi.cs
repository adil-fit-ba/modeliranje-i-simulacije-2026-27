// Kratki primjeri NetLogo pojmova koji C# programera najčešće iznenade.
// Uz svaki primjer je NetLogo kod i rezultat koji daje NetLogo 7.0.4 (provjereno headless).
// Najkorisnije je pokretati ih u debuggeru: breakpoint unutar lambde u Ask pokazuje ko je this.

using MiniNetLogo;
using static MiniNetLogo.Color;

namespace NetLogoKrozCSharp;

static class Pojmovi
{
    public static void Pokreni()
    {
        AskRedoslijed();
        WithIliIf();
        DieTokomAsk();
        HatchTokomAsk();
        Torus();
        PatchHere();
        Nobody();
    }

    static void Naslov(string naslov, string netlogo)
    {
        Console.WriteLine();
        Console.WriteLine($"== {naslov}");
        foreach (var linija in netlogo.Split('\n')) Console.WriteLine($"   NetLogo: {linija}");
    }

    // 1. ask ide slučajnim redom, i taj red je novi pri svakom pozivu
    static void AskRedoslijed()
    {
        Naslov("ask: slučajan redoslijed, novi pri svakom pozivu",
               "create-turtles 5\nrepeat 3 [ ask turtles [ type who type \" \" ] print \"\" ]");
        World.ClearAll();
        World.CreateTurtles<Turtle>(5);
        for (int i = 0; i < 3; i++)
        {
            var red = new List<int>();
            World.Ask(World.Turtles, t => red.Add(t.Who));
            Console.WriteLine($"   C#:      {string.Join(" ", red)}");
        }
        Console.WriteLine("   (NetLogo je dao npr. 2 3 0 4 1 / 2 1 4 0 3 / 1 0 2 3 4)");
    }

    // 2. with napravi skup prije petlje; if odlučuje u trenutku kada agent dođe na red
    static void WithIliIf()
    {
        Naslov("with ili if: with prvo izabere pa pita, if odlučuje u trenutku",
               "ask turtles [ if color = red [ ask other turtles [ set color blue ] ] ]\n" +
               "ask turtles with [ color = red ] [ ask other turtles [ set color blue ] ]");

        World.ClearAll();
        World.CreateTurtles<Turtle>(3, t => t.Color = Red);
        int izvrsenja = 0;
        World.Ask(World.Turtles, t =>
        {
            if (t.Color == Red)
            {
                izvrsenja++;
                World.Ask(World.Turtles.Other(t), o => o.Color = Blue);
            }
        });
        Console.WriteLine($"   C# if:   naredbe izvršene {izvrsenja} put(a), crvenih ostalo {World.Turtles.Count(t => t.Color == Red)}");

        World.ClearAll();
        World.CreateTurtles<Turtle>(3, t => t.Color = Red);
        izvrsenja = 0;
        World.Ask(World.Turtles.With(t => t.Color == Red), t =>
        {
            izvrsenja++;
            World.Ask(World.Turtles.Other(t), o => o.Color = Blue);
        });
        Console.WriteLine($"   C# with: naredbe izvršene {izvrsenja} put(a), crvenih ostalo {World.Turtles.Count(t => t.Color == Red)}");
        Console.WriteLine("   (NetLogo: if 1 put, ostala 1 crvena; with 3 puta, ostalo 0 crvenih)");
        Console.WriteLine("   Prva turtle oboji ostale u plavo. Kod if one to vide kada dođu na red (asinhrono);");
        Console.WriteLine("   kod with su izabrane prije petlje, pa izvrše naredbe iako više nisu crvene.");
    }

    // 3. agent koji umre prije svog reda se preskače; foreach nad samom listom bi pao
    static void DieTokomAsk()
    {
        Naslov("die tokom ask: mrtav agent se preskače",
               "create-turtles 10\nask turtles [ ask other turtles [ die ] ]");
        World.ClearAll();
        World.CreateTurtles<Turtle>(10);
        World.Ask(World.Turtles, t => World.Ask(World.Turtles.Other(t), o => o.Die()));
        Console.WriteLine($"   C#:      preživjelih {World.Turtles.Count}   (NetLogo: 1)");
        Console.WriteLine("   Prva turtle ubije ostalih devet; one su mrtve prije svog reda i ne izvrše ništa.");

        World.ClearAll();
        World.CreateTurtles<Turtle>(10);
        try
        {
            foreach (var t in World.Turtles) t.Die();   // obični foreach nad listom koja se mijenja
        }
        catch (InvalidOperationException e)
        {
            Console.WriteLine($"   foreach nad World.Turtles uz Die(): {e.GetType().Name}");
            Console.WriteLine("   Zato Ask radi nad kopijom skupa (Shuffle pravi novu listu).");
        }
    }

    // 4. hatch: dijete je kopija roditelja i nije na redu u Ask koji je u toku
    static void HatchTokomAsk()
    {
        Naslov("hatch tokom ask: dijete je kopija i nije na redu",
               "create-turtles 5 [ set color red set size 2 ]\nask turtles [ hatch 1 ]");
        World.ClearAll();
        World.CreateTurtles<Turtle>(5, t => { t.Color = Red; t.Size = 2; });
        int naRedu = 0;
        (Turtle roditelj, Turtle dijete)? par = null;
        World.Ask(World.Turtles, t =>
        {
            naRedu++;
            var d = t.Hatch();
            par ??= (t, d);
        });
        int kopija = World.Turtles.Count(t => t.Color == Red && t.Size == 2);
        Console.WriteLine($"   C#:      na redu {naRedu}, ukupno {World.Turtles.Count}, crvenih veličine 2: {kopija}");
        Console.WriteLine("   (NetLogo: na redu 5, ukupno 10, crvenih veličine 2: 10)");
        var (r, c) = par!.Value;
        Console.WriteLine($"   roditelj {r} i dijete {c}: isti heading ({r.Heading:0} i {c.Heading:0}), nov who");
    }

    // 5. svijet je torus: fd prelazi preko ivice, a distance mjeri najkraći put preko ivice
    static void Torus()
    {
        Naslov("torus: fd i distance preko ivice (svijet -25 .. 25)",
               "create-turtles 1 [ setxy 25.2 0 set heading 90 fd 1 print xcor ]\n" +
               "[ distance turtle 2 ] of turtle 1   ; turtle 1 u (-25, 0), turtle 2 u (25, 0)");
        World.ClearAll(-25, 25, -25, 25);
        var t0 = World.CreateTurtles<Turtle>(1)[0];
        t0.SetXY(25.2, 0);
        t0.Heading = 90;
        t0.Forward(1);
        var t1 = World.CreateTurtles<Turtle>(1)[0];
        t1.SetXY(-25, 0);
        var t2 = World.CreateTurtles<Turtle>(1)[0];
        t2.SetXY(25, 0);
        Console.WriteLine($"   C#:      xcor {t0.X:0.###}, distance {t1.Distance(t2):0.###}   (NetLogo: -24.8 i 1)");
        Console.WriteLine("   Obična formula bez ivica dala bi 26.2 i 50.");
    }

    // 6. patch-here: parcela pxcor pokriva [pxcor - 0.5, pxcor + 0.5)
    static void PatchHere()
    {
        Naslov("patch-here: koja parcela sadrži tačku",
               "[ pxcor ] of patch x 0   za x = 2.4  2.5  2.6  -2.5  -2.6");
        World.ClearAll(-25, 25, -25, 25);
        var xs = new[] { 2.4, 2.5, 2.6, -2.5, -2.6 };
        Console.WriteLine($"   C#:      {string.Join("  ", xs.Select(x => $"{x} -> {World.PatchAt(x, 0).Pxcor}"))}");
        Console.WriteLine("   (NetLogo: 2.4 -> 2  2.5 -> 3  2.6 -> 3  -2.5 -> -2  -2.6 -> -3)");
        Console.WriteLine($"   Zamka: Math.Round(2.5) = {Math.Round(2.5)} i Math.Round(-3.5) = {Math.Round(-3.5)}, a parcele su 3 i -3:");
        Console.WriteLine("   C# polovinu zaokružuje na paran broj. Zato PatchAt koristi Math.Floor(x + 0.5).");
    }

    // 7. nobody je null
    static void Nobody()
    {
        Naslov("nobody = null",
               "create-turtles 10 [ set color one-of [ red blue ] ]\nprint one-of turtles with [ color = green ]");
        World.ClearAll();
        World.CreateTurtles<Turtle>(10, t => t.Color = World.OneOf(Red, Blue));
        var zelena = World.Turtles.With(t => t.Color == Green).OneOf();
        Console.WriteLine($"   C#:      {(zelena == null ? "null" : zelena.ToString())}   (NetLogo: nobody)");
        Console.WriteLine("   Zato iza one-of ide provjera: if prey != nobody [ ... ]  ->  if (prey != null) { ... }");
    }
}
