# Blokovi interakcije: NetLogo i C#

NetLogo 7.0.4 headless: `nastava/v03/modeli/mjerenja/rezultati.md` (24.10.2026.), osim gdje je
navedeno drugačije. C#: `dotnet run -- blokovi` (`blokovi-csharp.txt`), uz dodatna pokretanja u
`blokovi-csharp-blok2-200.txt` i `blokovi-csharp-blok3-100.txt`. Zadane vrijednosti klizača osim
navedenih. U zagradi je raspon (najmanje–najviše).

Pojedinačna pokretanja nisu ista, jer jezici imaju različite generatore slučajnih brojeva; porede
se rasponi i sredine.

## Blok 1: ograničeno povjerenje (10 pokretanja po pragu)

| prag | broj grupa, tick 500, bez medija: NetLogo | C# | udio „za“, tick 150, 4 kuće medija: NetLogo | C# |
|---|---|---|---|---|
| 0,1 | 6,4 (4–8) | 5,8 (4–8) | 0,398 (0,36–0,44) | 0,401 (0,31–0,47) |
| 0,2 | 4,2 (3–5) | 3,7 (3–4) | 0,386 (0,30–0,44) | 0,388 (0,27–0,48) |
| 0,3 | 2,8 (2–4) | 2,9 (2–3) | 0,379 (0,28–0,53) | 0,384 (0,27–0,49) |
| 0,5 | 1,7 (1–2) | 1,7 (1–2) | 0,400 (0,29–0,50) | 0,370 (0,17–0,50) |
| 1 | 1,0 | 1,0 | 0,895 (0,67–1,00) | 0,858 (0,66–0,99) |
| 2 | 1,0 | 1,0 | 0,902 (0,70–1,00) | 0,909 (0,71–1,00) |

## Blok 2: prag i kaskada (prosjek praga 0,3, 10 pokretača, 200 pokretanja po vrijednosti)

| rasipanje praga | talas (> 0,9 na kraju): NetLogo | C# | sredina udjela: NetLogo | C# | krugova, medijan: NetLogo | C# |
|---|---|---|---|---|---|---|
| 0 | 43 od 200 | 38 od 200 | 0,223 | 0,198 | 0 | 0 |
| 0,05 | 76 od 200; isti uslov u drugom mjerenju 92 od 200 | 85 od 200 | 0,387; 0,466 | 0,431 | 0 | 0 |
| 0,1 | 194 od 200 | 192 od 200 | 0,970 | 0,961 | 40,5 | 41 |
| 0,2 | 200 od 200 | 200 od 200 | 0,995 | 0,993 | 18 | 17 |

Uz 20 pokretanja C# je za rasipanje 0,05 dao 11 talasa od 20 (`blokovi-csharp.txt`); uz 200 je 85 od 200,
unutar razlike između dva NetLogo mjerenja istog uslova.

## Blok 3: mreža poznanstava (2 kuće medija)

Poznanika po osobi: NetLogo 3,70–3,73 (20 pokretanja), C# 3,74.

| daleke veze | udio „za“, tick 500, 20 pokretanja: NetLogo | C# | 100 pokretanja: NetLogo | C# |
|---|---|---|---|---|
| 0 | 0,431 (0,22–0,72) | 0,394 (0,22–0,67) | 0,448 | 0,455 |
| 0,05 | 0,538 (0,28–0,80) | 0,505 (0,21–0,87) | — | 0,506 |
| 0,2 | 0,708 (0,38–1,00) | 0,733 (0,42–0,99) | — | 0,728 |
| 1 | 0,915 (0,60–0,99) | 0,926 (0,51–0,99) | 0,930 | 0,922 |

Na ticku 150 uz `udio-dalekih-veza` = 1 dvadeset pokretanja dalo je NetLogo 0,447 i C# 0,562.
Uz 100 pokretanja je NetLogo 0,555, a C# 0,549. Rasipanje između pokretanja je veliko
(st. devijacija 0,21), pa 20 pokretanja nije dovoljno za taj uslov. NetLogo pokretanja sa 100
ponavljanja su posebna provjera (24.10.2026.), nisu u `rezultati.md`.

## Blok 4: preseljenje (gustina 0,7, 10 pokretanja)

| traženi udio sličnih | prosječno sličnih na kraju: NetLogo | C# | mjeseci do mirovanja, medijan: NetLogo | C# |
|---|---|---|---|---|
| 0,3 | 0,745 (0,72–0,77) | 0,744 (0,73–0,76) | 9,5 | 11 |
| 0,5 | 0,888 (0,88–0,90) | 0,887 (0,88–0,90) | 14 | 15 |
| 0,75 | 0,998 (0,997–0,999) | 0,998 (0,997–0,999) | 84 | 84 |

Na početku je u oba jezika prosječno sličnih oko 0,50.
