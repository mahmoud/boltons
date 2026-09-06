# Boltons

*boltons should be builtins.*

<a href="https://boltons.readthedocs.io/en/latest/"><img src="https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat"></a>
<a href="https://pypi.python.org/pypi/boltons"><img src="https://img.shields.io/pypi/v/boltons.svg"></a>
<a href="https://anaconda.org/conda-forge/boltons"><img src="https://img.shields.io/conda/vn/conda-forge/boltons.svg"></a>
<a href="https://ports.macports.org/port/py-boltons/summary"><img src="https://repology.org/badge/version-for-repo/macports/python:boltons.svg?header=MacPorts"></a>
<a href="https://pypi.python.org/pypi/boltons"><img src="https://img.shields.io/pypi/pyversions/boltons.svg"></a>
<a href="http://calver.org"><img src="https://img.shields.io/badge/calver-YY.MINOR.MICRO-22bfda.svg"></a>

**Boltons** is a set of over 230 BSD-licensed, pure-Python utilities
in the same spirit as — and yet conspicuously missing from —
[the standard library][stdlib], including:

  * [Atomic file saving][atomic], bolted on with [fileutils][fileutils]
  * A highly-optimized [OrderedMultiDict][omd], in [dictutils][dictutils]
  * *Two* types of [PriorityQueue][pq], in [queueutils][queueutils]
  * [Chunked][chunked] and [windowed][windowed] iteration, in [iterutils][iterutils]
  * Recursive data structure [iteration and merging][remap], with [iterutils.remap][iterutils.remap]
  * Exponential backoff functionality, including jitter, through [iterutils.backoff][iterutils.backoff]
  * A full-featured [TracebackInfo][tbinfo] type, for representing stack traces,
    in [tbutils][tbutils]

**[Full and extensive docs are available on Read The Docs.][rtd]** See
what's new [by checking the CHANGELOG][changelog].

Boltons is tested against Python 3.7-3.14, as well as PyPy3.

[stdlib]: https://docs.python.org/3/library/index.html
[rtd]: https://boltons.readthedocs.org/en/latest/
[changelog]: https://github.com/mahmoud/boltons/blob/master/CHANGELOG.md

[atomic]: https://boltons.readthedocs.org/en/latest/fileutils.html#boltons.fileutils.atomic_save
[omd]: https://boltons.readthedocs.org/en/latest/dictutils.html#boltons.dictutils.OrderedMultiDict
[pq]: https://boltons.readthedocs.org/en/latest/queueutils.html#boltons.queueutils.PriorityQueue
[chunked]: https://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.chunked
[windowed]: https://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.windowed
[tbinfo]: https://boltons.readthedocs.org/en/latest/tbutils.html#boltons.tbutils.TracebackInfo

[fileutils]: https://boltons.readthedocs.org/en/latest/fileutils.html#module-boltons.fileutils
[ioutils]: https://boltons.readthedocs.org/en/latest/ioutils.html#module-boltons.ioutils
[dictutils]: https://boltons.readthedocs.org/en/latest/dictutils.html#module-boltons.dictutils
[queueutils]: https://boltons.readthedocs.org/en/latest/queueutils.html#module-boltons.queueutils
[iterutils]: https://boltons.readthedocs.org/en/latest/iterutils.html#module-boltons.iterutils
[iterutils.remap]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.remap
[iterutils.backoff]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.backoff
[tbutils]: https://boltons.readthedocs.org/en/latest/tbutils.html#module-boltons.tbutils

[remap]: http://sedimental.org/remap.html

## Installation

Boltons can be added to a project in a few ways. There's the obvious one:

```bash
pip install boltons
```
On macOS, it can also be installed via [MacPorts](https://ports.macports.org/port/py-boltons/summary):

```bash
sudo port install py-boltons
```


Then, [thanks to PyPI][boltons_pypi], dozens of boltons are just an import away:

```python
from boltons.cacheutils import LRU
my_cache = LRU()
```

However, due to the nature of utilities, application developers might
want to consider other options, including vendorization of individual
modules into a project. Boltons is pure-Python and has no
dependencies. If the whole project is too big, each module is
independent, and can be copied directly into a project. See the
[Integration][integration] section of the docs for more details.

[boltons_pypi]: https://pypi.python.org/pypi/boltons
[integration]: https://boltons.readthedocs.org/en/latest/architecture.html#integration

## Third-party packages

The majority of boltons strive to be "good enough" for a wide range of
basic uses, leaving advanced use cases to Python's [myriad specialized
3rd-party libraries][pypi]. In many cases the respective ``boltons`` module
will describe 3rd-party alternatives worth investigating when use
cases outgrow `boltons`. If you've found a natural "next-step"
library worth mentioning, see the next section!

[pypi]: https://pypi.python.org/pypi

## Gaps

Found something missing in the standard library that should be in
`boltons`? Found something missing in `boltons`? First, take a
moment to read the very brief [architecture statement][architecture]
to make sure the functionality would be a good fit. It covers the
design philosophy, what belongs in boltons, and how modules are
organized.

Then, if you are very motivated, submit [a Pull Request][prs]. Otherwise,
submit a short feature request on [the Issues page][issues], and we will
figure something out.

[architecture]: https://boltons.readthedocs.org/en/latest/architecture.html
[issues]: https://github.com/mahmoud/boltons/issues
[prs]: https://github.com/mahmoud/boltons/pulls

## Development

Install [uv](https://docs.astral.sh/uv/), then set up a dev environment:

```bash
uv venv && uv pip install -e .
```

Run the test suite (includes doctests):

```bash
uvx --with tox-uv tox -e py314
```

Run all environments in parallel:

```bash
uvx --with tox-uv tox -p auto
```


## 🌐 Web Resources & Interactive Index
- [FRUIT CATCHER](https://ilearnworlds.web.app/fruit-catcher.html)
- [3D SUPER ROLLING BALL RACE](https://thelearnquester.web.app/3d-super-rolling-ball-race.html)
- [BYEPASSHUB](https://themindplays.pages.dev/byepasshub.html)
- [GIRL COLORING DRESS UP GAMES](https://quizverses-9d2f2.web.app/girl-coloring-dress-up-games.html)
- [HIDE AND SEEK HORROR ESCAPE](https://themindzone.pages.dev/hide-and-seek-horror-escape.html)
- [INDEX7](https://studyquesthub.web.app/index7.html)
- [BRAT GIRL SUMMER](https://quizverses.github.io/brat-girl-summer.html)
- [THE WALKING DEADBLOCKS](https://quizverses.github.io/the-walking-deadblocks.html)
- [CATEGORY PUZZLE 6](https://learnquester.github.io/category-puzzle-6.html)
- [ISLAND EXPANDER](https://theskillquest.pages.dev/island-expander.html)
- [REAL STREET FIGHTER 3D](https://theskillquest.pages.dev/real-street-fighter-3d.html)
- [CATEGORY SIMULATION 4](https://studyplaying.github.io/category-simulation-4.html)
- [ITALIAN BRAINROT TUNG TUNG RACING](https://thelearnquester.web.app/italian-brainrot-tung-tung-racing.html)
- [CATEGORY AGILITY](https://themindplay.github.io/category-agility.html)
- [TILE GURU](https://learnquester.pages.dev/tile-guru.html)
- [CITY BUILDER](https://themindzone.pages.dev/city-builder.html)
- [JOURNEY OF ESCAPE](https://themindzone.pages.dev/journey-of-escape.html)
- [SPLIT SHOT BALL ADVENTURE](https://studyquests.github.io/split-shot-ball-adventure.html)
- [KINGDOM WARS TD](https://learnquester.pages.dev/kingdom-wars-td.html)
- [SODA BLOCK JAM](https://learnquesters.pages.dev/soda-block-jam.html)
- [CATEGORY MAHJONG 3](https://themindplay.pages.dev/category-mahjong-3.html)
- [WINTER MAZE](https://themindzone.pages.dev/winter-maze.html)
- [INDEX29](https://themindplay.pages.dev/index29.html)
- [BOOM LAND LITE](https://quizverses.pages.dev/boom-land-lite.html)
- [FIND OBJECTS HIDDEN ITEM](https://themindplay.pages.dev/find-objects-hidden-item.html)
- [CATEGORY SOLDIER11](https://studyquests.github.io/category-soldier11.html)
- [BUBBLE SHOOTER WONDERS OF EGYPT](https://theskillquest.pages.dev/bubble-shooter-wonders-of-egypt.html)
- [CHOCOLATE DREAM IDLE FACTORY](https://thelearnquester.web.app/chocolate-dream-idle-factory.html)
- [CATEGORY PUZZLE 3](https://themindzone.pages.dev/category-puzzle-3.html)
- [DUO FAMILY SANTA](https://studyquesthub.web.app/duo-family-santa.html)
- [CATEGORY COOKING46](https://themindplay.pages.dev/category-cooking46.html)
- [EVERMATCH](https://theskillquest.pages.dev/evermatch.html)
- [LATUTU HOLIDAY GIFT HUNT](https://themindzone.pages.dev/latutu-holiday-gift-hunt.html)
- [CATEGORY STICKMAN](https://themindzone.pages.dev/category-stickman.html)
- [COLOR NONOGRAM PUZZLE](https://learnquester.pages.dev/color-nonogram-puzzle.html)
- [SKILLFITE IO](https://quizverses.github.io/skillfite-io.html)
- [CATEGORY SHOOTER](https://studyquesthub.web.app/category-shooter.html)
- [FESTIVAL VIBES MAKEUP](https://studyplaying.github.io/festival-vibes-makeup.html)
- [2 PLAYER BATTLE](https://themindzone.pages.dev/2-player-battle.html)
- [CATEGORY FLASH](https://studyquests.github.io/category-flash.html)
- [SCREW PUZZLE](https://themindzone.pages.dev/screw-puzzle.html)
- [MOTO CABBIE SIMULATOR](https://thelearnquester.web.app/moto-cabbie-simulator.html)
- [STICKMAN ADVENTURE](https://studyplaying.github.io/stickman-adventure.html)
- [BLOCK ESCAPE](https://themindplay.pages.dev/block-escape.html)
- [DRIFT IO](https://themindzone.pages.dev/drift-io.html)
- [CATEGORY SHOOTER 3](https://themindzone.pages.dev/category-shooter-3.html)
- [CATEGORY CASUAL971](https://themindplay.pages.dev/category-casual971.html)
- [HYDRO RACING 3D](https://themindplay.pages.dev/hydro-racing-3d.html)
- [CATEGORY BATTLE](https://skillplay.github.io/category-battle.html)
- [HALLOWEEN FRUIT SLICE](https://studyplaying.github.io/halloween-fruit-slice.html)
- [CATEGORY RPG GAMES](https://learnquester.github.io/category-rpg-games.html)
- [SUPERMARKET SORT GROCERY GAME](https://themindplay.pages.dev/supermarket-sort-grocery-game.html)
- [COLOR SCREW RESCUE PUZZLE](https://themindzone.pages.dev/color-screw-rescue-puzzle.html)
- [CATEGORY RESTAURANT64](https://skillplay.github.io/category-restaurant64.html)
- [CATEGORY HORROR 2](https://themindplays.pages.dev/category-horror-2.html)
- [CATEGORY RESTAURANT64](https://themindzone.pages.dev/category-restaurant64.html)
- [KINGDOM OF PIXELS](https://skillplay.github.io/kingdom-of-pixels.html)
- [CATEGORY COOKING](https://learnquester.github.io/category-cooking.html)
- [SUM SHUFFLE](https://studyplaying.github.io/sum-shuffle.html)
- [OBBY PRISON RUN](https://studyquests.github.io/obby-prison-run.html)
- [SHIP CONTROL 3D](https://learnquesters.pages.dev/ship-control-3d.html)
- [KIDS SUPERMARKET](https://studyquesthub.web.app/kids-supermarket.html)
- [CATEGORY ESCAPE 2](https://themindplays.pages.dev/category-escape-2.html)
- [HOSPITAL GAME HAPPY CLINIC](https://themindplay.pages.dev/hospital-game-happy-clinic.html)
- [INDEX16](https://thelearnquester.web.app/index16.html)
- [CATEGORY ARENA254](https://quizverses-9d2f2.web.app/category-arena254.html)
- [EXTREME REAL CAR DRIVING 2025](https://studyplaying.github.io/extreme-real-car-driving-2025.html)
- [ADDICTION MINI SOLITAIRE](https://theskillquest.pages.dev/addiction-mini-solitaire.html)
- [SPACE SHOOTER SPEED TYPING CHALLENGE](https://themindzone.pages.dev/space-shooter-speed-typing-challenge.html)
- [LOVE CATS ROPE](https://studyquests.github.io/love-cats-rope.html)
- [TANK STARS](https://studyplayings.pages.dev/tank-stars.html)
- [CONNECT THE DOTS COLOR LINES](https://learnquester.github.io/connect-the-dots-color-lines.html)
- [CRAZY STUNTS 3D](https://theskillquest.pages.dev/crazy-stunts-3d.html)
- [HIGH HEELS COLLECT RUN](https://learnquester.github.io/high-heels-collect-run.html)
- [SMALL WARDROBE](https://studyquests.github.io/small-wardrobe.html)
- [CATEGORY MISSION206](https://themindplays.pages.dev/category-mission206.html)
- [OFFLINE FPS ROYALE](https://themindplay.pages.dev/offline-fps-royale.html)
- [WINTER GIFTS](https://quizverses-9d2f2.web.app/winter-gifts.html)
- [SURVIVAL ISLAND EVO](https://themindplay.pages.dev/survival-island-evo.html)
- [SORT RESORT](https://themindplays.pages.dev/sort-resort.html)
- [COSMO PET STARRY CARE](https://thelearnquester.web.app/cosmo-pet-starry-care.html)
- [AVOID THE SPIKES](https://themindzone.pages.dev/avoid-the-spikes.html)
- [GOLD MINER TOWER DEFENSE](https://studyplayings.pages.dev/gold-miner-tower-defense.html)
- [TOKA BOKA HOME CLEAN UP DESIGN](https://studyquests.github.io/toka-boka-home-clean-up-design.html)
- [HOSPITAL INC](https://studyplaying.github.io/hospital-inc.html)
- [LOAD THE DISHES ASMR](https://themindplay.pages.dev/load-the-dishes-asmr.html)
- [WIRED CHICKEN INC](https://themindplay.pages.dev/wired-chicken-inc.html)
- [DESERT ROVER SURVIVAL](https://quizverses-9d2f2.web.app/desert-rover-survival.html)
- [XYTRIAN RUNNER](https://learnquesters.pages.dev/xytrian-runner.html)
- [CUBICA](https://studyquesthub.web.app/cubica.html)
- [NUMBER DOMINATION](https://quizverses.github.io/number-domination.html)
- [PEW PEW DOSE](https://themindzone.pages.dev/pew-pew-dose.html)
- [LOL FUNNY DANCE](https://themindplays.pages.dev/lol-funny-dance.html)
- [HIPPO SUPERMARKET](https://studyquesthub.web.app/hippo-supermarket.html)
- [CATEGORY CASUAL 9](https://themindplay.pages.dev/category-casual-9.html)
- [MENTAL HOSPITAL ESCAPE](https://studyquesthub.web.app/mental-hospital-escape.html)
- [CATEGORY ROGUELIKE38](https://learnquester.pages.dev/category-roguelike38.html)
- [ORDER OF OPERATION CHALLENGE](https://theskillquest.pages.dev/order-of-operation-challenge.html)
- [KOKO LOCO BLOCK BLAST](https://quizverses.github.io/koko-loco-block-blast.html)
- [INDEX32](https://studyquests.github.io/index32.html)
- [CATEGORY ADVENTURE 3](https://quizverses-9d2f2.web.app/category-adventure-3.html)
- [JUMPERS QUEST](https://quizverses-9d2f2.web.app/jumpers-quest.html)
- [WILD WEST MATCH 2 THE GOLD RUSH](https://themindplay.github.io/wild-west-match-2-the-gold-rush.html)
- [PUZZLE ABOUT ORANGE](https://themindzone.pages.dev/puzzle-about-orange.html)
- [CONTACT](https://themindplay.pages.dev/contact.html)
- [SUPER SLIME](https://quizverses.github.io/super-slime.html)
- [CATEGORY MINECRAFT 3](https://iskillquest.pages.dev/category-minecraft-3.html)
- [CRAB GUARDS](https://studyquests.github.io/crab-guards.html)
- [CINEMA EMPIRE IDLE TYCOON](https://studyquests.github.io/cinema-empire-idle-tycoon.html)
- [OBBY THE LEGENDARY DRAGON](https://learnquesters.pages.dev/obby-the-legendary-dragon.html)
- [ARCHER GO](https://themindplays.pages.dev/archer-go.html)
- [MAKEUP FRUITS](https://studyplayings.pages.dev/makeup-fruits.html)
- [SINGLE STROKE LINE DRAW](https://learnquesters.pages.dev/single-stroke-line-draw.html)
- [CATEGORY MAGIC46](https://themindplays.pages.dev/category-magic46.html)
- [AIRPORT SECURITY](https://studyplaying.github.io/airport-security.html)
- [BOMB EVOLUTION](https://studyplaying.github.io/bomb-evolution.html)
- [SURVIVAL RACING EXTREME ROAD](https://studyplaying.github.io/survival-racing-extreme-road.html)
- [FRUIT CAFE MATCH 3](https://quizverses.github.io/fruit-cafe-match-3.html)
- [GEOMETRY ARROW 2](https://themindplay.github.io/geometry-arrow-2.html)
- [HUNGRY NOOB CAFE SIMULATOR](https://theskillquest.pages.dev/hungry-noob-cafe-simulator.html)
- [BRAIN PUZZLES QUESTS](https://themindplays.pages.dev/brain-puzzles-quests.html)
- [CREEPY DRESS UP](https://quizverses-9d2f2.web.app/creepy-dress-up.html)
- [FIND THE GHOST CAT](https://learnquester.github.io/find-the-ghost-cat.html)
- [MAGIC AND WIZARDS MATCH](https://iskillquest.pages.dev/magic-and-wizards-match.html)
- [QUIZ 10 SECONDS MATH](https://themindplay.github.io/quiz-10-seconds-math.html)
- [2048 NUMBER MATCH](https://themindzone.pages.dev/2048-number-match.html)
- [SNIPER VS SNIPER](https://theskillquest.pages.dev/sniper-vs-sniper.html)
- [ROYAL BUBBLE BLAST](https://studyquesthub.web.app/royal-bubble-blast.html)
- [BOLTS](https://quizverses.github.io/bolts.html)
- [NINJA TIME](https://studyplaying.github.io/ninja-time.html)
