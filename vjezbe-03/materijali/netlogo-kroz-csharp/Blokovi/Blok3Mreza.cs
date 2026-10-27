// Vježbe 3, blok 3: mreža poznanstava (links), prevedeno u C# nad MiniNetLogo.
// NetLogo model: nastava/v03/modeli/v03-blok3-mreza.nlogox
//
// Polazi od modela stava s vježbi 2. Ljudi ne šetaju; razgovaraju samo s poznanicima.
// Poznanici su najbliži ljudi; dio veza vodi do nekoga bilo gdje u svijetu.
// Ideja (daleke veze): Watts i Strogatz (1998). Jedan tick = jedna sedmica.
//
// Desno od C# linija je NetLogo linija iz modela.

using MiniNetLogo;
using static MiniNetLogo.Color;

namespace Blokovi.Mreza;

// klizači i prekidači s Interface taba (zadane vrijednosti kao u modelu) i globals
public static class Globals
{
    public static double UdioDalekihVeza = 0;      // udio-dalekih-veza
    public static int BrojVeza = 3;                // broj-veza
    public static int BrojLjudi = 200;             // broj-ljudi
    public static int BrojMedija = 2;              // broj-medija
    public static double Uticaj = 0.2;             // uticaj
    public static double PorukaMedija = 1;         // poruka-medija
    public static double SnagaMedija = 0.1;        // snaga-medija
    public static double DometMedija = 5;          // domet-medija
    public static bool MedijiRade = true;          // mediji-rade?
    public static bool PrikaziVeze = true;         // prikazi-veze?

    public static double ProsjecanStav;            // globals [ prosjecan-stav
    public static double UdioZa;                   //           udio-za ]
}

public class Covjek : Turtle                       // breed [ ljudi covjek ]  ;; ljudi stoje (kuća, posao)
{
    public double Stav;                            // ljudi-own [ stav        ;; -1 (protiv) do +1 (za)
    public double Integritet;                      //             integritet  ;; 0 (lako se mijenja) do 1 (ne mijenja se) ]

    static IEnumerable<Medij> mediji => World.Turtles.OfType<Medij>();

    public void Razgovaraj()                       // to razgovaraj
    {
        var sagovornik = this.LinkNeighbors.OfType<Covjek>().OneOf();   // let sagovornik one-of link-neighbors   ;; NOVO: poznanik
        if (sagovornik != null)                    //   if sagovornik != nobody [
        {
            double razlika = sagovornik.Stav - this.Stav;                    // let razlika ([ stav ] of sagovornik) - stav
            this.Stav += razlika * (1 - this.Integritet) * Globals.Uticaj;   // set stav stav + razlika * (1 - integritet) * uticaj ]
        }
    }

    public void SlusajMedije()                     // to slusaj-medije
    {
        if (mediji.InRadius(this, Globals.DometMedija).Any())      // if any? mediji in-radius domet-medija [
            this.Stav += (Globals.PorukaMedija - this.Stav) * (1 - this.Integritet) * Globals.SnagaMedija;   // set stav stav + (poruka-medija - stav) * (1 - integritet) * snaga-medija ]
    }

    public void Oboji()                                // to oboji
    {
        if (this.Stav > 0.2) this.Color = Blue;        //   ifelse stav > 0.2 [ set color blue ]
        else if (this.Stav < -0.2) this.Color = Red;   //     [ ifelse stav < -0.2 [ set color red ]
        else this.Color = Gray;                        //                          [ set color gray ] ]
    }
}

public class Medij : Turtle { }                    // breed [ mediji medij ]  ;; stacionarni agenti (izvor poruke)

// observer procedure (setup, napravi-mrezu, go)
public static class Blok3Mreza
{
    static IEnumerable<Covjek> ljudi => World.Turtles.OfType<Covjek>();

    public static void Setup()                     // to setup
    {
        World.ClearAll(-20, 20, -20, 20);          //   clear-all (svijet -20 .. 20 kao u modelu)
        World.CreateTurtles<Covjek>(Globals.BrojLjudi, c =>   // create-ljudi broj-ljudi [
        {
            c.SetXY(World.RandomXcor(), World.RandomYcor());  //   setxy random-xcor random-ycor
            c.Shape = "person";                    //     set shape "person"
            c.Size = 1.5;                          //     set size 1.5
            c.Stav = World.RandomFloat(2) - 1;     //     set stav (random-float 2) - 1
            c.Integritet = World.RandomFloat(1);   //     set integritet random-float 1
            c.Oboji();                             //     oboji ]
        });
        NapraviMrezu();                            //   napravi-mrezu
        World.CreateTurtles<Medij>(Globals.BrojMedija, m =>   // create-mediji broj-medija [
        {
            m.SetXY(World.RandomXcor(), World.RandomYcor());  //   setxy random-xcor random-ycor
            m.Shape = "house";                     //     set shape "house"
            m.Size = 3;                            //     set size 3
            m.Color = Yellow;                      //     set color yellow ]
        });
        UpdateMjere();                             //   update-mjere
        World.ResetTicks();                        //   reset-ticks
    }

    static void NapraviMrezu()                     // to napravi-mrezu
    {
        // svako se upozna s nekoliko najbližih ljudi. U [ distance myself ] je this kandidat (d),
        // a myself onaj koji traži poznanike (c), varijabla iz vanjske lambde.
        World.Ask(ljudi, c =>                      //   ask ljudi [
            c.CreateLinksWith(ljudi.Other(c).MinNOf(Globals.BrojVeza, d => d.Distance(c))));   // create-links-with min-n-of broj-veza other ljudi [ distance myself ] ]

        // dio veza se zamijeni vezom s nekim bilo gdje u svijetu.
        // Ask radi nad kopijom spiska veza: nova veza napravljena tokom Ask nije na redu.
        World.Ask(World.Links, l =>                //   ask links [
        {
            if (World.RandomFloat(1) < Globals.UdioDalekihVeza)    // if random-float 1 < udio-dalekih-veza [
            {
                var a = l.End1;                    //       let a end1
                var novi = ljudi.With(d => !ReferenceEquals(d, a) && !d.IsLinkNeighbor(a)).OneOf();   // let novi one-of ljudi with [ self != a and not link-neighbor? a ]
                if (novi != null)                  //       if novi != nobody [
                {
                    World.Ask(new[] { a }, x => x.CreateLinkWith(novi));   // ask a [ create-link-with novi ]
                    l.Die();                       //         die ] ] ]
                }
            }
        });
        World.Ask(World.Links, l =>                //   ask links [
        {
            l.Color = Gray;                        //     set color gray - 2
            l.Hidden = !Globals.PrikaziVeze;       //     set hidden? not prikazi-veze? ]
        });
    }

    // to go. Model nema stop, pa uvijek vraća true.
    public static bool Go()
    {
        World.Ask(ljudi, c =>                      //   ask ljudi [
        {
            c.Razgovaraj();                        //     razgovaraj
            if (Globals.MedijiRade) c.SlusajMedije();   // if mediji-rade? [ slusaj-medije ]
            c.Oboji();                             //     oboji ]
        });
        UpdateMjere();                             //   update-mjere
        World.Tick();                              //   tick
        return true;
    }

    static void UpdateMjere()                      // to update-mjere
    {
        Globals.ProsjecanStav = ljudi.Average(c => c.Stav);                          // set prosjecan-stav mean [ stav ] of ljudi
        Globals.UdioZa = (double)ljudi.Count(c => c.Stav > 0.2) / ljudi.Count();     // set udio-za (count ljudi with [ stav > 0.2 ]) / (count ljudi)
    }

    // monitor „poznanika po osobi“: mean [ count link-neighbors ] of ljudi
    public static double PoznanikaPoOsobi => ljudi.Average(c => c.LinkNeighbors.Count);
}
