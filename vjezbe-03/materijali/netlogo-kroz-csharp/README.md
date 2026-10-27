# NetLogo kroz C#

Mali C# projekat koji pokazuje kako NetLogo radi „ispod haube“. Nije zamjena za NetLogo: nema
grafike, interfejsa ni većine primitiva. Ima onoliko koliko treba da se razumiju turtles, patches,
`ask`, skupovi agenata i jedan cijeli model s interakcijama.

Imena metoda su ista kao u C# kodu na slajdovima (`Shuffle`, `PatchHere`, `Pcolor`, `Neighbors4`,
`Die`, `Forward`, `Right`), pa se ono što je na slajdu prikazano kao `{…}` ovdje može otvoriti,
pokrenuti i proći korak po korak.

## Pokretanje

Potreban je .NET SDK 8 ili noviji. Iz foldera projekta:

```
dotnet run -- pojmovi
dotnet run -- model --seed 1 --ticks 500 --mapa 100
dotnet run -- model --seed 1 --sinhrono
dotnet run -- eksperiment --ponavljanja 20 --ticks 500
dotnet run -- blokovi [--blok 1..6] [--ponavljanja n] [--seed 1]
```

U Visual Studiju: otvoriti `NetLogoKrozCSharp.csproj`, izabrati profil (pojmovi, model, model
sinhrono, eksperiment, blokovi) pored dugmeta za pokretanje i pokrenuti s F5.

Ako je folder u OneDrive-u, `Directory.Build.props` šalje `bin` i `obj` u
`%LOCALAPPDATA%\VSBuild\NetLogoKrozCSharp\`, da se build fajlovi ne sinhronizuju. Izvan OneDrive-a
su na uobičajenom mjestu, pored projekta.

Najviše se nauči u debuggeru. Breakpoint u `Sheep.EatGrass` ili unutar lambde u `World.Ask` pokazuje
ko je `this`, koliko je turtles u svijetu (`World.Turtles.Count`) i koji je tick (`World.Ticks`).
To je pitanje iz vježbi 2: za svaku liniju, ko je ovdje `this`?

## Šta je gdje

| Fajl | Sadržaj |
|---|---|
| `MiniNetLogo/Agenti.cs` | `Turtle`, `Patch`, `Link`, `Hatch`, `Sprout`; boje |
| `MiniNetLogo/Svijet.cs` | `World`: parcele, turtles, veze, ticks, `Ask`, slučajni brojevi, torus ili svijet s ivicama |
| `MiniNetLogo/Skupovi.cs` | `Shuffle`, `With`, `OneOf`, `Other`, `InRadius`, `NOf`, `MinNOf`, `TurtlesOn` i tabela LINQ ekvivalenata |
| `WolfSheep/WolfSheepPredation.cs` | model Wolf Sheep Predation, linija uz liniju s originalom |
| `Blokovi/` | šest blokova interakcije s vježbi 3, linija uz liniju s NetLogo modelima |
| `Pojmovi.cs` | sedam kratkih primjera s rezultatom koji daje NetLogo |
| `Program.cs` | pokretanje: `pojmovi`, `model`, `eksperiment`, `blokovi` |
| `provjera/` | NetLogo eksperiment, rezultati oba jezika, `uporedi.py`; `blokovi-csharp.txt` |

## NetLogo i C#

| NetLogo | C# u ovom projektu |
|---|---|
| observer | kod izvan svakog `Ask`: `Setup`, `Go`, `Main` |
| `breed [ sheep a-sheep ]` | `class Sheep : Animal` |
| `turtles-own [ energy ]` | polje `Energy` u zajedničkoj nadklasi `Animal` |
| `patches-own [ countdown ]` | `class GrassPatch : Patch` |
| `globals`, klizači, prekidači | `static class Globals` |
| `ask sheep [ ... ]` | `World.Ask(sheep, s => { ... })` |
| `sheep` | `World.Turtles.OfType<Sheep>()` |
| `sheep-here` | `PatchHere.Here<Sheep>()` |
| `one-of ...`, `nobody` | `.OneOf()`, `null` |
| `turtles with [ ... ]` | `.With(...)` |
| `count`, `any?`, `[ x ] of`, `mean` | `Count()`, `Any()`, `Select`, `Average` |
| `hatch 1 [ ... ]` | `this.Hatch(d => { ... })` |
| `die` | `Die()`, a zatim `return` |
| `fd`, `rt`, `lt`, `setxy` | `Forward`, `Right`, `Left`, `SetXY` |
| `pcolor` iz turtle | `Pcolor`, svojstvo koje čita i mijenja `PatchHere` |
| `tick`, `reset-ticks`, `ticks` | `World.Tick()`, `World.ResetTicks()`, `World.Ticks` |
| `random`, `random-float`, `random-xcor` | `World.Random`, `World.RandomFloat`, `World.RandomXcor` |
| `random-seed` | `World.RandomSeed` |
| dugmad setup i go (forever) | `Setup(); while (Go()) { }` |
| BehaviorSpace | `dotnet run -- eksperiment` |
| `myself` | varijabla iz vanjske lambde: `World.Ask(ljudi, c => ... d => d.Distance(c))` |
| `create-links-with`, `link-neighbors`, `link-neighbor?` | `CreateLinksWith`, `LinkNeighbors`, `IsLinkNeighbor` |
| `ask links [ ... ]`, `end1`, `die` (veza) | `World.Ask(World.Links, l => { ... })`, `l.End1`, `l.Die()` |
| `sprout-ljudi 1 [ ... ]`, `move-to` | `p.Sprout<Covjek>(1, c => { ... })`, `MoveTo(p)` |
| `ljudi-on neighbors` | `PatchHere.Neighbors.TurtlesOn<Covjek>()` |
| `n-of`, `min-n-of n s [ x ]` | `NOf(n)`, `MinNOf(n, a => a.X)` |
| `random-normal` | `World.RandomNormal` |
| svijet bez omotavanja (Model Settings) | `World.ClearAll(..., wrap: false)` |

## Sedam pojmova (`dotnet run -- pojmovi`)

Rezultati u zagradama dao je NetLogo 7.0.4 za isti kod; C# daje iste.

1. **`ask` ide slučajnim redom**, novim pri svakom pozivu. `Ask` je `foreach` nad `Shuffle()`.
2. **`with` ili `if`.** Tri crvene turtles; svaka crvena oboji ostale u plavo. S `if` naredbe se
   izvrše jednom (prva oboji ostale, one to vide kada dođu na red). S `with` tri puta, jer je skup
   izabran prije petlje. To je asinhrono ažuriranje: agent vidi promjene prethodnih agenata.
3. **`die` tokom `ask`.** `ask turtles [ ask other turtles [ die ] ]` s 10 turtles ostavi 1:
   ostale su mrtve prije svog reda i preskaču se. Obični `foreach` nad listom koja se mijenja baca
   `InvalidOperationException`; zato `Ask` radi nad kopijom.
4. **`hatch` tokom `ask`.** Pet turtles uz `hatch 1` daje deset; na redu je bilo pet, jer nove
   turtles nisu u skupu nad kojim `ask` radi. Dijete je kopija roditelja (`MemberwiseClone`).
5. **Torus.** S x = 25,2 korak udesno vodi na x = −24,8, a udaljenost između x = −25 i x = 25 je 1.
6. **`patch-here`.** Tačka 2,5 pripada parceli 3, a tačka −2,5 parceli −2. C# `Math.Round` polovinu
   zaokružuje na paran broj (2,5 → 2), pa `PatchAt` koristi `Math.Floor(x + 0.5)`.
7. **`nobody` je `null`.** Zato iza `one-of` ide provjera `if prey != nobody`.

## Model: Wolf Sheep Predation s travom

Tri vrste agenata djeluju jedna na drugu: ovce jedu travu, vukovi jedu ovce, trava ponovo raste
poslije 30 tickova. Ovce i vukovi troše energiju na kretanje, umiru kada im energija padne ispod
nule i razmnožavaju se s vjerovatnoćom 4 % i 5 % po ticku. Model koristi gotovo sve iz tabele
iznad: dva breeda, `turtles-own`, `patches-own`, `hatch` i `die` usred `ask`, `one-of sheep-here`,
`pcolor` iz turtle i stop uslov.

Prekidač `--sinhrono` nije u originalu. Bez njega ovca vidi travu kakva je u tom trenutku, pa travu
koju je pojela prethodna ovca više ne vidi (kao NetLogo). S njim sve ovce vide travu s početka
ticka, pa više ovaca može pojesti istu travu.

## Provjera: C# i NetLogo daju isto ponašanje

20 pokretanja po 500 tickova, zadani parametri, verzija s travom. Vrijednosti su od ticka 100
(prvih 100 tickova je prelaz od početnog stanja); raspon je od najmanjeg do najvećeg pokretanja,
u zagradi sredina.

| | NetLogo 7.0.4 | C# | C# sinhrono |
|---|---|---|---|
| prosječan broj ovaca | 156–174 (164) | 149–173 (162) | 156–173 (163) |
| prosječan broj vukova | 71–79 (76) | 67–80 (75) | 77–87 (82) |
| prosječan broj parcela s travom | 920–982 (953) | 912–1025 (963) | 921–992 (963) |
| najviše ovaca | 204–282 (237) | 208–255 (226) | 199–281 (237) |
| najviše vukova | 98–121 (109) | 95–125 (111) | 109–143 (120) |
| vukovi kasne za ovcama (tickova) | 38–90 (56) | 36–89 (54) | 27–66 (48) |
| vukovi izumrli do ticka 500 | 0 od 20 | 0 od 20 | 0 od 20 |

Brojke po pokretanju nisu iste, jer NetLogo i C# imaju različite generatore slučajnih brojeva, ali
rasponi se poklapaju: model se ponaša isto. U oba jezika populacije osciliraju, a vrh broja vukova
dolazi u prosjeku oko 55 tickova poslije vrha broja ovaca. Kašnjenje je pomak s najvećom korelacijom
između broja ovaca i kasnijeg broja vukova.

Sinhrona varijanta daje ovcama više hrane, ali **ovaca nema više, nego vukova** (prosjek 82 umjesto
75). Višak hrane završi kod predatora. Promjena koja izgleda tehnička, način ažuriranja, promijeni
rezultat, i to ne tamo gdje bi se očekivalo. Zato se u radu navodi kako se agenti ažuriraju.

Ponavljanje provjere. NetLogo dio, iz foldera `provjera/`:

```
NetLogo_Console.exe --headless --model "<NetLogo>/models/Sample Models/Biology/Wolf Sheep Predation.nlogox"
    --setup-file eksperiment-netlogo.xml --experiment ws-trava --table rezultati-netlogo.csv
```

C# dio: `dotnet run -- eksperiment` (i još jednom sa `--sinhrono`), pa poređenje:
`python provjera/uporedi.py provjera/rezultati-netlogo.csv rezultati/eksperiment-csharp.csv`.
Rezultati iz tabele su u `provjera/` (`rezultati-*.csv`, `poredjenje.txt`).

## Blokovi interakcije (vježbe 3)

Šest malih modela iz `../../modeli/` (`v03-blok1-povjerenje.nlogox` … `v03-blok6-kazna.nlogox`),
prevedena linija uz liniju; NetLogo linija je u komentaru desno od C# linije.

| Fajl | Blok | Pravilo |
|---|---|---|
| `Blokovi/Blok1Povjerenje.cs` | ograničeno povjerenje | razgovor mijenja stav oba sagovornika samo ako se stavovi razlikuju manje od `prag`; isto vrijedi za poruku medija |
| `Blokovi/Blok2Prag.cs` | prag i kaskada | u sali (svijet bez omotavanja) čovjek ustane kad je udio susjeda koji stoje barem njegov prag |
| `Blokovi/Blok3Mreza.cs` | mreža poznanstava | ljudi stoje i razgovaraju samo s poznanicima (links); dio veza vodi daleko |
| `Blokovi/Blok4Preseljenje.cs` | preseljenje | ko među susjedima ima manje sličnih od traženog udjela, preseli se na prazno mjesto |
| `Blokovi/Blok5Ustanova.cs` | mjesto s iskustvom | ko stane na patch ustanove, dobije loše iskustvo s vjerovatnoćom `udio-losih-iskustava` (povjerenje ide prema 0) ili dobro (prema 1); `UstanovaPatch : Patch` je `patches-own` |
| `Blokovi/Blok6Kazna.cs` | kontrola i kazna | čovjek prekrši pravilo s vjerovatnoćom `sklonost`; ako ga kontrola otkrije, sklonost padne, inače poraste |

`myself` je u C# obična varijabla iz vanjske lambde (closure). U bloku 1 to je čovjek koji razgovara,
dok je unutar `World.Ask(new[] { sagovornik }, s => ...)` `this` sagovornik `s`. U blokovima 3 i 4 to
je čovjek čiji se poznanici ili susjedi biraju.

`dotnet run -- blokovi` za svaki blok pokrene mali eksperiment (nekoliko vrijednosti jednog
parametra, 10 ili 20 pokretanja po vrijednosti) i ispiše tabelu; `--blok 2` pokreće samo jedan blok.
Rezultati su u `rezultati/blok1-csharp.csv` … `blok6-csharp.csv`, a ispis pokretanja blokova 1–4
(oko 100 s) u `provjera/blokovi-csharp.txt`. Poređenje s NetLogo mjerenjima za blokove 1–4 je u
`provjera/blokovi-poredjenje.md`: rasponi i sredine se poklapaju u sva četiri bloka.

## Šta nije napravljeno

- grafika, interfejs, plotovi;
- usmjerene veze (`create-link-to`) i oblici veza;
- u svijetu bez omotavanja `Forward` ne zaustavlja turtle na ivici kao NetLogo; blok 2 to ne
  koristi, jer ljudi u sali ne šetaju;
- verzija modela bez trave, labele, `user-message`;
- `[ x ] of skup` u NetLogo vraća listu slučajnim redom; `Select` čuva redoslijed.

Svijet drži spisak turtles po parceli (kao NetLogo), poredan po `who`, pa `TurtlesHere` ne pretražuje
cijeli svijet. Wolf Sheep daje isti CSV kao prije te izmjene.

## Izvor i licenca

Model je prijevod originala: Wilensky, U. (1997). *NetLogo Wolf Sheep Predation model*.
http://ccl.northwestern.edu/netlogo/models/WolfSheepPredation. Center for Connected Learning and
Computer-Based Modeling, Northwestern University, Evanston, IL. U NetLogo: File → Models Library →
Sample Models → Biology → Wolf Sheep Predation. Original je pod licencom CC BY-NC-SA 3.0, pa je i
ovaj prijevod pod istom licencom.
