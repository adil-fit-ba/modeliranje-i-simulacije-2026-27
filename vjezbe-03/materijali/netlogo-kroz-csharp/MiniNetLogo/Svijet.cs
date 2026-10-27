namespace MiniNetLogo;

// Svijet: parcele, turtles, veze, brojač tickova i generator slučajnih brojeva.
// NetLogo model ima jedan svijet, pa je ovdje statična klasa.
public static class World
{
    public static int MinPxcor { get; private set; } = -16;
    public static int MaxPxcor { get; private set; } = 16;
    public static int MinPycor { get; private set; } = -16;
    public static int MaxPycor { get; private set; } = 16;
    public static int WorldWidth => MaxPxcor - MinPxcor + 1;     // world-width
    public static int WorldHeight => MaxPycor - MinPycor + 1;    // world-height

    // Model Settings: World wraps horizontally/vertically. false = svijet s ivicama (npr. sala).
    public static bool Wrapping { get; private set; } = true;

    static readonly List<Turtle> turtles = new();
    static readonly List<Link> links = new();
    static Patch[] patches = Array.Empty<Patch>();
    static int nextWho;

    public static IReadOnlyList<Turtle> Turtles => turtles;      // turtles (svi breedovi zajedno)
    public static IReadOnlyList<Patch> Patches => patches;       // patches
    public static IReadOnlyList<Link> Links => links;            // links
    public static int Ticks { get; private set; }                // ticks
    public static Random Rng { get; private set; } = new();

    // random-seed n: isti broj daje isto pokretanje
    public static void RandomSeed(int seed) => Rng = new Random(seed);

    // clear-all, uz veličinu svijeta i omotavanje (u NetLogo se zadaju u Model Settings).
    // newPatch pravi parcele modela; tako patches-own postaje podklasa Patch.
    public static void ClearAll(int minPxcor = -16, int maxPxcor = 16, int minPycor = -16, int maxPycor = 16,
                                Func<Patch>? newPatch = null, bool wrap = true)
    {
        (MinPxcor, MaxPxcor, MinPycor, MaxPycor) = (minPxcor, maxPxcor, minPycor, maxPycor);
        Wrapping = wrap;
        foreach (var t in turtles) t.inWorld = false;
        turtles.Clear();
        links.Clear();
        nextWho = 0;
        Ticks = 0;
        patches = new Patch[WorldWidth * WorldHeight];
        for (int py = MinPycor; py <= MaxPycor; py++)
            for (int px = MinPxcor; px <= MaxPxcor; px++)
            {
                var p = newPatch?.Invoke() ?? new Patch();
                p.Pxcor = px;
                p.Pycor = py;
                patches[(py - MinPycor) * WorldWidth + (px - MinPxcor)] = p;
            }
    }

    public static void ResetTicks() => Ticks = 0;    // reset-ticks
    public static void Tick() => Ticks++;            // tick: jednom po koraku, izvan svakog Ask

    // create-turtles n [ naredbe ], create-<breeds> n [ naredbe ]:
    // nove turtles stoje u (0, 0) sa slučajnim cijelim headingom; prvo se naprave sve,
    // a zatim svaka izvrši naredbe, slučajnim redom (kao Ask).
    public static List<T> CreateTurtles<T>(int n, Action<T>? commands = null) where T : Turtle, new() =>
        CreateTurtlesAt(n, 0, 0, commands);

    // isto, ali na zadanom mjestu; koristi ga sprout (Patch.Sprout)
    internal static List<T> CreateTurtlesAt<T>(int n, double x, double y, Action<T>? commands) where T : Turtle, new()
    {
        var created = new List<T>();
        for (int i = 0; i < n; i++)
        {
            var t = new T { Heading = Rng.Next(360), X = x, Y = y };
            Add(t);
            created.Add(t);
        }
        if (commands != null) Ask(created, commands);
        return created;
    }

    internal static void Add(Turtle t)
    {
        t.Who = nextWho++;
        turtles.Add(t);
        t.inWorld = true;
        Relocate(t);
    }

    internal static void Remove(Turtle t)
    {
        turtles.Remove(t);
        t.patch?.here.Remove(t);
        t.patch = null;
        t.inWorld = false;
    }

    // turtle se pomjerila: ako je prešla na drugu parcelu, prelazi i u njen spisak turtles-here
    internal static void Relocate(Turtle t)
    {
        if (!t.inWorld) return;
        var p = PatchAt(t.X, t.Y);
        if (ReferenceEquals(p, t.patch)) return;
        t.patch?.here.Remove(t);
        p.Insert(t);
        t.patch = p;
    }

    internal static void AddLink(Link l)
    {
        links.Add(l);
        l.End1.myLinks.Add(l);
        l.End2.myLinks.Add(l);
    }

    internal static void RemoveLink(Link l)
    {
        links.Remove(l);
        l.End1.myLinks.Remove(l);
        l.End2.myLinks.Remove(l);
    }

    // ask skup [ naredbe ]: svaki agent izvrši naredbe, jedan po jedan.
    //  1. redoslijed je slučajan i novi pri svakom pozivu (Shuffle);
    //  2. radi se nad KOPIJOM skupa (Shuffle pravi novu listu): turtle izležena tokom Ask nije na redu,
    //     a promjena liste turtles ne ruši petlju, kao što bi srušila foreach nad samom listom;
    //  3. agent koji umre prije svog reda se preskače;
    //  4. svaki agent vidi promjene koje su napravili agenti prije njega (asinhrono ažuriranje).
    public static void Ask<T>(IEnumerable<T> agents, Action<T> commands) where T : Agent
    {
        foreach (var a in agents.Shuffle())
        {
            if (a.Dead) continue;
            commands(a);   // unutar naredbi: this == a
        }
    }

    public static int Random(int n) => Rng.Next(n);                       // random n: cijeli broj 0 .. n-1
    public static double RandomFloat(double n) => Rng.NextDouble() * n;   // random-float n: 0 <= x < n
    public static double RandomXcor() => MinPxcor - 0.5 + Rng.NextDouble() * WorldWidth;    // random-xcor
    public static double RandomYcor() => MinPycor - 0.5 + Rng.NextDouble() * WorldHeight;   // random-ycor
    public static T OneOf<T>(params T[] items) => items[Rng.Next(items.Length)];           // one-of [ a b ]

    // random-normal sredina devijacija (Box–Muller; NetLogo koristi drugi postupak, raspodjela je ista)
    public static double RandomNormal(double mean, double sd)
    {
        double u1 = 1.0 - Rng.NextDouble(), u2 = Rng.NextDouble();
        return mean + sd * Math.Sqrt(-2 * Math.Log(u1)) * Math.Cos(2 * Math.PI * u2);
    }

    // Torus: koordinata izvan [min-pxcor - 0.5, max-pxcor + 0.5) vraća se sa suprotne strane.
    // U svijetu bez omotavanja koordinata ostaje kakva jeste.
    public static double WrapX(double x) => Wrapping ? Wrap(x, MinPxcor - 0.5, WorldWidth) : x;
    public static double WrapY(double y) => Wrapping ? Wrap(y, MinPycor - 0.5, WorldHeight) : y;

    static double Wrap(double v, double low, int size)
    {
        double r = (v - low) % size;
        if (r < 0) r += size;
        double w = low + r;
        return w >= low + size ? low : w;    // zaštita od greške zaokruživanja
    }

    // patch x y: parcela koja sadrži tačku; parcela pxcor pokriva [pxcor - 0.5, pxcor + 0.5).
    // Zato Math.Floor(x + 0.5), a ne Math.Round(x): Math.Round(2.5) = 2 (zaokružuje na paran broj),
    // a tačka 2.5 pripada parceli 3.
    public static Patch PatchAt(double x, double y) =>
        PatchAtOrNobody(x, y) ?? throw new ArgumentOutOfRangeException(nameof(x), $"tačka ({x}, {y}) je izvan svijeta");

    // isto, ali izvan svijeta bez omotavanja vraća nobody (null), kao patch-at na ivici
    public static Patch? PatchAtOrNobody(double x, double y)
    {
        int px = (int)Math.Floor(WrapX(x) + 0.5), py = (int)Math.Floor(WrapY(y) + 0.5);
        if (px < MinPxcor || px > MaxPxcor || py < MinPycor || py > MaxPycor) return null;
        return patches[(py - MinPycor) * WorldWidth + (px - MinPxcor)];
    }

    // distance: na torusu najkraći put može ići preko ivice
    public static double Distance(double x1, double y1, double x2, double y2)
    {
        double dx = Math.Abs(x1 - x2), dy = Math.Abs(y1 - y2);
        if (Wrapping)
        {
            dx = Math.Min(dx, WorldWidth - dx);
            dy = Math.Min(dy, WorldHeight - dy);
        }
        return Math.Sqrt(dx * dx + dy * dy);
    }
}
