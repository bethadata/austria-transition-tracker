---
layout: page
title: Transport 
permalink: /transport/
---

<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    <br>
    Transport emissions, as documented according to international accounting standards, stem almost exclusively from the combustion of gasoline and diesel in the road sector (passenger and duty vehicles). Ship, rail, national aviation and mobile military vehicles have minor contributions (included in Other). <br>
    <!-- As can be seen in the graphics to the right, large parts of the emissions in Austria stem from fuel exports ("tank tourism"). <br>     -->
    <br> 
    Emissions of international aviation are not included in the national emission statistics, their contribution by combustion of kerosene to the real emissions is however still significant (see Kerosene consumption below). <br>
    <br>
    Data tracked on this page are mostly related to road transport, including monthly fuel consumption, new registrations and stock of different vehicle classes by type of motor energy. <br>
    <br>

  </div>

  <div class="spacer"></div>

  <div class="column_right">
      {% include AT_timeseries_transport_emissions_sectors.html %}
  </div>
   <div class="spacer"></div>

</div> 

<div id="energy_use" class="row">
  <div class="spacer"></div>

  <div class="header-container">
    <h3 class="section-header">Energy use</h3>
    <hr>
  </div>

  <div class="spacer"></div>
</div>

<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_transport_final_energy_use.html %}
  </div>

  <div class="spacer"></div>

  <div class="column_right">
    {% include AT_timeseries_transport_final_energy_use_share.html %}
  </div>
   <div class="spacer"></div>

</div> 


<div id="fuel_consumption" class="row">
  <div class="spacer"></div>

  <div class="header-container">
    <h3 class="section-header">Fuel consumption</h3>
    <hr>
  </div>

  <div class="spacer"></div>
</div>

<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_road_fuels_consumption.html %}
  </div>

  <div class="spacer"></div>

  <div class="column_right">
    {% include AT_timeseries_road_biofuels_consumption.html %}
  </div>
   <div class="spacer"></div>

</div> 

<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_kerosene_consumption.html %}
  </div>

  <div class="spacer"></div>

  <div class="column_left">
  </div>
 <div class="spacer"></div>

</div> 

<div id="vechicle shares" class="row">
  <div class="spacer"></div>

  <div class="header-container">
    <h3 class="section-header">Share of vehicles (new/stock)</h3>
    <hr>
  </div>

  <div class="spacer"></div>
</div>

<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_share_fuel_new_cars.html %}
  </div>

  <div class="spacer"></div>

  <div class="column_right">
    {% include AT_timeseries_number_fuel_new_cars.html %}
  </div>
   <div class="spacer"></div>

</div> 


<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_share_fuel_new_cars_yearly.html %}
  </div>

  <div class="spacer"></div>

  <div class="column_right">
    {% include AT_timeseries_number_fuel_new_cars_yearly.html %}
  </div>
   <div class="spacer"></div>

</div> 


<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_share_fuel_stock_cars.html %}
  </div>

  <div class="spacer"></div>

  <div class="column_right">
    {% include AT_timeseries_number_fuel_stock_cars.html %}
  </div>
   <div class="spacer"></div>

</div> 


<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_monthly_registrations_brands_shares.html %}
  </div>

  <div class="spacer"></div>

  <div class="column_right">
    {% include AT_timeseries_monthly_registrations_brands_absolute.html %}
  </div>
   <div class="spacer"></div>

</div> 



<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_yearly_registrations_brands_shares.html %}
  </div>

  <div class="spacer"></div>

  <div class="column_right">
    {% include AT_timeseries_yearly_registrations_brands_absolute.html %}
  </div>
   <div class="spacer"></div>

</div> 



<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_share_fuel_new_lorries_le3p5.html %}
  </div>

  <div class="spacer"></div>

  <div class="column_right">
    {% include AT_timeseries_number_fuel_new_lorries_le3p5.html %}
  </div>
   <div class="spacer"></div>

</div> 

<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_share_fuel_new_lorries_gt3p5.html %}
  </div>

  <div class="spacer"></div>

  <div class="column_right">
    {% include AT_timeseries_number_fuel_new_lorries_gt3p5.html %}
  </div>
   <div class="spacer"></div>

</div> 

<div id="rail" class="row">
  <div class="spacer"></div>

  <div class="header-container">
    <h3 class="section-header">Rail</h3>
    <hr>
  </div>

  <div class="spacer"></div>
</div>

<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_rail_tracks_abs.html %}
  </div>

  <div class="spacer"></div>

  <div class="column_right">
    {% include AT_timeseries_rail_tracks_rel.html %}
  </div>
   <div class="spacer"></div>

</div> 
