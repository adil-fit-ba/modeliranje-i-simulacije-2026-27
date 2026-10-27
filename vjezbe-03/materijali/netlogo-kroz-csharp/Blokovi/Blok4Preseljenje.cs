// Vježbe 3, blok 4: preseljenje, prevedeno u C# nad MiniNetLogo.
// NetLogo model: nastava/v03/modeli/v03-blok4-preseljenje.nlogox
//
// Pravilo: ko među susjedima ima manje sličnih od traženog udjela, preseli se.
// Ideja: Schelling (1971); sličan model je u Models Library: Social Science > Segregation.
// Jedan tick = jedan mjesec.
//
// Desno od C# linija je NetLogo linija iz modela.

using MiniNetLogo;
using static MiniNetLogo.Color;

namespace Blokovi.Preseljenje;

// klizači s Interface taba (zadane vrijednosti kao u modelu) i globals
public static class Globals
{
    public static double TrazeniUdioSlicnih = 0.3; // trazeni-udio-slicnih
    public static double Gustina = 0.7;            // gustina

    public static double ProsjecnoSlicnih;         // globals [ prosjecno-slicnih   ;; prosječan udio sličnih među susjedima
    public static double UdioNezadovoljnih;        //           udio-nezadovoljnih ]
}

public class Covjek : Turtle                       // breed [ ljudi covjek ]
{
    public int Grupa;                              // ljudi-own [ grupa        ;; 0 ili 1
    public int Slicnih;                            //             slicnih      ;; broj susjeda iz iste grupe
    public int Susjeda;                            //             susjeda      ;; ukupan broj susjeda
    public bool Zadovoljan;                        //             zadovoljan? ]

    public void PreseliSe() =>                     // to preseli-se
        this.MoveTo(World.Patches.With(p => !p.Here<Covjek>().Any()).OneOf()!);   // move-to one-of patches with [ not any? ljudi-here ]
}

// observer procedure (setup, go, procijeni)
public static class Blok4Preseljenje
{
    static IEnumerable<Covjek> ljudi => World.Turtles.OfType<Covjek>();

    public static void Setup()                     // to setup
    {
        World.ClearAll(-20, 20, -20, 20);          //   clear-all (svijet -20 .. 20 kao u modelu)
        int broj = (int)Math.Floor(Globals.Gustina * World.Patches.Count + 0.5);   // round (gustina * count patches); round ide na veći broj kod .5
        World.Ask(World.Patches.NOf(broj), p =>    //   ask n-of (round (gustina * count patches)) patches [
        {
            p.Sprout<Covjek>(1, c =>               //     sprout-ljudi 1 [
            {
                c.Shape = "square";                //       set shape "square"
                c.Grupa = World.Random(2);         //       set grupa random 2
                c.Color = c.Grupa == 0 ? Sky : Orange;   // set color ifelse-value grupa = 0 [ sky ] [ orange ] ] ]
            });
        });
        Procijeni();                               //   procijeni
        UpdateMjere();                             //   update-mjere
        World.ResetTicks();                        //   reset-ticks
    }

    // to go. Vraća false kada bi NetLogo izvršio stop.
    public static bool Go()
    {
        if (!ljudi.With(c => !c.Zadovoljan).Any()) return false;   // if not any? ljudi with [ not zadovoljan? ] [ stop ]
        World.Ask(ljudi.With(c => !c.Zadovoljan), c => c.PreseliSe());   // ask ljudi with [ not zadovoljan? ] [ preseli-se ]
        Procijeni();                               //   procijeni
        UpdateMjere();                             //   update-mjere
        World.Tick();                              //   tick
        return true;
    }

    static void Procijeni()                        // to procijeni
    {
        World.Ask(ljudi, c =>                      //   ask ljudi [
        {
            var okoMene = c.PatchHere.Neighbors.TurtlesOn<Covjek>();       // let oko-mene ljudi-on neighbors
            c.Susjeda = okoMene.Count;                                     // set susjeda count oko-mene
            // u [ grupa = [ grupa ] of myself ] je this susjed (d), a myself c, iz vanjske lambde
            c.Slicnih = okoMene.Count(d => d.Grupa == c.Grupa);            // set slicnih count oko-mene with [ grupa = [ grupa ] of myself ]
            c.Zadovoljan = c.Slicnih >= Globals.TrazeniUdioSlicnih * c.Susjeda;   // set zadovoljan? slicnih >= trazeni-udio-slicnih * susjeda ]
        });
    }

    static void UpdateMjere()                      // to update-mjere
    {
        var saSusjedima = ljudi.With(c => c.Susjeda > 0);                           // let sa-susjedima ljudi with [ susjeda > 0 ]
        Globals.ProsjecnoSlicnih = saSusjedima.Average(c => (double)c.Slicnih / c.Susjeda);   // set prosjecno-slicnih mean [ slicnih / susjeda ] of sa-susjedima
        Globals.UdioNezadovoljnih = (double)ljudi.Count(c => !c.Zadovoljan) / ljudi.Count();  // set udio-nezadovoljnih (count ljudi with [ not zadovoljan? ]) / (count ljudi)
    }
}
