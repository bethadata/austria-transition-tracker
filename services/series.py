# -*- coding: utf-8 -*-
"""Series algebra: the vocabulary the sources and the chart modules share.

`total`, `shares`, `residual` and `to_yearly` appeared -- open-coded, with
slightly different NaN behaviour each time -- in nine of the eleven chart
modules. `charts/energy.py` alone built the same "Other = Total minus the named
fuels" subtraction twice, eight `np.array(...)` terms deep, and the same
`value * 100 / total` share loop four times. Two of those hand-rolled share
loops forgot the `* 100` and shipped a chart labelled "%" whose values ran 0 to
1 (`rail_tracks_rel`, `share_heating_systems` -- both fixed by moving to
`shares`).

The shape everything speaks is the one the pipeline has always used:

    {"data": {label: {"x": [...], "y": [...]}},
     "meta": {...}}                              # optional

`x` is datetimes, `y` is numbers with `nan` for "not published". Series in one
chart are not required to share an x axis.

**The NaN rule, spelled out once because getting it wrong is invisible.** A gap
is not a zero: an unpublished month must break the line rather than draw a
collapse to nothing. But when subtypes are *summed into* a category, a subtype
the source does not list contributes nothing, so a gap there is 0. The
resolution both ways round:

  * summing treats a gap as 0, **unless every input is a gap**, in which case
    the result is a gap. That is what keeps one missing subtype from poisoning a
    category (and then every month derived from it, and then every share divided
    by it -- 791 regressions from one NaN, found during the 2026-08 migration)
    while still leaving a genuinely empty year empty.
  * dividing propagates gaps, and a zero denominator yields a gap rather than an
    inf. An inf reaches the JSON writer as null anyway, but only after numpy has
    warned about it, so it is done deliberately here.
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------

def values(data, label):
    """One series' y values as a float array, whatever container it arrived in."""
    return np.asarray(data["data"][label]["y"], dtype=float)


def times(data, label):
    """One series' x values as a list, whatever container it arrived in."""
    return list(data["data"][label]["x"])


def labels(data, exclude=()):
    """The series labels in their declared order. Order is the colour order."""
    return [k for k in data["data"] if k not in exclude]


def series(x, y):
    return {"x": list(x), "y": np.asarray(y, dtype=float)}


def wrap(pairs, meta=None):
    """[(label, {"x","y"}), ...] -> a data_plot, preserving order.

    A dict literal would do the same, but going through here makes the ordering
    intent explicit at the call site: the order of these pairs is the order of
    the legend and of the palette.
    """
    out = {"data": {label: s for label, s in pairs}}
    if meta:
        out["meta"] = meta
    return out


def _nansum(columns):
    """Sum columns elementwise; a position where every column is nan stays nan."""
    stack = np.vstack([np.asarray(c, dtype=float) for c in columns])
    summed = np.nansum(stack, axis=0)
    summed[np.all(np.isnan(stack), axis=0)] = np.nan
    return summed


def _divide(numerator, denominator):
    """numerator / denominator with a gap wherever the answer is not defined."""
    num = np.asarray(numerator, dtype=float)
    den = np.asarray(denominator, dtype=float)
    out = np.full(len(num), np.nan)
    ok = ~np.isnan(num) & ~np.isnan(den) & (den != 0)
    out[ok] = num[ok] / den[ok]
    return out


# ---------------------------------------------------------------------------
# Alignment
# ---------------------------------------------------------------------------

def align(data, axis=None, on=None):
    """Put every series on one shared x axis, padding with nan.

    Series in a chart are aligned **by date**, never by position. The old code
    aligned by slicing the tail of the longer array, which happened to work only
    because every series ended in the same month; a single balance published a
    month late would have shifted a whole series sideways and nothing would have
    looked wrong.

    axis  the x axis to use; defaults to the sorted union of every series'
    on    align to this series' axis instead (drops dates outside it)
    """
    if on is not None:
        axis = times(data, on)
    if axis is None:
        axis = sorted({t for label in data["data"] for t in times(data, label)})
    axis = list(axis)
    index = {t: i for i, t in enumerate(axis)}

    out = []
    for label in data["data"]:
        col = np.full(len(axis), np.nan)
        for t, v in zip(times(data, label), values(data, label)):
            if t in index:
                col[index[t]] = v
        out.append((label, series(axis, col)))
    return wrap(out, data.get("meta"))


# ---------------------------------------------------------------------------
# Derived series
# ---------------------------------------------------------------------------

def total(data, name="Total", exclude=()):
    """Append a series that is the sum of the others.

    The total is appended last so it does not take a palette slot: the frontend
    draws whichever series is named `total` in ink, on top of the stack.
    """
    src = align(data)
    parts = labels(src, exclude=tuple(exclude) + (name,))
    axis = times(src, parts[0])
    summed = _nansum([values(src, p) for p in parts])
    out = [(label, src["data"][label]) for label in src["data"] if label != name]
    out.append((name, series(axis, summed)))
    return wrap(out, src.get("meta"))


def shares(data, of="Total", exclude=(), drop_total=True):
    """Every series as a percentage of a total.

    `of` may name a series in `data` (the usual case) or be an array. If it
    names a series that is not present, the total is computed from the series
    being shared out -- which is what "share of the stack" means and is what
    every open-coded version did when there was no Total series to hand.
    """
    src = align(data)
    excluded = tuple(exclude) + ((of,) if (drop_total and isinstance(of, str)) else ())
    parts = labels(src, exclude=excluded)
    if isinstance(of, str):
        if of in src["data"]:
            denominator = values(src, of)
        else:
            denominator = _nansum([values(src, p) for p in parts])
    else:
        denominator = np.asarray(of, dtype=float)

    axis = times(src, parts[0])
    return wrap([(label, series(axis, _divide(values(src, label), denominator) * 100))
                 for label in parts],
                src.get("meta"))


def residual(data, name, of="Total", parts=None):
    """Add a series holding whatever the named parts do not account for.

    This is the "Other" / "Industry / Other" bucket, and it is a deliberate
    modelling choice rather than arithmetic tidiness: the residual absorbs
    everything the source does not report separately, so the stack always adds
    up to the published total. Where a sub-series is unpublished for part of its
    range, its share of the total sits inside the residual for those dates --
    which is what the chart note has to say.
    """
    src = align(data)
    parts = list(parts) if parts is not None else labels(src, exclude=(of, name))
    axis = times(src, of)
    rest = _nansum([values(src, p) for p in parts])
    # nan_to_num on the parts, not on the total: a part nobody published
    # contributes nothing to what is already accounted for, whereas a total that
    # is missing leaves the residual genuinely unknown.
    remainder = values(src, of) - np.nan_to_num(rest)
    out = [(label, src["data"][label]) for label in src["data"] if label != name]
    out.append((name, series(axis, remainder)))
    return wrap(out, src.get("meta"))


def moving_average(x, y, window):
    """Trailing mean over `window` points, stamped at the last point of each.

    Trailing rather than centred, because the point of the 12-month line on
    these charts is "the last twelve months as of this date". A window that runs
    past the end of the data is not padded -- averaging in zeros there drew a
    decline through 2024-26 on the chicken-slaughter chart that never happened.
    """
    y = np.asarray(y, dtype=float)
    x = list(x)
    xs, ys = [], []
    for i in range(len(y) - window + 1):
        xs.append(x[i + window - 1])
        ys.append(np.mean(y[i:i + window]))
    return series(xs, ys)


def to_yearly(data, how="sum"):
    """Monthly series -> yearly, stamped on 1 January.

    `sum` reads a gap as "nothing to add" but keeps a year with no data at all
    as a gap: a partially published year is a partial figure (2023 buildings gas
    is a four-month number), a year with nothing is a hole. `mean` is for series
    that are levels rather than flows.
    """
    out = []
    for label in data["data"]:
        buckets = {}
        for t, v in zip(times(data, label), values(data, label)):
            buckets.setdefault(pd.Timestamp(year=t.year, month=1, day=1), []).append(v)
        axis = sorted(buckets)
        col = []
        for year in axis:
            real = [v for v in buckets[year] if not np.isnan(v)]
            if not real:
                col.append(np.nan)
            elif how == "mean":
                col.append(float(np.mean(real)))
            else:
                col.append(float(np.sum(real)))
        out.append((label, series(axis, col)))
    return wrap(out, data.get("meta"))


def scale(data, factor):
    """Multiply every series by a constant. Unit conversions, not unit_fac."""
    return wrap([(label, series(times(data, label), values(data, label) * factor))
                 for label in data["data"]],
                data.get("meta"))


def select(data, order):
    """Pick and reorder series. The order given is the palette order.

    Existing to be explicit about that: the chart modules used to reorder by
    rebuilding a dict literal, which reads as reformatting rather than as the
    CVD-safety decision it is.
    """
    return wrap([(label, data["data"][label]) for label in order], data.get("meta"))


def combine(data, name, parts, drop=True):
    """Merge several series into one (Waste = renewable + non-renewable waste)."""
    src = align(data)
    axis = times(src, parts[0])
    merged = _nansum([values(src, p) for p in parts])
    out = []
    placed = False
    for label in src["data"]:
        if label in parts:
            if not placed:
                out.append((name, series(axis, merged)))
                placed = True
            if drop:
                continue
        out.append((label, src["data"][label]))
    return wrap(out, src.get("meta"))
