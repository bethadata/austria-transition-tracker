# -*- coding: utf-8 -*-
"""Chart manifest: the contract between the Python pipeline and the Vue frontend.

The pipeline emits structure and identity only - chart ids, series keys, unit
keys, source keys. Every piece of human-readable text lives in the frontend
locale files, keyed by those ids. That is why register() still takes the English
strings that used to be baked into the chart: it strips them out of the data and
routes them into a *seed* for src/locales/en/, which is generated once and then
owned by the frontend.

Two invariants worth knowing before changing anything here:

* Series order is the colour order, and that is a CVD-safety mechanism rather
  than a preference. "series" in the manifest is an ordered list; never sort it
  for display.
* null means no data. It is not zero. The old exporter mapped a gap and a real
  zero to the same 0, which in a stacked-area emissions chart silently
  understates a sector instead of breaking the line.
"""

import datetime
import json
import os
import re
import unicodedata

import numpy as np

from paths import PUBLIC_DATA, LOCALE_SEED
# Ids used to be derived from the Jekyll filenames: an "AT_timeseries_" prefix
# was stripped, the result lowercased, and four inherited typos
# ("sloughtered_pig_meat", "animal_feestock_population") were patched by a lookup
# table. All of that is gone -- the call sites pass the id they mean. The
# derivation was worth removing rather than keeping: an id is a locale key, a
# data filename and a manifest key at once, so a call site that cannot be
# grepped for its own chart's id is one rename away from a chart that renders
# blank.


def slugify(label):
    """English label -> stable key. Only ever used to seed the locale files."""
    s = str(label)
    s = s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
    s = s.replace("ß", "ss")
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("%", " pct ").replace("&", " and ")
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii").lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    s = re.sub(r"_+", "_", s)
    return s or "unknown"


def clean_text(text):
    """Strip the presentational markup the titles carry (b, sub, br)."""
    if text is None:
        return None
    s = re.sub(r"<br\s*/?>", " ", str(text))
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

# source_text is free prose today, mostly "provider (dataset code)". The code is
# worth keeping structured - it is the only machine-readable provenance the
# charts have - so it is split out and the provider becomes a locale key.
_SOURCE_KEYS = {
    "eurostat": "eurostat",
    "national_inventory_report": "nir",
    "umweltbundesamt": "uba",
    "statistik_austria": "statistik_austria",
    "statistics_austria": "statistik_austria",
    "statcube_statistik_austria": "statcube",
    "e_control": "e_control",
    "eea": "eea",
    "eea_greenhouse_gases_data_viewer": "eea",
    "eurostat_energy_balances": "eurostat_energy_balances",
    # Composite and free-prose providers. Slugifying these whole produced keys
    # up to 78 characters long; the key only has to be stable and unique, the
    # text the reader sees comes from the locale file either way.
    "eea_for_sectoral_uba_for_total_emissions": "eea_uba",
    "eurostat_and_statistik_austria": "eurostat_statistik_austria",
    "umweltbundesamt_eurostat_and_own_projection": "own_projection",
    "eurostat_and_own_estimation": "own_estimation",
    "eurostat_and_own_estimation_data_of_not_fully_available_years_are_projected":
        "own_estimation_projected",
    "eurostat_energy_balances_up_to_2015_e_control_from_2015_up_to_6_2026":
        "eurostat_econtrol_spliced",
}

# A dataset code, as opposed to prose in brackets. Every real code in this
# project is snake_case (nrg_bal_c, road_eqr_carpda, NRG_CB_GASM), so requiring
# an underscore is what keeps "(Klimadashboard)" from being read as one.
_CODE_RE = re.compile(r"\(([A-Za-z0-9]*_[A-Za-z0-9_]*(?:\s*,\s*[A-Za-z0-9_]+)*)\)")

_source_texts = {}


def _source(source_text):
    if not source_text:
        return None
    text = clean_text(source_text)
    # "Source: eurostat (nrg_bal_c)" -- the prefix is noise, and it made an
    # otherwise identical provider slug into a second, separate key.
    text = re.sub(r"^sources?\s*:\s*", "", text, flags=re.I)
    # The code is not always trailing: "eurostat (road_eqr_carpda) & Statistik
    # Austria" carries it in the middle, and slugifying around it produced one
    # key per dataset for what is one provider pair.
    code = None
    m = _CODE_RE.search(text)
    if m and len(m.group(1)) < 60:
        code = m.group(1).strip()
        text = (text[:m.start()] + text[m.end():])
    provider = re.sub(r"\s+", " ", text).strip(" ,&")
    # The key is derived from the text with every remaining parenthetical
    # dropped, so that "... & own projection (train years 2019-2024)" keeps one
    # stable key instead of minting a new one each time the training window
    # moves. The full text, years included, still goes to the locale seed.
    stem = re.sub(r"\s+", " ", re.sub(r"\([^()]*\)", "", provider)).strip(" ,&")
    key = _SOURCE_KEYS.get(slugify(stem), slugify(stem))
    # Free-prose providers ("Umweltbundesamt, eurostat & own projection") keep
    # their full text in the locale seed; only the key has to be stable.
    _source_texts.setdefault(key, provider)
    entry = {"key": key}
    if code:
        entry["code"] = code
    return entry


# ---------------------------------------------------------------------------
# Values
# ---------------------------------------------------------------------------

def _to_date(x):
    if isinstance(x, (datetime.datetime, datetime.date)):
        return x.strftime("%Y-%m-%d")
    if isinstance(x, np.datetime64):
        return str(x)[:10]
    if isinstance(x, (int, np.integer)):
        return "%04d-01-01" % int(x)
    return str(x)[:10]


def _to_value(y):
    """Numpy scalar -> JSON number, with NaN/inf collapsing to null (a gap)."""
    if y is None:
        return None
    try:
        v = float(y)
    except (TypeError, ValueError):
        return None
    if np.isnan(v) or np.isinf(v):
        return None
    return round(v, 6)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_charts = []
_titles = {}
_series_labels = {}
_unit_labels = {}
_group_labels = {}


def _align(x_all, xs, values):
    """One series' values, placed on the chart's shared x axis, null elsewhere."""
    index = {d: i for i, d in enumerate(x_all)}
    col = [None] * len(x_all)
    for xi, vi in zip(xs, values):
        d = _to_date(xi)
        if d in index:
            col[index[d]] = _to_value(vi)
    return col


def _columns(series_dict):
    """{label: {x, y}} -> ordered keys, shared x axis, aligned columns.

    Series in one chart do not always share an x axis (the projection chart
    overlays a historic series with a shorter projected one), so the x axis is
    the sorted union and every series is padded with null. That is also what
    makes a real gap in the middle of a series representable at all.
    """
    keys = []
    labels = {}
    by_key = {}
    for label in series_dict:
        key = slugify(label)
        base, n = key, 2
        while key in by_key:
            # A collision would silently merge two series into one column.
            key = "%s_%d" % (base, n)
            n += 1
        keys.append(key)
        labels[key] = clean_text(label)
        by_key[key] = series_dict[label]

    x_all = sorted({_to_date(x) for s in by_key.values() for x in s["x"]})

    columns = {}
    for key in keys:
        s = by_key[key]
        columns[key] = _align(x_all, s["x"], s["y"])
    return keys, labels, x_all, columns


def _scale(payload, factor):
    def scale_cols(cols):
        for k in cols:
            cols[k] = [None if v is None else round(v / factor, 6) for v in cols[k]]
    if "groups" in payload:
        for g in payload["groups"].values():
            scale_cols(g["series"])
    else:
        scale_cols(payload["series"])
    # An error bar is in the same unit as the series it belongs to, so it has to
    # travel through the same division. Missing it would draw the bars in the
    # unscaled unit -- visually huge, and wrong in a way that reads as a modelling
    # result rather than as a bug.
    if payload.get("uncertainty"):
        scale_cols(payload["uncertainty"])


def register(chart_id, title, unit, data_plot, view, time_res,
             unit_fac=1, source_text=None, info_text=None, preliminary=False,
             initial_visible=None, page=None, section=None, order=0):
    """Write public/data/<id>.json and add this chart to the manifest.

    Called only from charts.spec.chart(), which is where the arguments are
    validated; this function does the writing.
    """
    cid = chart_id

    unit_key = slugify(unit) if unit else None
    if unit_key:
        _unit_labels.setdefault(unit_key, clean_text(unit))

    title_text = clean_text(title)
    if title_text:
        entry = {"title": title_text}
        if info_text:
            entry["info"] = clean_text(info_text)
        _titles[cid] = entry

    payload = {"id": cid, "updated": datetime.date.today().strftime("%Y-%m-%d")}
    group_keys = None

    if view == "groups":
        # A chart with a dataset selector: data_plot is {group: {"data": {...}}}
        group_keys = []
        groups_out = {}
        series_keys = []
        for label in data_plot:
            gkey = slugify(label)
            group_keys.append(gkey)
            _group_labels.setdefault(gkey, clean_text(label))
            keys, labels, x_all, columns = _columns(data_plot[label]["data"])
            for k in labels:
                _series_labels.setdefault(k, labels[k])
            if not series_keys:
                series_keys = keys
            groups_out[gkey] = {"x": x_all, "series": columns}
        payload["groups"] = groups_out
        first = data_plot[list(data_plot)[0]]
        meta = first.get("meta", {}) if isinstance(first, dict) else {}
    else:
        keys, labels, x_all, columns = _columns(data_plot["data"])
        for k in labels:
            _series_labels.setdefault(k, labels[k])
        series_keys = keys
        payload["x"] = x_all
        payload["series"] = columns
        meta = data_plot.get("meta", {})

        # Error-bar half-widths, one column per series that carries them, on the
        # same x axis as the series. The manifest only ever named *which* series
        # had an uncertainty; the values themselves stayed in Python, so the
        # projection chart shipped its confidence band as a flag with no data
        # behind it and the frontend drew nothing.
        bands = {}
        for label, values in (meta.get("uncertainty") or {}).items():
            if label not in data_plot["data"]:
                continue
            bands[slugify(label)] = _align(x_all, data_plot["data"][label]["x"], values)
        if bands:
            payload["uncertainty"] = bands

    if unit_fac and unit_fac != 1:
        _scale(payload, unit_fac)

    os.makedirs(PUBLIC_DATA, exist_ok=True)
    with open("%s/%s.json" % (PUBLIC_DATA, cid), "w", encoding="utf-8") as fp:
        json.dump(payload, fp, separators=(",", ":"), ensure_ascii=False)

    chart = {
        "id": cid,
        "page": page,
        "section": section,
        "order": order,
        "type": view,
        "time_res": time_res or "yearly",
        "unit": unit_key,
        "series": series_keys,
    }
    if group_keys:
        chart["groups"] = group_keys
    if view == "toggle":
        chart["toggle"] = ["area", "bar", "line"]
        chart["initial"] = initial_visible or "area"
    # "Total" is drawn in ink rather than taking a palette slot; it is a series
    # like any other in the data, so the frontend has to be told which one.
    for candidate in ("total", "historic_emissions"):
        if candidate in series_keys:
            chart["total"] = candidate
            break
    if meta.get("uncertainty"):
        chart["uncertainty"] = [slugify(k) for k in meta["uncertainty"]]
    if meta.get("areas"):
        chart["areas"] = [slugify(k) for k in meta["areas"]]
    # Per-series interpolation values for the legend label, e.g. which month the
    # "observed to date" series runs to. The label text stays in the locale files
    # with a {month} placeholder; only the number travels, so the frontend can
    # spell the month in the reader's language. Series keys that encoded the
    # month instead needed four new locale keys every time the data advanced.
    if meta.get("labels"):
        chart["labels"] = {slugify(k): v for k, v in meta["labels"].items()}
    # Written only when true, so it disappears from the manifest of its own
    # accord the first time a final figure replaces the provisional drop.
    if preliminary:
        chart["preliminary"] = True
    src = _source(source_text)
    if src:
        chart["source"] = src

    # Replace rather than append: the fossil-fuel consumption charts are built
    # by the same function the emissions projection needs, so a chart can be
    # registered twice in one run and would otherwise appear twice.
    for i, existing in enumerate(_charts):
        if existing["id"] == cid:
            _charts[i] = chart
            break
    else:
        _charts.append(chart)
    return chart


# ---------------------------------------------------------------------------
# Finalisation
# ---------------------------------------------------------------------------

def _write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2, ensure_ascii=False, sort_keys=True)
        fp.write("\n")


def finalize(prune=True, write_seed=True):
    """Write the manifest, drop stale data files, and seed the English locale.

    Pruning is the fix for the ~13 orphaned chart files that accumulated under
    Jekyll: nothing ever deleted the output of a chart that had been renamed or
    switched off, so they stayed committed and served.
    """
    manifest = {
        "generated": datetime.date.today().strftime("%Y-%m-%d"),
        "charts": _charts,
    }
    _write_json(PUBLIC_DATA + "/manifest.json", manifest)

    removed = []
    if prune:
        keep = {c["id"] for c in _charts}
        for path in os.listdir(PUBLIC_DATA):
            if not path.endswith(".json") or path == "manifest.json":
                continue
            if path[:-5] not in keep:
                os.remove(os.path.join(PUBLIC_DATA, path))
                removed.append(path[:-5])

    if write_seed:
        _write_json(LOCALE_SEED + "/charts.json", _titles)
        _write_json(LOCALE_SEED + "/common.json", {
            "series": _series_labels,
            "units": _unit_labels,
            "groups": _group_labels,
            "sources": _source_texts,
        })

    return {"charts": len(_charts), "pruned": removed}


def summary():
    """Chart ids that landed with no page assignment - i.e. generated but shown
    nowhere. Reported rather than silently tolerated: that is exactly how the
    Jekyll site ended up serving charts nothing regenerated."""
    return [c["id"] for c in _charts if not c.get("page")]
