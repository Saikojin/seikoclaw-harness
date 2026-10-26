# From a passable demo to a store that closes sales

**An executive case study comparing unguided AI coding against the SeikoClaw Harness**

- **Live interactive comparison**: [https://saikojin.github.io/seikoclaw-harness/](https://saikojin.github.io/seikoclaw-harness/)
- **Control group (unguided AI)**: [Saikojin/RawExerMart](https://github.com/Saikojin/RawExerMart) ([live demo](https://saikojin.github.io/seikoclaw-harness/demos/rawexermart/index.html))
- **Treatment group (with SeikoClaw)**: [Saikojin/ClawExerMart](https://github.com/Saikojin/ClawExerMart) ([live demo](https://saikojin.github.io/seikoclaw-harness/demos/clawexermart/index.html) | [stress-test mode](https://saikojin.github.io/seikoclaw-harness/demos/clawexermart/index.html?data=worst))
- **Technical engineering report**: [EXERMART_CASE_STUDY.md](EXERMART_CASE_STUDY.md)

---

## The experiment

We gave two AI coding environments the exact same business assignment: build an online marketplace for buying and selling new and pre-owned gym equipment.

The first agent worked without guidance and produced **RawExerMart**. The second agent worked inside the **SeikoClaw** quality system and produced **ClawExerMart**.

At a glance, both projects compile, both pass their automated tests, and both put gym equipment on a web page. In a five-minute status meeting, they might look equally finished. Once you step into the shoes of a customer spending \$2,000 on a used power rack, the gap between a prototype and a real product becomes clear.

---

## 1. Unguided AI builds a brochure. Guided AI builds the business.

When an unguided AI builds an online store, it copies the most common pattern on the internet: a grid of photos, a price tag, and a filter bar. **RawExerMart** stops there. It gives you a catalog, a basic form to post an item, and a table comparing prices at other retailers.

Selling heavy, pre-owned gym gear in the real world requires solving three customer objections before anyone enters a credit card:

- **Mechanical trust.** A buyer paying \$1,800 for a used commercial treadmill wants proof that the motor and frame are sound. **ClawExerMart** builds a certified 8-point technician inspection report into every listing, grading frame welds, bearing spin, cable tension, and motor hours.
- **Physical fit.** Home gym buyers work with tight basement ceilings. **ClawExerMart** includes a room and ceiling clearance calculator. Enter an 8-foot basement ceiling, and the store warns you that a 90-inch power rack leaves zero inches of overhead clearance for pull-ups, while a rowing machine fits with 42 inches to spare.
- **Heavy logistics and trade-ins.** You cannot drop a 320-pound steel cage in a standard mailbox. **ClawExerMart** calculates palletized freight with residential liftgate delivery at checkout, and gives sellers an instant cash buyout calculator based on brand resale curves.

From the same starting prompt, the unguided agent delivered **3 basic screens**. The SeikoClaw agent delivered **6 complete customer journeys** that answer the actual reasons buyers hesitate.

---

## 2. Catching the \$129,999 bug that unit tests missed

In **RawExerMart**, 40 automated tests ran and passed. Every single test used clean, polite sample data: short product names, four-digit prices, and working image links.

Real inventory is messy. Sellers paste 20-word titles, upload broken photo links, and list \$129,999 commercial gym packages. SeikoClaw includes an automated stress test (`break-ui`) that feeds worst-case inventory into the store before launch.

That stress test uncovered **8 defects**, including a silent revenue killer. The catalog's price slider defaulted to a \$5,000 cap. When a commercial seller listed a \$24,995 Hammer Strength rig and a \$129,999 Eleiko facility package, the store hid both items from every visitor on the home page. Standard unit tests missed it because nobody tested a five-figure price. SeikoClaw caught the filter bug, fixed the ceiling logic so \$5,000+ displays all high-ticket inventory, and added a clean fallback screen when a seller's photo fails to load.

---

## 3. Looking at the real screen before calling the job done

The biggest hidden cost in AI-generated software is the false green light. **RawExerMart** reported 100% passing tests without ever opening a web browser. Its tests only checked text in memory.

When an agent never looks at the screen, visual defects slip straight to customers. On product cards, discount tags collided with inspection badges. On narrow columns, long city names pushed shipping prices off the card.

SeikoClaw refuses to mark a project complete until it opens a real Chrome browser, clicks through every customer workflow, and takes photographic proof of every screen. Those 7 verification captures sit right in the repository alongside the code.

---

## Executive scorecard

| Business question | Unguided AI (`RawExerMart`) | With SeikoClaw (`ClawExerMart`) | Why leadership cares |
| :--- | :--- | :--- | :--- |
| **How many customer workflows ship from one prompt?** | 3 basic screens | **6 complete buyer & seller workflows** | Cuts follow-up prompting and rework cycles in half |
| **What happens when a \$129,999 commercial order is listed?** | Untested against extreme inventory | **Stress-tested across 8 edge cases** | Prevents silent filter and checkout bugs on high-value items |
| **Did anyone verify the actual screen in a real browser?** | 0 browser runs (memory-only tests) | **7 automated Chrome visual sign-offs** | Eliminates "the tests passed, why is the layout broken?" |
| **Does it feel like a prototype or a commercial product?** | Generic template defaults | **Tactile controls & clear visual hierarchy** | Builds immediate buyer confidence on first click |

---

## Try the 60-second walkthrough

Open the [live split-screen comparison](https://saikojin.github.io/seikoclaw-harness/#live-sandbox) and try these three clicks:

1. **Click "Gym Space Matcher" in the right window (`ClawExerMart`).** Watch it flag which machines will hit an 8-foot basement ceiling. Notice that the left window (`RawExerMart`) has no way to check if equipment fits your room.
2. **Click "Sell / Trade-In" in both windows.** The left window gives you a blank text box asking you to guess your own price. The right window calculates your equipment's market resale value and offers an instant cash buyout on the spot.
3. **Click the yellow "Claw: Worst-Case Stress" button above the right window.** Watch the store absorb a 145-character product name, a broken image link, and a \$129,999 commercial package without a single overlapping button or broken layout.
