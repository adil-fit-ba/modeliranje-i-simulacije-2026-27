// Wolf Sheep Predation, verzija "sheep-wolves-grass", prevedena u C# nad MiniNetLogo.
//
// Original: Wilensky, U. (1997). NetLogo Wolf Sheep Predation model.
//   http://ccl.northwestern.edu/netlogo/models/WolfSheepPredation
//   Center for Connected Learning and Computer-Based Modeling, Northwestern University, Evanston, IL.
//   U NetLogo: File > Models Library > Sample Models > Biology > Wolf Sheep Predation.
//   Licenca originala je CC BY-NC-SA 3.0; ovaj prijevod je pod istom licencom.
//
// Desno od C# linija je NetLogo linija iz originala. Izostavljeno: verzija "sheep-wolves" bez trave,
// labele (display-labels) i poruka user-message. Prekidač Sinhrono nije u originalu.

using MiniNetLogo;
using static MiniNetLogo.Color;

namespace WolfSheep;

// globals [ max-sheep ], plus klizači i prekidači s Interface taba: u NetLogo su i oni globalne varijable
public static class Globals
{
    public static int MaxSheep = 30000;
    public static int InitialNumberSheep = 100;    // initial-number-sheep
    public static int InitialNumberWolves = 50;    // initial-number-wolves
    public static int GrassRegrowthTime = 30;      // grass-regrowth-time
    public static int SheepGainFromFood = 4;       // sheep-gain-from-food
    public static int WolfGainFromFood = 20;       // wolf-gain-from-food
    public static int SheepReproduce = 4;          // sheep-reproduce (%)
    public static int WolfReproduce = 5;           // wolf-reproduce (%)

    // Nije u originalu. false = kao NetLogo: ovca vidi travu kakva je u tom trenutku, pa travu koju je
    // pojela prethodna ovca više ne vidi (asinhrono). true = sve ovce vide travu s početka ticka,
    // pa više ovaca može pojesti istu travu (sinhrono).
    public static bool Sinhrono = false;
    internal static HashSet<Patch> GreenAtTickStart = new();
}

// turtles-own [ energy ]: varijabla koju imaju obje vrste, pa je u zajedničkoj nadklasi
public abstract class Animal : Turtle
{
    public double Energy;

    public void Move()                                      // to move  ; turtle procedure
    {
        this.Right(World.Random(50));                       //   rt random 50
        this.Left(World.Random(50));                        //   lt random 50
        this.Forward(1);                                    //   fd 1
    }

    public void Death()                                     // to death  ; turtle procedure
    {
        if (this.Energy < 0) this.Die();                    //   if energy < 0 [ die ]
    }
}

public class Sheep : Animal                                 // breed [ sheep a-sheep ]
{
    public void EatGrass()                                  // to eat-grass  ; sheep procedure
    {
        bool green = Globals.Sinhrono
            ? Globals.GreenAtTickStart.Contains(this.PatchHere)
            : this.Pcolor == Green;
        if (green)                                          //   if pcolor = green [
        {
            this.Pcolor = Brown;                            //     set pcolor brown
            this.Energy += Globals.SheepGainFromFood;       //     set energy energy + sheep-gain-from-food ]
        }
    }

    public void ReproduceSheep()                            // to reproduce-sheep  ; sheep procedure
    {
        if (World.RandomFloat(100) < Globals.SheepReproduce)  // if random-float 100 < sheep-reproduce [
        {
            this.Energy /= 2;                               //     set energy (energy / 2)
            this.Hatch(child =>                             //     hatch 1 [ rt random-float 360 fd 1 ] ]
            {
                child.Right(World.RandomFloat(360));
                child.Forward(1);
            });
        }
    }
}

public class Wolf : Animal                                  // breed [ wolves wolf ]
{
    public void EatSheep()                                  // to eat-sheep  ; wolf procedure
    {
        var prey = this.PatchHere.Here<Sheep>().OneOf();    //   let prey one-of sheep-here
        if (prey != null)                                   //   if prey != nobody [
        {
            prey.Die();                                     //     ask prey [ die ]
            this.Energy += Globals.WolfGainFromFood;        //     set energy energy + wolf-gain-from-food ]
        }
    }

    public void ReproduceWolves()                           // to reproduce-wolves  ; wolf procedure
    {
        if (World.RandomFloat(100) < Globals.WolfReproduce)   // if random-float 100 < wolf-reproduce [
        {
            this.Energy /= 2;                               //     set energy (energy / 2)
            this.Hatch(child =>                             //     hatch 1 [ rt random-float 360 fd 1 ] ]
            {
                child.Right(World.RandomFloat(360));
                child.Forward(1);
            });
        }
    }
}

public class GrassPatch : Patch                             // patches-own [ countdown ]
{
    public int Countdown;

    public void GrowGrass()                                   // to grow-grass  ; patch procedure
    {
        if (this.Pcolor == Brown)                             //   if pcolor = brown [
        {
            if (this.Countdown <= 0)                          //     ifelse countdown <= 0
            {
                this.Pcolor = Green;                          //       [ set pcolor green
                this.Countdown = Globals.GrassRegrowthTime;   //         set countdown grass-regrowth-time ]
            }
            else
            {
                this.Countdown -= 1;                          //       [ set countdown countdown - 1 ] ]
            }
        }
    }
}

// Observer procedure (setup, go) i reporteri. Observer nije agent, pa su ovo statične metode.
public static class WolfSheepPredation
{
    // skupovi agenata, s imenima kao u NetLogo
    static IEnumerable<Sheep> sheep => World.Turtles.OfType<Sheep>();
    static IEnumerable<Wolf> wolves => World.Turtles.OfType<Wolf>();
    static IEnumerable<GrassPatch> patches => World.Patches.Cast<GrassPatch>();
    static IEnumerable<GrassPatch> grass => patches.Where(p => p.Pcolor == Green);   // to-report grass

    public static int CountSheep => sheep.Count();          // count sheep
    public static int CountWolves => wolves.Count();        // count wolves
    public static int CountGrass => grass.Count();          // count grass

    public static void Setup()                              // to setup
    {
        World.ClearAll(-25, 25, -25, 25, () => new GrassPatch());   // clear-all (svijet 51 × 51 kao u modelu)
        Globals.MaxSheep = 30000;                           //   set max-sheep 30000

        World.Ask(patches, p =>                             //   ask patches [
        {
            p.Pcolor = World.OneOf(Green, Brown);           //     set pcolor one-of [ green brown ]
            if (p.Pcolor == Green)                          //     ifelse pcolor = green
                p.Countdown = Globals.GrassRegrowthTime;    //       [ set countdown grass-regrowth-time ]
            else
                p.Countdown = World.Random(Globals.GrassRegrowthTime);  // [ set countdown random grass-regrowth-time ] ]
        });

        World.CreateTurtles<Sheep>(Globals.InitialNumberSheep, s =>   // create-sheep initial-number-sheep [
        {
            s.Shape = "sheep";                              //     set shape "sheep"
            s.Color = White;                                //     set color white
            s.Size = 1.5;                                   //     set size 1.5
            s.Energy = World.Random(2 * Globals.SheepGainFromFood);   // set energy random (2 * sheep-gain-from-food)
            s.SetXY(World.RandomXcor(), World.RandomYcor()); //    setxy random-xcor random-ycor ]
        });

        World.CreateTurtles<Wolf>(Globals.InitialNumberWolves, w =>   // create-wolves initial-number-wolves [
        {
            w.Shape = "wolf";                               //     set shape "wolf"
            w.Color = Black;                                //     set color black
            w.Size = 2;                                     //     set size 2
            w.Energy = World.Random(2 * Globals.WolfGainFromFood);    // set energy random (2 * wolf-gain-from-food)
            w.SetXY(World.RandomXcor(), World.RandomYcor()); //    setxy random-xcor random-ycor ]
        });

        World.ResetTicks();                                 //   reset-ticks
    }

    // to go. Vraća false kada bi NetLogo izvršio stop (dugme go forever se tada isključi).
    public static bool Go()
    {
        if (!World.Turtles.Any()) return false;             //   if not any? turtles [ stop ]
        if (!wolves.Any() && CountSheep > Globals.MaxSheep) //   if not any? wolves and count sheep > max-sheep
            return false;                                   //     [ user-message "..." stop ]

        if (Globals.Sinhrono) Globals.GreenAtTickStart = grass.ToHashSet<Patch>();

        World.Ask(sheep, s =>                               //   ask sheep [
        {
            s.Move();                                       //     move
            s.Energy -= 1;                                  //     set energy energy - 1
            s.EatGrass();                                   //     eat-grass
            s.Death();                                      //     death
            if (s.Dead) return;                             //     (u NetLogo die sam prekida ostatak bloka)
            s.ReproduceSheep();                             //     reproduce-sheep ]
        });

        World.Ask(wolves, w =>                              //   ask wolves [
        {
            w.Move();                                       //     move
            w.Energy -= 1;                                  //     set energy energy - 1
            w.EatSheep();                                   //     eat-sheep
            w.Death();                                      //     death
            if (w.Dead) return;
            w.ReproduceWolves();                            //     reproduce-wolves ]
        });

        World.Ask(patches, p => p.GrowGrass());             //   ask patches [ grow-grass ]
        World.Tick();                                       //   tick
        return true;
    }
}
