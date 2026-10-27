namespace MiniNetLogo;

// Skupovi agenata (agentsets). Veći dio NetLogo primitiva već postoji u LINQ:
//   count skup             -> skup.Count()
//   any? skup              -> skup.Any()
//   [ energy ] of skup     -> skup.Select(a => a.Energy)    (NetLogo vraća listu slučajnim redom)
//   [ energy ] of agent    -> agent.Energy
//   mean [ energy ] of s   -> s.Average(a => a.Energy)
//   max-one-of s [ x ]     -> s.MaxBy(a => a.X)
//   breed, npr. sheep      -> World.Turtles.OfType<Sheep>()
// Ovdje su samo oni koji u LINQ nemaju isto ime ili isto ponašanje.
public static class Agentsets
{
    // shuffle: kopija u slučajnom redoslijedu (Fisher–Yates). Ask je foreach nad Shuffle().
    public static List<T> Shuffle<T>(this IEnumerable<T> source)
    {
        var list = source.ToList();
        for (int i = list.Count - 1; i > 0; i--)
        {
            int j = World.Rng.Next(i + 1);
            (list[i], list[j]) = (list[j], list[i]);
        }
        return list;
    }

    // skup with [ uslov ]: novi skup, napravljen ODMAH (ToList); kasnije promjene ga ne mijenjaju
    public static List<T> With<T>(this IEnumerable<T> source, Func<T, bool> condition) =>
        source.Where(condition).ToList();

    // one-of skup: slučajan agent; iz praznog skupa dolazi nobody, a nobody je u C# null
    public static T? OneOf<T>(this IEnumerable<T> source) where T : class
    {
        var list = source.ToList();
        return list.Count == 0 ? null : list[World.Rng.Next(list.Count)];
    }

    // other skup: svi osim agenta koji pita
    public static IEnumerable<T> Other<T>(this IEnumerable<T> source, Agent me) =>
        source.Where(a => !ReferenceEquals(a, me));

    // skup in-radius r: agenti na udaljenosti <= r (na torusu)
    public static IEnumerable<T> InRadius<T>(this IEnumerable<T> source, Turtle me, double radius) where T : Turtle =>
        source.Where(t => me.Distance(t) <= radius);

    // n-of n skup: n slučajno izabranih agenata
    public static List<T> NOf<T>(this IEnumerable<T> source, int n) => source.Shuffle().Take(n).ToList();

    // min-n-of n skup [ izraz ]: n agenata s najmanjom vrijednošću izraza; jednake vrijednosti
    // dolaze slučajnim redom (zato Shuffle prije OrderBy, koji čuva poredak jednakih)
    public static List<T> MinNOf<T>(this IEnumerable<T> source, int n, Func<T, double> reporter) =>
        source.Shuffle().OrderBy(reporter).Take(n).ToList();

    // <breeds>-on skup-parcela, npr. ljudi-on neighbors: turtles jedne podklase na tim parcelama
    public static List<T> TurtlesOn<T>(this IEnumerable<Patch> patches) where T : Turtle =>
        patches.SelectMany(p => p.Here<T>()).ToList();
}
