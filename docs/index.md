---
layout: home
---


<div class="row">
 <div class="spacer"></div>

  <div class="column_left">
  <br>
  <b>Welcome to the <i>Austria Transition Tracker!</i> </b> <br>
  This site collects and displays various data connected to the sustainable transition in Austria. <br>
  <br>
  On the chart to the right you can see the historical greenhouse gas (GHG) emissions and corresponding sector contributions in Austria. The target of this page is to track the (hopefully) continuing transition to zero emissions with public available data.  <br> 
  <br>  
  On the top menu you can navigate to the different <b>sectors</b> shown in the chart to show more detailed data of each sector. In addition, there are extra pages on <b><a href= "{{ "/energy/" | relative_url }}">energy</a></b> and <b><a href= "{{ "/fossil_fuels/" | relative_url }}">fossil fuels</a></b> that tracke some more general trends. <br>
  <br> 
  New data sets are added constantly, depending on time resources and convenient availability - any suggestions are very welcome! <br>
  For more information, data sources, and technical details please visit the <b><a href= "{{ "/about/" | relative_url }}">About page.</a></b> <br> 
  <br>   
  </div>

 <div class="spacer"></div>

  <div class="column_right">
      {% include AT_timeseries_co2_emissions_sectors.html %}
  </div>

   <div class="spacer"></div>

</div> 

<div id="ghg_projection" class="row">
  <div class="spacer"></div>

  <div class="header-container">
    <h3 class="section-header">Current GHG emission projection</h3>
    <hr>
  </div>

  <div class="spacer"></div>
</div>


<div class="row">

 <div class="spacer"></div>

  <div class="column_left"> 
   {% include AT_timeseries_emissions_projection_yearly.html %}
   </div>

  <div class="spacer"></div>

  <div class="column_right">
  <br> 
    Official detailed emission statistics are only available several months after the respective year. However, rough emission projections are possible with more timely available fossil fuel consumption data. On the chart to the left a projection of Austrian greenhouse gas emissions with latest available data is shown. The exact methodology <b><a href= "{{ "/consumption-estimation/" | relative_url }}">is described here</a></b>. In short, eurostat data of fossil fuel consumption is extrapolated to the full year and scaled with emission factors to arrive at actual energy-sector related emission estimations (Transport, Buildings, Energy & Industry, including process emissions). Other sectors (Agriculture, Waste, Fluorinated Gases) are extrapolated based on current trends. <br> 
    <br> 
    The model is rather simple and based on past data and temporal correlation. Extrapolated data must therefore be interpreted with great care, especially early in the year! <br> 
    <br> 
    Estimated monthly and yearly emission data (including extrapolations) of all considered fossil fuels are shown below. Detailed consumption data of specific fuels are shown on the <b><a href= "{{ "/fossil_fuels/" | relative_url }}">fossil fuels page</a></b> <br><br>

  </div>

   <div class="spacer"></div>

</div> 


<div class="row">
</div> 

<div class="row">

 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_emissions_fuels_monthly.html %}
  </div>
  
 <div class="spacer"></div>

  <div class="column_right">
   {% include AT_timeseries_emissions_fuels_yearly.html %}
  </div>

   <div class="spacer"></div>

</div> 


<div id="ghg_lulucf" class="row">
  <div class="spacer"></div>

  <div class="header-container">
    <h3 class="section-header">GHG including LULUCF and shares</h3>
    <hr>
  </div>

  <div class="spacer"></div>
</div>


<div class="row">

 <div class="spacer"></div>

  <div class="column_left">
    {% include AT_timeseries_co2_emissions_sectors_with_LULUCF.html %}
  </div>
  
 <div class="spacer"></div>

  <div class="column_right">
   {% include AT_timeseries_co2_emissions_sectors_shares.html %}
  </div>

   <div class="spacer"></div>

</div> 