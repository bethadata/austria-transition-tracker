---
layout: page
title: Energy
permalink: /energy/
---


<div class="row-text">

 <div class="spacer"></div>

 <div class="column_left">
    This page shows the monthly and yearly data on energy use in Austria, with a few more detailed data sets regarding electricity production.
  </div>
  
 <div class="spacer"></div>

  <div class="column_right">
  </div>
   <div class="spacer"></div>

</div> 


<div id="gross_final_energy" class="row">
  <div class="spacer"></div>

  <div class="header-container">
    <h3 class="section-header">Gross and final energy consumption</h3>
    <hr>
  </div>

  <div class="spacer"></div>
</div>


<div class="row"> 
<div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_gross_inland_consumption_absolute.html %}
  </div>

  <div class="spacer"></div>

  <div class="column_right">
    {% include AT_timeseries_gross_inland_consumption_share.html %}
  </div>
   <div class="spacer"></div>

</div> 

<div class="row"> 
<div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_total_final_energy_use.html %}
  </div>

  <div class="spacer"></div>

  <div class="column_right">
    {% include AT_timeseries_total_final_energy_use_share.html %}
  </div>
   <div class="spacer"></div>

</div> 


<div id="electricity_district_heating" class="row">
  <div class="spacer"></div>

  <div class="header-container">
    <h3 class="section-header">Electricity</h3>
    <hr>
  </div>

  <div class="spacer"></div>
</div>


<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_elec_prod_monthly.html %}
  </div>

  <div class="spacer"></div>

  <div class="column_right">
   {% include AT_timeseries_elec_prod_monthly_share.html %}
  </div>
   <div class="spacer"></div>

</div> 

<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
  </div>

  <div class="spacer"></div>

  <div class="column_right">
   {% include AT_timeseries_elec_prod_monthly_share_cons.html %}
  </div>
   <div class="spacer"></div>

</div> 



<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
   {% include AT_timeseries_elec_energy_use.html %}
  </div>

  <div class="spacer"></div>

  <div class="column_right">
   {% include AT_timeseries_elec_energy_use_share.html %}
  </div>
   <div class="spacer"></div>

</div> 


<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
  </div>

  <div class="spacer"></div>

  <div class="column_right">
   {% include AT_timeseries_elec_energy_use_share_cons.html %}
  </div>
   <div class="spacer"></div>

</div> 


<div id="electricity_district_heating" class="row">
  <div class="spacer"></div>

  <div class="header-container">
    <h3 class="section-header">District heating</h3>
    <hr>
  </div>

  <div class="spacer"></div>
</div>

<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_dh_energy_use.html %}
  </div>

  <div class="spacer"></div>

  <div class="column_right">
   {% include AT_timeseries_dh_energy_use_share.html %}
  </div>
   <div class="spacer"></div>

</div> 
