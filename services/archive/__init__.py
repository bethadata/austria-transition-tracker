"""Code that is no longer wired up, kept because it is not reconstructible.

Nothing here is imported by the pipeline, and nothing here should be: several
modules reference functions and paths that no longer exist. Each file's docstring
says what it was, why it stopped being live, and what replaced it.

  plotly_figures.py             the Jekyll-era Plotly figure builders. The
                                pipeline stopped drawing when the HTML writer
                                was deleted (2026-08-24); appearance is now
                                src/components/TimeSeriesChart.vue.
  national_inventory_sectors.py the NIR sub-sector emissions reader, superseded
                                by sources/eea.py. Carries F-gas GWP
                                conversions and a waste-CHP split the EEA route
                                does not have.
  unused_readers.py             two readers from the old filter.py that nothing
                                called: a monthly-to-yearly extrapolation and
                                the ESR/ETS split of the national total.
  emissions_estimation.py       earlier iterations of the emissions projection,
  emissions_extrapolation.py    archived before the 2026-08 Vue migration.
  filter_temp.py                a scratch file that read a 2023 vehicle
                                yearbook at import time. Kept only as a record
                                that the file existed; delete it freely.
  plot_fluorinated_gases.py     a module whose plot() was `pass`. The F-gas
                                chart comes from charts/overview.py.
"""
