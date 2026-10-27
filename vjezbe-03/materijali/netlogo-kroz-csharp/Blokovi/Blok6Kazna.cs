// Vježbe 3, blok 6: kontrola i kazna, prevedeno u C# nad MiniNetLogo.
// NetLogo model: nastava/v03/modeli/v03-blok6-kazna.nlogox
//
// Pravilo: ko prekrši pravilo, može biti kažnjen. Kazna smanjuje sklonost kršenju,
// a prekršaj bez kazne je povećava. Ideja: Becker (1968). Jedan tick = jedna sedmica.
//
// Desno od C# linija je NetLogo linija iz modela.

using MiniNetLogo;
using static MiniNetLogo.Color;

namespace Blokovi.Kazna;

// klizači i prekidač s Interface taba (zadane vrijednosti kao u modelu) i globals
public static class Globals
{
    public static double VjerovatnocaKontrole = 0.1;   // vjerovatnoca-kontrole
    public static double JacinaKazne = 0.1;            // jacina-kazne
    public static double PomakBezKazne = 0.02;         // pomak-bez-kazne
    public static int BrojLjudi = 200;                 // broj-ljudi
    public static double Domet = 3;                    // domet
    public static double Uticaj = 0.2;                 // uticaj
    public static bool Razgovor = false;               // razgovor?

    public static double ProsjecnaSklonost;            // globals [ prosjecna-sklonost
    public static double UdioPrekrsaja;                //           udio-prekrsaja
    public static int BrojKaznjenih;                   //           broj-kaznjenih ]
}

public class Covjek : Turtle                           // breed [ ljudi covjek ]  ;; pokretni agenti
{
    public double Sklonost;                            // ljudi-own [ sklonost    ;; 0 do 1: vjerovatnoća prekršaja
    public double Integritet;                          //             integritet  ;; 0 (lako se mijenja) do 1 (ne mijenja se)
    public bool Prekrsio;                              //             prekrsio?
    public bool Kaznjen;                               //             kaznjen? ]

    static IEnumerable<Covjek> ljudi => World.Turtles.OfType<Covjek>();

    public void Kreni()                                // to kreni
    {
        this.Right(World.Random(360));                 //   right random 360
        this.Forward(1);                               //   forward 1
    }

    // jedna prilika za prekršaj: prekrši? → kontrola? → kazna ili prekršaj bez kazne
    public void Prilika()                              // to prilika
    {
        this.Prekrsio = false;                         //   set prekrsio? false
        this.Kaznjen = false;                          //   set kaznjen? false
        if (World.RandomFloat(1) < this.Sklonost)      //   if random-float 1 < sklonost [
        {
            this.Prekrsio = true;                      //     set prekrsio? true
            if (World.RandomFloat(1) < Globals.VjerovatnocaKontrole)    // ifelse random-float 1 < vjerovatnoca-kontrole [
            {
                this.Kaznjen = true;                   //       set kaznjen? true
                this.Sklonost = Math.Max(0, this.Sklonost - Globals.JacinaKazne * (1 - this.Integritet));       // set sklonost max (list 0 (sklonost - jacina-kazne * (1 - integritet)))
            }
            else                                       //     ] [
                this.Sklonost = Math.Min(1, this.Sklonost + Globals.PomakBezKazne * (1 - this.Integritet));     // set sklonost min (list 1 (sklonost + pomak-bez-kazne * (1 - integritet))) ]
        }
    }

    // razgovor kao u modelu stava s vježbi 2: sklonost se približi sklonosti sagovornika
    public void Razgovaraj()                           // to razgovaraj
    {
        var sagovornik = ljudi.Other(this).InRadius(this, Globals.Domet).OneOf();   // let sagovornik one-of other ljudi in-radius domet
        if (sagovornik != null)                        //   if sagovornik != nobody [
        {
            double razlika = sagovornik.Sklonost - this.Sklonost;                  // let razlika ([ sklonost ] of sagovornik) - sklonost
            this.Sklonost += razlika * (1 - this.Integritet) * Globals.Uticaj;     // set sklonost sklonost + razlika * (1 - integritet) * uticaj ]
        }
    }

    public void Oboji()                                // to oboji
    {
        if (this.Kaznjen) this.Color = Yellow;         //   ifelse kaznjen? [ set color yellow ]
        else if (this.Sklonost > 0.75) this.Color = Red;   //   [ ifelse sklonost > 0.75 [ set color red ]
        else if (this.Sklonost < 0.25) this.Color = Sky;   //     [ ifelse sklonost < 0.25 [ set color sky ]
        else this.Color = Gray;                        //                              [ set color gray ] ] ]
    }
}

// observer procedure (setup, go)
public static class Blok6Kazna
{
    static IEnumerable<Covjek> ljudi => World.Turtles.OfType<Covjek>();

    public static void Setup()                         // to setup
    {
        World.ClearAll(-20, 20, -20, 20);              //   clear-all (svijet -20 .. 20 kao u modelu)
        World.CreateTurtles<Covjek>(Globals.BrojLjudi, c =>   // create-ljudi broj-ljudi [
        {
            c.SetXY(World.RandomXcor(), World.RandomYcor());  //   setxy random-xcor random-ycor
            c.Shape = "person";                        //     set shape "person"
            c.Size = 1.5;                              //     set size 1.5
            c.Sklonost = World.RandomFloat(1);         //     set sklonost random-float 1
            c.Integritet = World.RandomFloat(1);       //     set integritet random-float 1
            c.Prekrsio = false;                        //     set prekrsio? false
            c.Kaznjen = false;                         //     set kaznjen? false
            c.Oboji();                                 //     oboji ]
        });
        UpdateMjere();                                 //   update-mjere
        World.ResetTicks();                            //   reset-ticks
    }

    // to go. Model nema stop, pa uvijek vraća true.
    public static bool Go()
    {
        World.Ask(ljudi, c =>                          //   ask ljudi [
        {
            c.Kreni();                                 //     kreni
            if (Globals.Razgovor) c.Razgovaraj();      //     if razgovor? [ razgovaraj ]
            c.Prilika();                               //     prilika
            c.Oboji();                                 //     oboji ]
        });
        UpdateMjere();                                 //   update-mjere
        World.Tick();                                  //   tick
        return true;
    }

    static void UpdateMjere()                          // to update-mjere
    {
        Globals.ProsjecnaSklonost = ljudi.Average(c => c.Sklonost);                         // set prosjecna-sklonost mean [ sklonost ] of ljudi
        Globals.UdioPrekrsaja = (double)ljudi.Count(c => c.Prekrsio) / ljudi.Count();       // set udio-prekrsaja (count ljudi with [ prekrsio? ]) / (count ljudi)
        Globals.BrojKaznjenih = ljudi.Count(c => c.Kaznjen);                                // set broj-kaznjenih count ljudi with [ kaznjen? ]
    }
}
