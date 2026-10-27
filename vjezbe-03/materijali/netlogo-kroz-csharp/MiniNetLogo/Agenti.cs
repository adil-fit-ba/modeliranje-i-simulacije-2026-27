namespace MiniNetLogo;

// NetLogo boje su brojevi (green = 55, brown = 35); ovdje je dovoljno nekoliko imena.
public enum Color { Black, White, Gray, Red, Brown, Yellow, Green, Blue, Orange, Sky }

// NetLogo ima četiri vrste agenata: observer, turtles, patches i links.
//   observer — nije klasa: to je kod izvan svakog Ask (Main, Setup, Go)
//   turtles  — Turtle i njene podklase (breed = podklasa)
//   patches  — Patch i njene podklase (patches-own = podklasa)
//   links    — Link: neusmjerena veza između dvije turtles (vježbe 3, blok 3)
public abstract class Agent
{
    // agent koji je umro (die): Ask ga preskače ako još nije došao na red
    public bool Dead { get; internal set; }
}

public class Turtle : Agent
{
    public int Who;                  // who: redni broj, dodjeljuje ga svijet
    public double Heading;           // heading u stepenima: 0 = gore, 90 = desno
    public Color Color = Color.White;
    public double Size = 1;
    public string Shape = "default";

    // xcor, ycor: decimalne koordinate. Svojstva, a ne polja, da svijet zna na kojoj je parceli
    // (turtles-here bez pretraživanja cijelog svijeta).
    double x, y;
    public double X { get => this.x; set { this.x = value; World.Relocate(this); } }
    public double Y { get => this.y; set { this.y = value; World.Relocate(this); } }
    internal Patch? patch;           // parcela u čijem je spisku turtles-here
    internal bool inWorld;           // true od World.Add do Die

    // fd d: korak u smjeru heading. Svijet je torus: izlaskom preko ivice ulazi se sa suprotne strane.
    public void Forward(double d)
    {
        double rad = this.Heading * Math.PI / 180;
        this.X = World.WrapX(this.X + d * Math.Sin(rad));   // sin, jer heading 0 gleda prema +Y
        this.Y = World.WrapY(this.Y + d * Math.Cos(rad));
    }

    public void Right(double degrees) => this.Heading = ((this.Heading + degrees) % 360 + 360) % 360;   // rt
    public void Left(double degrees) => this.Right(-degrees);                                           // lt

    public void SetXY(double x, double y)                                                               // setxy
    {
        this.X = World.WrapX(x);
        this.Y = World.WrapY(y);
    }

    public void MoveTo(Patch p) => this.SetXY(p.Pxcor, p.Pycor);                                        // move-to parcela

    // patch-here: parcela na kojoj turtle stoji
    public Patch PatchHere => this.patch ?? World.PatchAt(this.X, this.Y);

    // pcolor iz turtle: turtle čita i mijenja boju parcele ispod sebe
    public Color Pcolor
    {
        get => this.PatchHere.Pcolor;
        set => this.PatchHere.Pcolor = value;
    }

    public double Distance(Turtle other) => World.Distance(this.X, this.Y, other.X, other.Y);           // distance

    // ---------- veze (links) ----------

    internal List<Link> myLinks = new();
    public IReadOnlyList<Link> MyLinks => this.myLinks;                                                 // my-links

    // link-neighbors: turtles s kojima je ova povezana (kopija, kao NetLogo skup)
    public List<Turtle> LinkNeighbors => this.myLinks.Select(l => l.OtherEnd(this)).ToList();

    // link-neighbor? t
    public bool IsLinkNeighbor(Turtle other) => this.myLinks.Any(l => ReferenceEquals(l.OtherEnd(this), other));

    // create-link-with t: ako veza već postoji, ne nastaje nova
    public Link? CreateLinkWith(Turtle other)
    {
        if (ReferenceEquals(other, this)) throw new InvalidOperationException("turtle ne može napraviti vezu sa sobom");
        if (this.IsLinkNeighbor(other)) return null;
        var link = new Link(this, other);
        World.AddLink(link);
        return link;
    }

    // create-links-with skup
    public void CreateLinksWith(IEnumerable<Turtle> others)
    {
        foreach (var o in others.ToList()) this.CreateLinkWith(o);
    }

    // die: turtle nestaje iz svijeta, a Ask je preskače ako još nije došla na red.
    // S njom nestaju i njene veze, kao u NetLogo.
    // U NetLogo die odmah završava i sve preostale naredbe tog agenta.
    // U C# to ne ide samo od sebe: poslije Die() pozivalac treba return (vidi Go u modelu).
    public void Die()
    {
        if (this.Dead) return;
        this.Dead = true;
        foreach (var l in this.myLinks.ToList()) l.Die();
        World.Remove(this);
    }

    // za hatch: kopija svih polja (i polja iz podklase, npr. Energy), ali bez veza
    internal Turtle Copy()
    {
        var c = (Turtle)this.MemberwiseClone();
        c.myLinks = new();
        c.patch = null;
        c.inWorld = false;
        return c;
    }

    public override string ToString() => $"({this.GetType().Name.ToLower()} {this.Who})";
}

public class Patch : Agent
{
    public int Pxcor, Pycor;         // cijele koordinate; postavlja ih svijet
    public Color Pcolor = Color.Black;

    // turtles-here: NetLogo drži spisak turtles po parceli, pa i ovdje. Poredak je po who, kao u
    // World.Turtles. Spisak se mijenja kad se turtle pomjeri; Ask zato radi nad kopijom (Shuffle).
    internal readonly List<Turtle> here = new();
    public IReadOnlyList<Turtle> TurtlesHere => this.here;

    // <breeds>-here, npr. sheep-here: turtles-here jedne podklase
    public IEnumerable<T> Here<T>() where T : Turtle => this.here.OfType<T>();

    // sprout-<breeds> n [ naredbe ]: nove turtles nastaju na ovoj parceli
    public List<T> Sprout<T>(int n, Action<T>? commands = null) where T : Turtle, new() =>
        World.CreateTurtlesAt(n, this.Pxcor, this.Pycor, commands);

    // neighbors4 i neighbors: susjedne parcele. Na torusu preko ivice; u svijetu bez omotavanja
    // parcela na rubu ima manje susjeda (5 ili 3).
    public IEnumerable<Patch> Neighbors4 =>
        from d in new[] { (0, 1), (1, 0), (0, -1), (-1, 0) }
        let p = World.PatchAtOrNobody(this.Pxcor + d.Item1, this.Pycor + d.Item2)
        where p != null
        select p;

    public IEnumerable<Patch> Neighbors =>
        from dx in new[] { -1, 0, 1 }
        from dy in new[] { -1, 0, 1 }
        where dx != 0 || dy != 0
        let p = World.PatchAtOrNobody(this.Pxcor + dx, this.Pycor + dy)
        where p != null
        select p;

    internal void Insert(Turtle t)
    {
        int i = this.here.Count;
        while (i > 0 && this.here[i - 1].Who > t.Who) i--;
        this.here.Insert(i, t);
    }

    public override string ToString() => $"(patch {this.Pxcor} {this.Pycor})";
}

// link: neusmjerena veza. U NetLogo je i veza agent: ima boju, može se sakriti i umrijeti.
public class Link : Agent
{
    public Turtle End1 { get; }      // end1: kod neusmjerene veze turtle s manjim who
    public Turtle End2 { get; }      // end2
    public Color Color = Color.Gray;
    public bool Hidden;              // hidden?

    internal Link(Turtle a, Turtle b) => (this.End1, this.End2) = a.Who < b.Who ? (a, b) : (b, a);

    public Turtle OtherEnd(Turtle t) => ReferenceEquals(t, this.End1) ? this.End2 : this.End1;   // other-end

    public void Die()                                                                            // die
    {
        if (this.Dead) return;
        this.Dead = true;
        World.RemoveLink(this);
    }

    public override string ToString() => $"(link {this.End1.Who} {this.End2.Who})";
}

public static class TurtleExtensions
{
    // hatch 1 [ naredbe ]: dijete je kopija roditelja (isti breed, iste vrijednosti svih varijabli,
    // ista pozicija i heading), dobije novi who i odmah izvrši svoje naredbe.
    // Dijete NIJE na redu u Ask koji je u toku, jer Ask radi nad kopijom skupa.
    public static T Hatch<T>(this T parent, Action<T>? commands = null) where T : Turtle
    {
        var child = (T)parent.Copy();
        World.Add(child);
        commands?.Invoke(child);
        return child;
    }
}
