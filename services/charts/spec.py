# -*- coding: utf-8 -*-
"""`chart()` -- the one way a chart enters the data contract.

Every chart module ends in calls to this function. It takes what the frontend
needs in order to render, and nothing else: an id, the series, the axis
resolution, the unit and source as text to be translated, and which of the
handful of shapes the chart is. It then hands all of that to `manifest.register`,
which writes `public/data/<id>.json` and one manifest entry.

**This function does not draw.** It used to: `plot_single.py` built a complete
Plotly figure per chart -- traces, colours, hover templates, layout, source
annotation -- and wrote it out as a standalone HTML document for Jekyll to
inline. The 2026-08-24 migration deleted the HTML writer but left the figure
building in place, so ~600 lines ran every pipeline run and produced an object
that was immediately discarded. Appearance is the frontend's job now
(`src/components/TimeSeriesChart.vue`), and the old builders are in
`archive/plotly_figures.py` for reference.

That is also why the old keyword arguments are gone rather than deprecated:
`colors=`, `plotmax_fac=`, `legend_inside=`, `show_plot=` and `save=` fed only
the discarded figure. Passing one now is a TypeError, which is the point -- a
silently ignored styling argument is how a call site comes to look like it
controls something it does not.

Shapes (`view=`):

  line        plain time series
  area        stacked areas
  area_neg    stacked areas that also go below zero (the LULUCF sink)
  bar         stacked bars
  toggle      area / bar / line, the reader picks; `initial=` sets the default
  groups      a dataset selector; `data` is {group: {"data": {...}}}, one level
              deeper than every other shape

`meta` on the incoming data still carries the two things that are per-series
rather than per-chart -- `uncertainty` (error-bar half widths) and `areas` (the
series that are filled even on a `line` chart) -- because they belong to the
numbers, not to the presentation.
"""

from . import manifest
from . import pages

#: The shapes the frontend can render. Checked here rather than trusted: an
#: unknown value used to fall through every branch of the old plotter and
#: produce an empty figure, and it would now produce a manifest entry the
#: frontend has no case for -- a card with a title and no chart in it.
VIEWS = ("line", "area", "area_neg", "bar", "toggle", "groups")

#: Axis resolutions. Decides the hover and tick format in the frontend.
TIME_RES = ("monthly", "yearly")


def chart(chart_id,
          title,
          unit,
          data,
          source,
          view="line",
          time_res="monthly",
          initial=None,
          note=None,
          preliminary=False,
          unit_fac=1):
    """Register one chart. Returns its manifest entry.

    chart_id  stable id: locale key, data filename and manifest key in one
    title     English title; seeds src/locales/_seed/charts.json and is then
              frontend-owned in both locales (D2). Never rendered from here.
    unit      English unit label; seeded and keyed the same way
    data      {"data": {label: {"x": [...], "y": [...]}}, "meta": {...}}
    source    provenance as text, e.g. "eurostat (NRG_CB_GASM)". The dataset
              code is split out into structured provenance by the manifest
    view      one of VIEWS
    time_res  "monthly" or "yearly"
    initial   for view="toggle": which of area/bar/line opens
    note      a short caveat shown under the chart, seeded like the title
    preliminary  the newest point is provisional. A flag rather than words in
              `note`, because the note is one locale string per chart and could
              therefore only ever describe one of the two cases: the frontend
              appends `common.chart.preliminary` when this is set, and drops it
              again by itself once the final figure supersedes the drop
    unit_fac  divisor applied to every value on the way out, error bars included
    """
    if view not in VIEWS:
        raise ValueError("%s: unknown view %r (expected one of %s)"
                         % (chart_id, view, ", ".join(VIEWS)))
    if time_res not in TIME_RES:
        raise ValueError("%s: unknown time_res %r" % (chart_id, time_res))
    if view == "toggle" and initial is None:
        initial = "area"
    if initial is not None and view != "toggle":
        raise ValueError("%s: initial= is only meaningful for view='toggle'" % chart_id)
    if not source:
        # Every chart on the site names its source. An unsourced one is a
        # reviewing failure, not a rendering one, so it fails at build time.
        raise ValueError("%s: no source" % chart_id)

    page, section, order = pages.lookup(chart_id)
    return manifest.register(
        chart_id=chart_id,
        title=title,
        unit=unit,
        data_plot=data,
        view=view,
        time_res=time_res,
        unit_fac=unit_fac,
        source_text=source,
        info_text=note,
        preliminary=preliminary,
        initial_visible=initial,
        page=page,
        section=section,
        order=order,
    )
