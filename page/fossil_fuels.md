---
layout: page
title: Fossil Fuels
permalink: /fossil_fuels/
---


<div class="row-text">

 <div class="spacer"></div>

 <div class="column_left">
    This page shows the monthly and yearly consumption of various fossil fuels in Austria, as they are reported by eurostat on a monthly basis. For each fuel, the monthly data are shown (left column). On the right column the yearly data are shown, which are separated up to the last available month of the current year. For the current year, the consumption is extrapolated based on the consumption trend so far. The extrapolation of this data forms the basis for the <b><a href= "{{ "/consumption-estimation/" | relative_url }}">GHG emission extrapolation </a></b> .
  </div>
  
 <div class="spacer"></div>

  <div class="column_right">
    <!-- <div class="toc">
    <a href="#natural_gas" class="toc-button">Natural gas</a>
    <a href="#oil" class="toc-button">Oil</a>
    <a href="#coal" class="toc-button">Coal</a>
    </div>   -->
  </div>
   <div class="spacer"></div>

</div> 


<div id="natural_gas" class="row">
  <div class="spacer"></div>

  <div class="header-container">
    <h3 class="section-header">Natural gas</h3>
    <hr>
  </div>

  <div class="spacer"></div>
</div>

<div class="row">

 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_consumption_natural_gas_monthly.html %}
  </div>
  
 <div class="spacer"></div>

  <div class="column_right">
   {% include AT_timeseries_consumption_natural_gas_yearly.html %}
  </div>

   <div class="spacer"></div>

</div> 


<div class="row">

 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_gas_sectoral_consumption_monthly.html %}
  </div>
  
 <div class="spacer"></div>

  <div class="column_right">
    {% include AT_timeseries_gas_sectoral_consumption_yearly.html %}
  </div>

   <div class="spacer"></div>

</div> 


<div id="oil" class="row">
  <div class="spacer"></div>

  <div class="header-container">
    <h3 class="section-header">Oil</h3>
    <hr>
  </div>

  <div class="spacer"></div>
</div>

<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_consumption_gasoline_monthly.html %}
  </div>
  
 <div class="spacer"></div>

  <div class="column_right">
      {% include AT_timeseries_consumption_gasoline_yearly.html %}
  </div>

   <div class="spacer"></div>

</div> 


<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_consumption_diesel_monthly.html %}
  </div>
  
 <div class="spacer"></div>

  <div class="column_right">
      {% include AT_timeseries_consumption_diesel_yearly.html %}
  </div>
   <div class="spacer"></div>

</div> 


<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_consumption_heating_oil_monthly.html %}
  </div>
  
 <div class="spacer"></div>

  <div class="column_right">
      {% include AT_timeseries_consumption_heating_oil_yearly.html %}
  </div>
   <div class="spacer"></div>

</div> 


<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_consumption_refinery_gas_monthly.html %}
  </div>
  
 <div class="spacer"></div>

  <div class="column_right">
      {% include AT_timeseries_consumption_refinery_gas_yearly.html %}
  </div>
   <div class="spacer"></div>

</div> 

<div id="coal" class="row">
  <div class="spacer"></div>

  <div class="header-container">
    <h3 class="section-header">Coal</h3>
    <hr>
  </div>

  <div class="spacer"></div>
</div>


<div id class="row">

 <div class="spacer"></div>
  <div class="column_left">
  
    {% include AT_timeseries_consumption_hard_coal_electricity_monthly.html %}
  </div>
  
 <div class="spacer"></div>

  <div class="column_right">
      {% include AT_timeseries_consumption_hard_coal_electricity_yearly.html %}
  </div>
   <div class="spacer"></div>

</div> 


<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_consumption_hard_coal_industry_monthly.html %}
  </div>
  
 <div class="spacer"></div>

  <div class="column_right">
      {% include AT_timeseries_consumption_hard_coal_industry_yearly.html %}
  </div>
   <div class="spacer"></div>

</div> 



<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_consumption_hard_coal_coke_ovens_monthly.html %}
  </div>
  
 <div class="spacer"></div>

  <div class="column_right">
      {% include AT_timeseries_consumption_hard_coal_coke_ovens_yearly.html %}
  </div>
   <div class="spacer"></div>

</div> 




<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_consumption_coke_oven_coke_monthly.html %}
  </div>
  
 <div class="spacer"></div>

  <div class="column_right">
      {% include AT_timeseries_consumption_coke_oven_coke_yearly.html %}
  </div>
   <div class="spacer"></div>

</div> 



