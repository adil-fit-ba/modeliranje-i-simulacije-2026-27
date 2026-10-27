// Vježbe 3, blok 1: ograničeno povjerenje, prevedeno u C# nad MiniNetLogo.
// NetLogo model: nastava/v03/modeli/v03-blok1-povjerenje.nlogox
//
// Polazi od modela stava s vježbi 2, uz tačku 3 zadatka (mijenja se i sagovornik).
// Novo pravilo: razgovor mijenja stav samo ako se stavovi razlikuju manje od praga.
// Ideja: Deffuant, Neau, Amblard i Weisbuch (2000). Jedan tick = jedna sedmica.
//
// Desno od C# linija je NetLogo linija iz modela.

using MiniNetLogo;
using static MiniNetLogo.Color;

namespace Blokovi.Povjerenje;

// klizači i prekidač s Interface taba (zadane vrijednosti kao u modelu) i globals
public static class Globals
{
    public static double Prag = 0.5;               // prag
    public static int BrojLjudi = 200;             // broj-ljudi
    public static int BrojMedija = 4;              // broj-medija
    public static double Domet = 3;                // domet
    public static double Uticaj = 0.2;             // uticaj
    public static double PorukaMedija = 1;         // poruka-medija
    public static double SnagaMedija = 0.1;        // snaga-medija
    public static double DometMedija = 8;          // domet-medija
    public static bool MedijiRade = false;         // mediji-rade?

    public static double ProsjecanStav;            // globals [ prosjecan-stav
    public static double UdioZa;                   //           udio-za
    public static int BrojGrupa;                   //           broj-grupa ]
}

public class Covjek : Turtle                       // breed [ ljudi covjek ]  ;; pokretni agenti
{
    public double Stav;                            // ljudi-own [ stav        ;; -1 (protiv) do +1 (za)
    public double Integritet;                      //             integritet  ;; 0 (lako se mijenja) do 1 (ne mijenja se) ]

    static IEnumerable<Covjek> ljudi => World.Turtles.OfType<Covjek>();
    static IEnumerable<Medij> mediji => World.Turtles.OfType<Medij>();

    public void Kreni()                            // to kreni
    {
        this.Right(World.Random(360));             //   right random 360
        this.Forward(1);                           //   forward 1
    }

    public void Razgovaraj()                       // to razgovaraj
    {
        var sagovornik = ljudi.Other(this).InRadius(this, Globals.Domet).OneOf();   // let sagovornik one-of other ljudi in-radius domet
        if (sagovornik != null)                    //   if sagovornik != nobody [
        {
            double razlika = sagovornik.Stav - this.Stav;     // let razlika ([ stav ] of sagovornik) - stav
            if (Math.Abs(razlika) < Globals.Prag)             // if abs razlika < prag [   ;; NOVO
            {
                double mojStav = this.Stav;                   //   let moj-stav stav       ;; sačuvati prije promjene
                this.Stav += razlika * (1 - this.Integritet) * Globals.Uticaj;   // set stav stav + razlika * (1 - integritet) * uticaj
                // ask sagovornik [ ... ]: unutar lambde this je s (sagovornik), a ovaj Covjek izvana
                // je myself. U C# je myself obična varijabla iz vanjskog opsega (closure).
                World.Ask(new[] { sagovornik }, s =>          //   ask sagovornik [
                {
                    s.Stav += (mojStav - s.Stav) * (1 - s.Integritet) * Globals.Uticaj;   // set stav stav + (moj-stav - stav) * (1 - integritet) * uticaj
                    s.Oboji();                                //     oboji ]
                });
            }
        }
    }

    public void SlusajMedije()                     // to slusaj-medije
    {
        if (mediji.InRadius(this, Globals.DometMedija).Any())                // if any? mediji in-radius domet-medija [
        {
            if (Math.Abs(Globals.PorukaMedija - this.Stav) < Globals.Prag)   //   if abs (poruka-medija - stav) < prag [   ;; NOVO
                this.Stav += (Globals.PorukaMedija - this.Stav) * (1 - this.Integritet) * Globals.SnagaMedija;   // set stav stav + (poruka-medija - stav) * (1 - integritet) * snaga-medija
        }
    }

    public void Oboji()                                // to oboji
    {
        if (this.Stav > 0.2) this.Color = Blue;        //   ifelse stav > 0.2 [ set color blue ]
        else if (this.Stav < -0.2) this.Color = Red;   //     [ ifelse stav < -0.2 [ set color red ]
        else this.Color = Gray;                        //                          [ set color gray ] ]
    }
}

public class Medij : Turtle { }                    // breed [ mediji medij ]  ;; stacionarni agenti (izvor poruke)

// observer procedure (setup, go) i reporter izbroji-grupe
public static class Blok1Povjerenje
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

    // to go. Model nema stop, pa uvijek vraća true.
    public static bool Go()
    {
        World.Ask(ljudi, c =>                      //   ask ljudi [
        {
            c.Kreni();                             //     kreni
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
        Globals.BrojGrupa = IzbrojiGrupe();                                          // set broj-grupa izbroji-grupe
    }

    // Grupa = niz stavova (poredanih po veličini) u kojem su susjedne vrijednosti bliže od 0,1.
    // Broje se samo grupe s barem 5% ljudi.
    static int IzbrojiGrupe()                      // to-report izbroji-grupe
    {
        var s = ljudi.Select(c => c.Stav).OrderBy(v => v).ToList();   // let s sort [ stav ] of ljudi
        double najmanje = 0.05 * s.Count;          //   let najmanje 0.05 * length s
        int grupe = 0;                             //   let grupe 0
        int velicina = 1;                          //   let velicina 1
        for (int i = 1; i < s.Count; i++)          //   let i 1  while [ i < length s ] [ ... set i i + 1 ]
        {
            if (s[i] - s[i - 1] < 0.1)             //     ifelse (item i s) - (item (i - 1) s) < 0.1
                velicina++;                        //       [ set velicina velicina + 1 ]
            else
            {
                if (velicina >= najmanje) grupe++; //       [ if velicina >= najmanje [ set grupe grupe + 1 ]
                velicina = 1;                      //         set velicina 1 ]
            }
        }
        if (velicina >= najmanje) grupe++;         //   if velicina >= najmanje [ set grupe grupe + 1 ]
        return grupe;                              //   report grupe
    }
}
