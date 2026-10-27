// Vježbe 3, blok 5: mjesto s iskustvom (ustanova kao patch), prevedeno u C# nad MiniNetLogo.
// NetLogo model: nastava/v03/modeli/v03-blok5-ustanova.nlogox
//
// Ustanove su patchevi (mjesta koja stoje) s vlastitom varijablom ustanova?. Ko stane na ustanovu,
// ima iskustvo: loše s vjerovatnoćom udio-losih-iskustava, inače dobro. Iskustvo mijenja povjerenje.
// Razgovor (kao u modelu stava s vježbi 2) prenosi iskustvo i na one koji u ustanovi nisu bili.
// Jedan tick = jedna sedmica.
//
// Desno od C# linija je NetLogo linija iz modela.

using MiniNetLogo;
using static MiniNetLogo.Color;

namespace Blokovi.Ustanova;

// klizači i prekidač s Interface taba (zadane vrijednosti kao u modelu) i globals
public static class Globals
{
    public static double UdioLosihIskustava = 0.7; // udio-losih-iskustava
    public static double PocetnoPovjerenje = 0.5;  // pocetno-povjerenje
    public static int BrojUstanova = 20;           // broj-ustanova
    public static double SnagaIskustva = 0.6;      // snaga-iskustva
    public static int BrojLjudi = 200;             // broj-ljudi
    public static double Domet = 3;                // domet
    public static double Uticaj = 0.2;             // uticaj
    public static bool Razgovor = true;            // razgovor?

    public static double ProsjecnoPovjerenje;      // globals [ prosjecno-povjerenje
    public static double UdioPovjerljivih;         //           udio-povjerljivih     ;; povjerenje > 0,6
    public static double UdioPosjetilaca;          //           udio-posjetilaca ]    ;; bar jednom bili u ustanovi
}

// patches-own: patch s dodatnom varijablom je podklasa klase Patch (kao GrassPatch u Wolf Sheep)
public class UstanovaPatch : Patch                 // patches-own [
{
    public bool Ustanova;                          //   ustanova?  ;; true na mjestu ustanove (šalter, ambulanta, ured) ]
}

public class Covjek : Turtle                       // breed [ ljudi covjek ]  ;; pokretni agenti
{
    public double Povjerenje;                      // ljudi-own [ povjerenje  ;; 0 (nema povjerenja u ustanove) do 1
    public double Integritet;                      //             integritet  ;; 0 (lako se mijenja) do 1 (ne mijenja se)
    public int Posjeta;                            //             posjeta     ;; koliko puta je čovjek bio u ustanovi ]

    static IEnumerable<Covjek> ljudi => World.Turtles.OfType<Covjek>();

    // patch-here vraća Patch; naši patchevi su UstanovaPatch, pa se pretvaraju da bi se vidio ustanova?
    public UstanovaPatch MjestoIspod => (UstanovaPatch)this.PatchHere;   // patch-here

    public void Kreni()                            // to kreni
    {
        this.Right(World.Random(360));             //   right random 360
        this.Forward(1);                           //   forward 1
    }

    public void Iskustvo()                         // to iskustvo
    {
        this.Posjeta += 1;                         //   set posjeta posjeta + 1
        if (World.RandomFloat(1) < Globals.UdioLosihIskustava)   // ifelse random-float 1 < udio-losih-iskustava
            this.Povjerenje += (0 - this.Povjerenje) * (1 - this.Integritet) * Globals.SnagaIskustva;   // [ set povjerenje povjerenje + (0 - povjerenje) * (1 - integritet) * snaga-iskustva ]  ;; loše: prema 0
        else
            this.Povjerenje += (1 - this.Povjerenje) * (1 - this.Integritet) * Globals.SnagaIskustva;   // [ set povjerenje povjerenje + (1 - povjerenje) * (1 - integritet) * snaga-iskustva ]  ;; dobro: prema 1
    }

    public void Razgovaraj()                       // to razgovaraj
    {
        var sagovornik = ljudi.Other(this).InRadius(this, Globals.Domet).OneOf();   // let sagovornik one-of other ljudi in-radius domet
        if (sagovornik != null)                    //   if sagovornik != nobody [
        {
            double razlika = sagovornik.Povjerenje - this.Povjerenje;            // let razlika ([ povjerenje ] of sagovornik) - povjerenje
            this.Povjerenje += razlika * (1 - this.Integritet) * Globals.Uticaj; // set povjerenje povjerenje + razlika * (1 - integritet) * uticaj ]
        }
    }

    public void Oboji()                                    // to oboji
    {
        if (this.Povjerenje > 0.6) this.Color = Blue;      //   ifelse povjerenje > 0.6 [ set color blue ]
        else if (this.Povjerenje < 0.4) this.Color = Red;  //     [ ifelse povjerenje < 0.4 [ set color red ]
        else this.Color = Gray;                            //                               [ set color gray ] ]
    }
}

// observer procedure (setup, go) i reporteri
public static class Blok5Ustanova
{
    static IEnumerable<Covjek> ljudi => World.Turtles.OfType<Covjek>();
    static IEnumerable<UstanovaPatch> patches => World.Patches.Cast<UstanovaPatch>();

    public static void Setup()                     // to setup
    {
        World.ClearAll(-20, 20, -20, 20, () => new UstanovaPatch());   // clear-all (svijet -20 .. 20; patchevi imaju ustanova?)
        World.Ask(patches, p => p.Ustanova = false);                   //   ask patches [ set ustanova? false ]
        World.Ask(patches.NOf(Globals.BrojUstanova), p =>              //   ask n-of broj-ustanova patches [
        {
            p.Ustanova = true;                     //     set ustanova? true
            p.Pcolor = Orange;                     //     set pcolor orange ]
        });
        World.CreateTurtles<Covjek>(Globals.BrojLjudi, c =>   // create-ljudi broj-ljudi [
        {
            c.SetXY(World.RandomXcor(), World.RandomYcor());  //   setxy random-xcor random-ycor
            c.Shape = "person";                    //     set shape "person"
            c.Size = 1.5;                          //     set size 1.5
            c.Povjerenje = Globals.PocetnoPovjerenje;         //     set povjerenje pocetno-povjerenje
            c.Integritet = World.RandomFloat(1);   //     set integritet random-float 1
            c.Posjeta = 0;                         //     set posjeta 0
            c.Oboji();                             //     oboji ]
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
            if (c.MjestoIspod.Ustanova) c.Iskustvo();   //  if [ ustanova? ] of patch-here [ iskustvo ]
            if (Globals.Razgovor) c.Razgovaraj();  //     if razgovor? [ razgovaraj ]
            c.Oboji();                             //     oboji ]
        });
        UpdateMjere();                             //   update-mjere
        World.Tick();                              //   tick
        return true;
    }

    static void UpdateMjere()                      // to update-mjere
    {
        Globals.ProsjecnoPovjerenje = ljudi.Average(c => c.Povjerenje);                          // set prosjecno-povjerenje mean [ povjerenje ] of ljudi
        Globals.UdioPovjerljivih = (double)ljudi.Count(c => c.Povjerenje > 0.6) / ljudi.Count(); // set udio-povjerljivih (count ljudi with [ povjerenje > 0.6 ]) / (count ljudi)
        Globals.UdioPosjetilaca = (double)ljudi.Count(c => c.Posjeta > 0) / ljudi.Count();       // set udio-posjetilaca (count ljudi with [ posjeta > 0 ]) / (count ljudi)
    }

    // prosječno povjerenje onih koji su bili u ustanovi i onih koji nisu (−1 ako takvih nema)
    public static double PovjerenjePosjetilaca()   // to-report povjerenje-posjetilaca
    {
        var p = ljudi.With(c => c.Posjeta > 0);    //   let p ljudi with [ posjeta > 0 ]
        return p.Any() ? p.Average(c => c.Povjerenje) : -1;   // report ifelse-value any? p [ mean [ povjerenje ] of p ] [ -1 ]
    }

    public static double PovjerenjeOstalih()       // to-report povjerenje-ostalih
    {
        var p = ljudi.With(c => c.Posjeta == 0);   //   let p ljudi with [ posjeta = 0 ]
        return p.Any() ? p.Average(c => c.Povjerenje) : -1;   // report ifelse-value any? p [ mean [ povjerenje ] of p ] [ -1 ]
    }
}
