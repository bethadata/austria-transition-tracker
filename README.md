# AUSTRIA TRANSITION TRACKER

Welcome to the **Austria energy and sustainability transition tracker**. 
The projet collects available data from various sources and publishes them on a static dashboard to provide a comprehensive overview over the energy transition and related topics in Austria. 

## Structure
The folder "services" contains the data-scraping and plot-creation services, both realized with python. Note that some data sets (e.g., Statistics Austria) are updated manually.
Under "page" you find all html/css/md files relevant for the static page.

## Setup locally

#### Static page
To run the site locally, install <a href = "https://jekyllrb.com/docs/installation/windows/">Jekyll and Bundler via Ruby </a>. If Jekyll has been installed, run "bundle exec jekyll serve" in the "page" directory. You should then be able to navigate to the site via "localhost:3000" in your browser and visualize all data. 

#### Data-scraping and plot-creating 
Dependencies are found in **services/pyproject.toml**, setup is recommended using [Poetry](https://python-poetry.org/).

Within the **config.py**, you have to assign your local directory of the project to the **BASEPATH**-variable, which will define where data-files and charts will be saved.

For automatic data scraping of eurostat data and other automatized data-sources run **services/scrape_data.py**. Other data sources such as E-control, Statistik Austria, umweltbundesamt, or national inventory reports, have to be downloaded manually. 

To create or update all chartes run **services/create_charts.py**. 

#### Automatization and github-publishing
Finally, for setting up an automatic build process of the whole dashobard, including data download, chart creating, and github publishing, you can use the **services/main.py**. Note that for *.githhub*-pages publishing, a corresponding remote branch has to be set within your local repository. 