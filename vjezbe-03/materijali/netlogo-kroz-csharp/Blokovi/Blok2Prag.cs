// Vježbe 3, blok 2: prag i kaskada, prevedeno u C# nad MiniNetLogo.
// NetLogo model: nastava/v03/modeli/v03-blok2-prag.nlogox
//
// Sala: na svakom mjestu sjedi jedan čovjek i vidi svojih (do) 8 susjeda.
// Pravilo: čovjek ustane kad je udio susjeda koji stoje barem njegov prag; ostaje stajati.
// Ideja: Granovetter (1978). Jedan tick = jedan krug odluke (nekoliko sekundi).
//
// Desno od C# linija je NetLogo linija iz modela.

using MiniNetLogo;
using static MiniNetLogo.Color;

namespace Blokovi.Prag;

// klizači s Interface taba (zadane vrijednosti kao u modelu) i globals
public static class Globals
{
    public static double ProsjekPraga = 0.3;       // prosjek-praga
    public static double RasipanjePraga = 0.1;     // rasipanje-praga
    public static int Pokretaci = 10;              // pokretaci

    public static double UdioAktivnih;             // globals [ udio-aktivnih ]
}

public class Covjek : Turtle                       // breed [ ljudi covjek ]
{
    public bool Aktivan;                           // ljudi-own [ aktivan?   ;; true kad je ustao (ostaje stajati)
    public double MojPrag;                         //             moj-prag   ;; udio susjeda koji stoje potreban da ustanem, 0 do 1 ]

    public double UdioOkoMene()                    // to-report udio-oko-mene
    {
        var okoMene = this.PatchHere.Neighbors.TurtlesOn<Covjek>();   //   let oko-mene ljudi-on neighbors
        return (double)okoMene.Count(c => c.Aktivan) / okoMene.Count;   // report (count oko-mene with [ aktivan? ]) / (count oko-mene)
    }

    public void Oboji() => this.Color = this.Aktivan ? Orange : Gray;   // to oboji: set color ifelse-value aktivan? [ orange ] [ gray - 2 ]
}

// observer procedure (setup, go)
public static class Blok2Prag
{
    static IEnumerable<Covjek> ljudi => World.Turtles.OfType<Covjek>();

    public static void Setup()                     // to setup
    {
        World.ClearAll(-15, 15, -15, 15, wrap: false);   // clear-all (svijet -15 .. 15, bez omotavanja: sala ima zidove)
        World.Ask(World.Patches, p =>              //   ask patches [
        {
            p.Sprout<Covjek>(1, c =>               //     sprout-ljudi 1 [
            {
                c.Shape = "person";                //       set shape "person"
                c.MojPrag = Ogranici(World.RandomNormal(Globals.ProsjekPraga, Globals.RasipanjePraga));   // set moj-prag ogranici (random-normal prosjek-praga rasipanje-praga)
                c.Aktivan = false;                 //       set aktivan? false ] ]
            });
        });
        World.Ask(ljudi.NOf(Globals.Pokretaci), c => c.Aktivan = true);   // ask n-of pokretaci ljudi [ set aktivan? true ]
        World.Ask(ljudi, c => c.Oboji());          //   ask ljudi [ oboji ]
        UpdateMjere();                             //   update-mjere
        World.ResetTicks();                        //   reset-ticks
    }

    static double Ogranici(double x) => Math.Max(0, Math.Min(1, x));   // to-report ogranici [ x ]  report max (list 0 (min (list 1 x)))

    // to go. Vraća false kada bi NetLogo izvršio stop.
    public static bool Go()
    {
        // with prvo izabere sve koji ustaju (prema stanju na početku kruga), pa ih tek onda pita
        var ustaju = ljudi.With(c => !c.Aktivan && c.UdioOkoMene() >= c.MojPrag);   // let ustaju ljudi with [ not aktivan? and udio-oko-mene >= moj-prag ]
        if (!ustaju.Any()) return false;           //   if not any? ustaju [ stop ]
        World.Ask(ustaju, c =>                     //   ask ustaju [
        {
            c.Aktivan = true;                      //     set aktivan? true
            c.Oboji();                             //     oboji ]
        });
        UpdateMjere();                             //   update-mjere
        World.Tick();                              //   tick
        return true;
    }

    static void UpdateMjere() =>                   // to update-mjere
        Globals.UdioAktivnih = (double)ljudi.Count(c => c.Aktivan) / ljudi.Count();   // set udio-aktivnih (count ljudi with [ aktivan? ]) / (count ljudi)
}
