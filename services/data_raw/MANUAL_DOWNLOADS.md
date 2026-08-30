# Manual data downloads

Everything in `services/data_raw/` that the pipeline cannot fetch for itself. Two sources
are automated (`scrape.py` writes `eurostat/` and `e_control/`, both git-ignored); every
other directory here is a hand-made drop, **tracked in git because git is the only backup
it has**.

This file is the instruction sheet for refreshing them. It is written to be read a year
after the last refresh, by someone who no longer remembers the click path — so where the
path is not known precisely it says so rather than inventing one. Fill a section in the
moment you next walk it.

## The three rules that apply to every drop

**1. The filename decides which file is live, never a literal in Python.** Each reader
globs its directory and takes the newest dated match. So:

- Drop the new file *next to* the old one. Do not overwrite, do not delete.
- Keep the naming pattern the section below states. A file that does not match its
  pattern is not an error — it is invisible, which is worse. Where a section says the
  pattern already accepts the portal's own filename, save it exactly as downloaded:
  renaming by hand is the step that eventually gets skipped.
- The year in the name is the **export/publication year**, not the last year of data.
  `eea_Austria_2025.xlsx` carries data through 2024.

**2. Which years exist is read off the file, never hardcoded.** If a refresh adds a year
and the charts do not move, that is the bug — not a quiet success.

**3. Every drop is followed by the same three commands**, from `services/`:

```bash
poetry run python pipeline.py         # rebuild all 89 charts
poetry run python check_contract.py   # manifest / data / locales consistent
cd .. && npm run test:smoke           # 12 routes x 2 locales, in a real browser
```

Then diff `src/locales/_seed/` against `src/locales/{de,en}/` and copy over any new keys.
A green typecheck is not a passing test, and neither is a pipeline that exits 0.

---

## EEA — Greenhouse gases data viewer

*Written from a refresh actually performed (2026-08-26).*

| | |
|---|---|
| **Feeds** | every "GHG emissions by sub-sectors" chart, the LULUCF page, the long-term carbon storage chart |
| **Read by** | `sources/eea.py` |
| **Goes to** | `data_raw/eea/eea_Austria_<year>.xlsx` |
| **Source** | https://www.eea.europa.eu/en/analysis/maps-and-charts/greenhouse-gases-viewer-data-viewers |
| **Cadence** | annual, roughly mid-year, when the EU inventory submission is published |

**Steps**

1. Open the data viewer at the link above and enter the greenhouse-gas viewer.
2. Filter to: country **Austria**, gas **All greenhouse gases - (CO2 equivalent)**,
   **all sectors** (the full CRF tree, not a top-level selection — the sub-sector codes
   are the whole point), **all years**.
3. Export the result as `.xlsx`.
4. Save it as `data_raw/eea/eea_Austria_<publication year>.xlsx`, alongside the previous
   exports. **Check the spelling of the prefix**: the 2025 export was first saved here as
   `eaa_…`, which matches nothing and would have left the pipeline reading the 2024 file
   with no complaint.

**What the reader needs to find in the file**

- Columns `Sector Name`, `Gas`, `Country`, `Jahr von Date`, `t CO2 equivalent`. Extra
  columns are ignored (the 2024 export also carried a `t` column; the 2025 one does not).
- Sector, gas and country blank on continuation rows — the reader forward-fills them.
  If a future export repeats the value on every row instead, the fill is harmless.
- Every CRF code listed in `SECTORS` in `sources/eea.py` must be present. That map is
  matched by literal string, so an upstream relabelling of a sector name is the failure
  mode to watch for, and it shows up as a sub-sector reading zero rather than as an error.

**Two things that changed with the 2025 export, and what they cost**

- The prefix went from `unfcc_` to `eea_`, and the module and directory were renamed from
  `unfcc` to `eea` with it. Both prefixes are still matched, so the two exports already on
  disk under the old name take part in the newest-year comparison.
- The inventory **caught up with the Umweltbundesamt Klimadashboard**: both now end in
  2024. `sources/eea.py` had encoded "UBA runs exactly one year ahead" as a `[:-1]` slice;
  it aligns on the year now. If the gap reopens, the sub-sectors are carried forward at
  their last known share, as before, and the chart note says so.

**Related but separate:** the Klimadashboard export below is the *anchor* this breakdown is
scaled to. Refreshing one without the other leaves the difference sitting in the "Other"
residual of every sector chart, which looks like data rather than like a mistake.

---

## Umweltbundesamt — Klimadashboard sectoral totals

| | |
|---|---|
| **Feeds** | the national emissions charts, and the total line every sub-sector stack is scaled to |
| **Read by** | `sources/umweltbundesamt.py` |
| **Goes to** | `data_raw/umweltbundesamt/Mio. t CO₂-Äquivalent nach Jahr und Sektor.xlsx` |
| **Source** | https://www.umweltbundesamt.at/klima/dashboard |
| **Cadence** | annual |

The one filename here that is **fixed, not dated** — the reader names it literally,
including the `₂` subscript and the umlaut, so overwriting in place is the intended
refresh. Keep the encoding of the name intact when saving.

*Not yet written down:* which dashboard view exports this table, and whether the
"nach Jahr und Sektor" pivot has to be chosen explicitly. Record it on the next refresh.
What the reader needs is: a `Jahr` column, a `Sektor` column carrying the six German sector
names listed in `SECTORS` in that module, and a `Summe von Mio. t CO₂-Äquivalent` value
column, with two header rows above the table (`skiprows=2`) and a comma decimal separator.

---

## Statistik Austria — vehicles

*Written from a refresh actually performed (2026-08-26).*

| | |
|---|---|
| **Feeds** | the Transport page: new registrations by fuel, the fleet stock, and the BEV brand charts |
| **Read by** | `sources/vehicles.py`; `charts/car_brands.py` reuses its `registration_workbooks()` |
| **Goes to** | `data_raw/statistik_austria/Fahrzeuge/` |
| **Source** | new registrations: https://www.statistik.at/statistiken/tourismus-und-verkehr/fahrzeuge/kfz-neuzulassungen |
| | fleet stock: https://www.statistik.at/statistiken/tourismus-und-verkehr/fahrzeuge/kfz-bestand |
| **Cadence** | monthly for the registrations workbook, annual for the stock yearbook |

**Steps**

1. From the *Kfz-Neuzulassungen* page, take the cumulative workbook for the current year —
   "Kfz-Neuzulassungen Jänner bis `<Monat>` `<Jahr>`". It contains every month of that year
   up to its own, one sheet per month, so only the newest file of a year matters.
2. From the *Kfz-Bestand* page, take the yearbook whose `tab_2` is the long
   "Kfz-Bestand seit 1960" table.
3. Save both under their download names into `Fahrzeuge/`, **next to the existing files**.
4. Replace the current year's registrations workbook as its month range grows; keep exactly
   one file per completed year.

**The names the readers match**

| Pattern | What it is |
|---|---|
| `NeuzulassungenFahrzeugeJaennerBis<Monat><Jahr>` | new registrations, cumulative January to `<Monat>` |
| `kfz-bestand_<Jahr>` | the stock yearbook; `tab_2` carries the years eurostat does not, and any complete year it has beyond eurostat |
| `BestandFahrzeuge<Monat><Jahr>VorlaeufigeDaten` | preliminary monthly stock — optional, and the only thing that carries the fleet past the newest complete year |

Each accepts an optional export prefix (`DE2__…`) and either `.xlsx` or `.ods`. **Do not
rename the download to match the old files.** The patterns were widened to take the portal's
name as it comes; renaming by hand is the step that eventually gets skipped.

**Three things the 2026 refresh changed at once, and what each cost**

- **`.xlsx` became `.ods`**, so `odfpy` is now a declared dependency next to `openpyxl`.
  pandas picks the engine off the extension, and the older files still need the old one.
- **The filename gained a `DE2__` prefix.** A file that does not match its pattern is not an
  error — it is invisible, and the charts simply stop moving.
- **The 2025 yearbook renumbered its columns and dropped four years.** It inserted a
  `Hybrid` column into `tab_2`, which pushed `Sonstige Pkw3` to `Sonstige Pkw4` — the
  footnote number is part of the column name, so a literal match raised. Columns are matched
  on the stem with the footnote digits stripped now. In the same edition the rows for
  **1996–1999 disappeared**; every earlier yearbook has them and nothing else does. Each
  year is therefore taken from the newest yearbook that still reports it, across every
  edition on disk — **which is why old yearbooks must never be deleted**, and why the
  reader raises, naming the years, if one goes missing from all of them.
Two consequences of the last one are worth knowing when reading the chart: hybrids are
broken out of "Sonstige" only from 2006, because that is as far back as the yearbook
separates them, and no yearbook has ever split plug-in hybrids out at all. The chart note
says both.

**The preliminary stock file is optional, and dated by its own heading.** Drop one and the
fleet chart gains a provisional newest point; drop none and it simply ends at the newest
complete year — nothing raises either way. Its month and year come from the sheet heading
("Vorläufiger Pkw-Bestand … **am 31.07.2026**"), not from the filename, because only the
heading says what the figures are a snapshot of; a filename that disagrees is logged, not
fatal. The fuel sheet is `Pkw_nach_Kraftstoff` in the 2026 exports and `Pkw` in older ones,
and whichever is present is used.

It reports full and plug-in hybrids as one figure, and so does the yearbook, so **plug-in
hybrids are counted as hybrids for every year those two supply** — the plug-in series drops
to zero there, and that is a change of decomposition, not of the world. The chart says so
twice: in its own note, and through the manifest's `preliminary` flag, which makes the
frontend append a shared "newest value is provisional" line and stop appending it by itself
once a final figure lands. Never write that caveat into the chart's own note text: there is
one note per chart per locale, so it would then be wrong in whichever case it was not
written for.

**The trap this source has already sprung:** Statistik Austria wrote car brands in title
case up to 2018, upper case from January 2025. Brands are matched case-insensitively now.
Assume any label-matched column here will change its spelling again. The BEV brand table is
also read *positionally* — eleven rows below the "Tabelle 7" header — so verify that block
after a format change; the top-ten brands legitimately churn from month to month, which
makes a genuinely misread block look like ordinary churn.

---

## Statistik Austria — heating systems survey

| | |
|---|---|
| **Feeds** | the Buildings page: installed heating systems, absolute and share |
| **Read by** | `sources/statistik_austria.py` |
| **Goes to** | `data_raw/statistik_austria/08Heizungen2003Bis2024NachBundeslaendernUndVerwendetemEnergietraeger.xlsx` |
| **Source** | https://www.statistik.at/statistiken — Mikrozensus, Energieeinsatz der Haushalte |
| **Cadence** | biennial |

The filename carries the year range and **the reader names it literally**, so a new survey
means editing `PATH` in that module as well as dropping the file. The workbook holds one
block per two-year survey starting in 2003; the reader derives the years from the block
count rather than from a hardcoded end year.

*Not yet written down:* the exact table number and the download path on statistik.at.

**Same survey, second table:** the air-conditioning drop below comes out of the same
Mikrozensus. Refreshing one is a good moment to look for the other.

---

## Statistik Austria — air conditioners in households

*Written from the first drop (2026-08-26).*

| | |
|---|---|
| **Feeds** | the Buildings page: air conditioners installed in Austrian households |
| **Read by** | `sources/statistik_austria.py`, `air_conditioners()` |
| **Goes to** | `data_raw/statistik_austria/<nn>SanierungsmassnahmenKlimaanlagen<von><bis>.ods` |
| **Source** | https://www.statistik.at/statistiken — Mikrozensus, Energieeinsatz der Haushalte |
| **Cadence** | biennial, published with the heating survey above |

The same Mikrozensus as the heating survey, in a separate table. The workbook is a stack of
blocks, one per survey wave, and each block is a **renovation** cross-tabulation
(Heizkesseltausch / Wärmedämmung / Fenstertausch) whose last row is the figure this project
wants. Only that row is read; the renovation table itself feeds nothing, and is a candidate
for a chart of its own if anyone wants one.

**This name is matched by pattern**, unlike the heating file above it: an optional export
prefix (`DE2__`), an optional leading table number, `SanierungsmassnahmenKlimaanlagen`, the
two years of the span, and either extension. **Save it exactly as downloaded, next to the
existing one** — do not overwrite and do not rename.

**Old editions are never deleted.** Every matching workbook is walked newest-first and each
wave is taken from the first edition that still reports it, so an export that starts later
than its predecessor drops no wave from the chart. That is the vehicles yearbook trap, which
this file would spring the same way.

**What the reader needs to find in the file**

- One title line per block, starting `Sanierungsmaßnahmen und Anzahl der Klimaanlagen`, with
  the collection window spelled out in prose: `… – Juli 2023 bis Juni 2024`. **The last year
  in that line is the year the point is dated to.** It is not derived from a cadence, because
  there is none: the three waves on disk cover two years, two years, then one, and nothing
  covers July 2022 to June 2023.
- A header row carrying `Wohnungsanzahl`, with `Variationskoeffizient in Prozent (%)` in the
  column to its right. Both are matched with the footnote digits stripped off the stem, and
  the column is located per block — the blocks already on disk do not have equal row counts.
- A row labelled exactly `Anzahl Klimaanlagen in Haushalten`. If that label is reworded
  upstream the reader raises and names the file, rather than shipping an empty chart.
- `-` in place of a figure means the survey suppressed it (coefficient of variation above
  33 %). It reads as a gap, never as a zero.

The coefficient of variation travels with the value and becomes the chart's error bars.
These are sample estimates rather than a count of installed units, and the band is the only
thing on the chart that says so.

---

## StatCube — meat and milk consumption

| | |
|---|---|
| **Feeds** | the Food page |
| **Read by** | `sources/statcube.py` |
| **Goes to** | `data_raw/statistik_austria/` |
| **Source** | StatCube, the Statistik Austria data cube (Versorgungsbilanzen / food balances) |
| **Cadence** | annual |

Two CSV exports, matched by prefix, newest-wins on the ISO date StatCube writes into the
filename:

- `meat_consumption_StatCube_table_<date>.csv`
- `milk-consumption_StatCube_table_<date>.csv`

Keep the prefixes exactly as written — note that one uses `-` and the other `_` before
`consumption`; that is how the existing files are named, and the prefix is what is matched.
The reader needs the German product names listed in `MEAT_TYPES` / `MILK_TYPES` and a
`Werte` measure.

*Not yet written down:* the StatCube table id and the selection saved for the export.

---

## Statistik Austria — provisional energy balance

| | |
|---|---|
| **Feeds** | the newest year of the energy-balance charts, appended ahead of eurostat |
| **Read by** | `charts/energy_balance.py` (`_preliminary_file`) |
| **Goes to** | `data_raw/statistik_austria/vorlaeufigeEnergiebilanzenOesterreich<Jahr>inTerajoule*.xlsx` |
| **Source** | https://www.statistik.at/statistiken — Energiebilanzen, vorläufige Werte |
| **Cadence** | annual, published well before eurostat's `nrg_bal_c` catches up |

Matched by regex on the leading part of the name, newest year wins; anything after
`inTerajoule` is ignored, which is why the `…DatenI(1).xlsx` currently on disk works.

---

## National Inventory Report — land-use tables

| | |
|---|---|
| **Feeds** | the LULUCF page's land-use area charts |
| **Extracted by** | `download/national_inventory.py` — hand-run, needs `pdftotext` on PATH |
| **Read by** | `sources/national_inventory.py` |
| **Goes to** | `data_raw/national_inventory_report/lulucf_<use>.txt` |
| **Source** | https://www.umweltbundesamt.at/studien-reports — Austria's National Inventory Report |
| **On disk** | `data_raw/national_inventory_report/national_inventory_report_2026.pdf` (~12 MB, git-ignored) |
| **Cadence** | annual, and in practice refreshed far less often |

The manual step is the PDF, and it is **the one manual drop here that git does not keep** —
`*.pdf` in that directory is ignored, because 12 MB of published report that stays
downloadable is not worth versioning when the six extracted grids are tracked. So a fresh
clone has the numbers but not the source document, and re-running the extractor means
fetching it again. Download the report by hand and drop it in, keeping the
`national_inventory_report_<year>.pdf` name, then run

```bash
python download/national_inventory.py
```

which rewrites the six `lulucf_<use>.txt` grids and prints the row counts and the area
check. It is deliberately not part of `scrape.py`: it needs a file that only a human can
have fetched, and it shells out to a binary that is not a Python dependency.

Six files are read — `forest_land`, `settlements`, `crop_land`, `grass_land`, `wet_land`,
`other`. The other 28 `.txt` files in that directory are the hand-transcribed remains of the
sub-sector reader that `sources/eea.py` replaced, and are kept only as history (see
`archive/national_inventory_sectors.py`).

**Forest land is in kHa and every other file in Ha.** That is a property of the report, and
a silent unit switch would rescale the chart by a factor of a thousand and still draw. The
extractor's guard against that is arithmetic rather than trust: the six uses are the whole
country, so it checks they sum to Austria's 8 387 900 ha ± 1 500 in every year — the
tolerance is the rounding of forest land to whole kHa, not slack. A mis-read row or a
dropped digit fails the same check.

**Use `pdftotext -table`, never `-layout`.** On the wetlands page the year cell and the data
cells of alternate rows sit on slightly different baselines, and `-layout` splits them: half
the years land on their own line and the matching rows come out unlabelled. Read
positionally that shifts wetlands by up to four years and still draws as a smooth curve.

**The report changes which years it prints.** Up to and including the 2024 edition the
tables ran annually from 1990; NIR 2026 gives 1990, 1995, 2000, 2005 and then every year
from 2010, and the intermediate years are nowhere in the report. Nothing downstream assumes
a regular axis any more, and the charts carry a note saying the early part is five-yearly.

**The 2026 edition also revised the areas back to 1990** (done 2026-08-29), so replacing the
files was all-or-nothing rather than an append: Other land moved a flat −63 317 ha into
Grassland in every year, settlements fell ~2–3 % and wetlands rose ~1–2 %. Forest land is
unchanged and cropland is unchanged through 2010. Splicing new years onto the old files
would have printed a 63 kha cliff at the join.

---

## Not currently read

Files that live here and feed nothing. Left in place deliberately, listed so a future reader
does not go looking for the chart they belong to:

- `data_raw/statistik_austria/Schieneninfrastruktur_2021_und_2022.xlsx` — the rail charts
  take their track lengths from eurostat `rail_if_line_tr` instead.
- `data_raw/other/AT_sold_heating_systems.xlsx`, `data_raw/other/AT_sold_heat_pumps.xlsx` —
  no reader.

---

## The two automated sources, for contrast

Neither belongs in this file's workflow, but knowing which is which is the point of it:

| Source | Command | Target |
|---|---|---|
| eurostat monthly/yearly tables | `poetry run python scrape.py` | `data_raw/eurostat/` (git-ignored) |
| E-Control MoMeGes electricity | `poetry run python scrape.py` | `data_raw/e_control/` (git-ignored) |
| eurostat full energy balance | `poetry run python -m download.energy_balance` | `data_raw/eurostat/energy_balances/` |

The energy balance sits between the two categories: it is scripted, but it walks roughly
eighty requests per year and eurostat publishes a new balance year about every eighteen
months, so it is run **by hand, about annually**, not from `scrape.py`.
