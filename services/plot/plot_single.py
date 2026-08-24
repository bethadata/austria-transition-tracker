import plotly.graph_objects as go
from plotly.colors import get_colorscale 
import numpy as np
import plotly.express as px
from . import manifest
from . import pages

greys = get_colorscale("Greys")


def plot_single_go(title = "",
                   unit = "",
                   data_plot = {},
                   filename = "",
                   show_plot = False,
                   unit_fac = 1,
                   legend_inside = True,
                   colors = None,
                   time_res = "monthly",
                   source_text = None,
                   info_text = None,
                   plot_type = "line",
                   plotmax_fac = 1.1,
                   save = True):
    
    if source_text == None:
        source_text = "eurostat (%s)" %(data_plot["meta"]["code"])
                      
    if colors == None: 
        colors = px.colors.qualitative.Dark2.copy()
        colors.remove('rgb(231,41,138)')  #removes pink 
        ### swap two colors 
        colors[3],colors[4] = colors[4],colors[3]
          
    
    if time_res == "monthly": 
        hovertemplate = '%{x|%b-%Y}, %{y:.2f}'
    elif time_res == "yearly": 
        hovertemplate = '%{x|%Y}, %{y:.2f}'
    
    fig = go.Figure()
    plotmin = 0 
    
    if plot_type == "line": 
        plotmax = 0
        color_ind = 0
        for data in data_plot["data"]:
            y_data = np.array(data_plot["data"][data]["y"])/unit_fac
            
            if data == "Total": 
                color = "black"
            else: 
                color = colors[color_ind % len(colors)]
            
            error_y = dict()
            stackgroup = None
            
            if "meta" in data_plot: 
                if "uncertainty" in data_plot["meta"]: 
                    if data in data_plot["meta"]["uncertainty"]: 
                        error_y = dict(type = "data", 
                                       visible = True, 
                                       array= data_plot["meta"]["uncertainty"][data]) 
                       
                
                if "areas" in data_plot["meta"]: 
                    if data in data_plot["meta"]["areas"]: 
                        stackgroup = "one" 
                    
            fig.add_trace(
                go.Scatter(x = data_plot["data"][data]["x"], 
                           y = y_data,
                           mode= "lines",
                           stackgroup = stackgroup,
                           name = data,
                           error_y = error_y,
                           line = dict(color = color),
                           hovertemplate = hovertemplate)
                )
            color_ind += 1
            plotmax = max(plotmax, max(y_data)*plotmax_fac)
            
            
    elif plot_type == "area": 
        color_ind = 0
        sum_data = np.zeros(10)
        
        for data in data_plot["data"]:
            y_data = np.array(data_plot["data"][data]["y"])/unit_fac
            color = colors[color_ind % len(colors)]
            color_opacity = color.rstrip(")")+",0.6)"
            color_opacity = color_opacity.replace("rgb", "rgba")
            if data == "Total": 
                fig.add_trace(
                    go.Scatter(x = data_plot["data"][data]["x"], 
                               y = np.array(data_plot["data"][data]["y"])/unit_fac,
                               mode='lines',
                               name = data,
                               line = dict(color = "black"),
                               hovertemplate = hovertemplate))
            else:
                fig.add_trace(
                    go.Scatter(x = data_plot["data"][data]["x"], 
                               y = y_data,
                               stackgroup = "one",
                               line = dict(color = color),
                               # fill='tonexty', 
                               fillcolor=color_opacity,
                               mode='lines',
                               name = data,
                               hovertemplate = hovertemplate))
                color_ind += 1
            
                if sum(sum_data) == 0: 
                    sum_data = np.array(y_data)
                else: 
                    sum_data += np.array(y_data)
                
        plotmax = max(sum_data)*plotmax_fac
    
    
    elif plot_type == "area_neg": 
        
        color_ind = 0
        sum_data = np.zeros(10)
        
        for data in data_plot["data"]:
            y_data = np.array(data_plot["data"][data]["y"])/unit_fac
            color = colors[color_ind % len(colors)]
            color_opacity = color.rstrip(")")+",0.6)"
            color_opacity = color_opacity.replace("rgb", "rgba")
            
            if data == "Total": 
                fig.add_trace(
                    go.Scatter(x = data_plot["data"][data]["x"], 
                                y = np.array(data_plot["data"][data]["y"])/unit_fac,
                                mode='lines',
                                name = data,
                                legendgroup = data,
                                line = dict(color = "black"),
                                hovertemplate = hovertemplate))
            else:
                y_data = np.array(y_data)
                y_data_pos = np.zeros(len(y_data))
                y_data_pos[y_data>0] = y_data[y_data>0]
                y_data_neg = np.zeros(len(y_data))
                y_data_neg[y_data<=0] = y_data[y_data<=0]

                showlegendneg = True
                if sum(y_data_pos) > 0:
                    showlegendneg = False
                    fig.add_trace(
                        go.Scatter(x = data_plot["data"][data]["x"], 
                                    y = y_data_pos,
                                    stackgroup = "one",
                                    line = dict(color = color),
                                    # fill='tonexty', 
                                    fillcolor=color_opacity,
                                    mode='lines',
                                    name = data,
                                    legendgroup = data,
                                    hovertemplate = hovertemplate))
                    
                if sum(y_data_neg) < 0: 
                    fig.add_trace(
                        go.Scatter(x = data_plot["data"][data]["x"], 
                                    y = y_data_neg,
                                    stackgroup = "two",
                                    line = dict(color = color),
                                    # fill='tonexty', 
                                    fillcolor=color_opacity,
                                    showlegend = showlegendneg,
                                    name = data,
                                    mode='lines',
                                    legendgroup = data,
                                    hovertemplate = hovertemplate))
                
                color_ind += 1
            
                if sum(sum_data) == 0: 
                    sum_data = np.array(y_data_pos)
                    sum_data_neg = np.array(y_data_neg)
                else: 
                    sum_data += np.array(y_data_pos)
                    sum_data_neg += np.array(y_data_neg)

                
                
        plotmax = max(sum_data)*plotmax_fac
        plotmin = min(sum_data_neg)*plotmax_fac 
        
    
    
    elif plot_type == "area_button": 
        buttondata = []
        len_bals = len(data_plot)
        
        bal_ind = 0 
        for bal in data_plot: 
            len_siecs = len(data_plot[bal]["data"])
            
            color_ind = 0
            sum_data = np.zeros(10)
            
            for data in data_plot[bal]["data"]:
                y_data = np.array(data_plot[bal]["data"][data]["y"])/unit_fac
               
                if bal_ind == 0: visible = True 
                else: visible = False 

                fig.add_trace(
                    go.Scatter(x = data_plot[bal]["data"][data]["x"], 
                               y = y_data,
                               stackgroup = "one",
                               line = dict(color = colors[color_ind % len(colors)]),
                               mode='lines',
                               name = data,
                               visible = visible,
                               hovertemplate = hovertemplate))
                color_ind += 1
            
                if sum(sum_data) == 0: 
                    sum_data = np.array(y_data)
                else: 
                    sum_data += np.array(y_data)
                    
            log_list = np.array([False for i in range(int(len_siecs*len_bals))])
            log_list[bal_ind*len_siecs:(bal_ind+1)*len_siecs] = True 
            
            ### data for the dropdown menu batton 
            buttondata.append(dict(label = bal,
                  method = 'update',
                  args = [{'visible': log_list},
                          {'title': title,
                           'showlegend': True}]))
                    
            plotmax = max(sum_data)*plotmax_fac
            bal_ind += 1 
    
    elif plot_type == "bar":         
        # hovertemplate= ("%{customdata:> .2f}<extra></extra>")
        # hovertemplate= ("%{data.name}: %{customdata:> .2f}<extra></extra>")
        start = True 
        color_ind = 0
        fig.update_layout(barmode='stack')
        for data in data_plot["data"]:
            y_data = data_plot["data"][data]["y"]/unit_fac
            
            if data == "Total": 
                fig.add_trace(
                    go.Scatter(x = data_plot["data"][data]["x"], 
                               y = np.array(data_plot["data"][data]["y"])/unit_fac,
                               mode='lines',
                               name = data,
                               customdata = y_data,
                               legendgroup = data,
                               xhoverformat = "<b>%Y<b>",
                               line = dict(color = greys[7][1]),
                               hovertemplate = hovertemplate))
            else: 
                if start: 
                    sum_data = np.zeros(len(y_data))
                    start = False 
                    
                fig.add_trace(
                    go.Bar(x = data_plot["data"][data]["x"], 
                               y = y_data,
                               customdata = y_data,
                               name = data,
                               xhoverformat = "<b>%Y<b>",
                               hoverlabel  = dict(align = "right"),
                               marker_color = colors[color_ind],
                               base = sum_data,
                               hovertemplate = hovertemplate))
      
                sum_data += np.array(y_data)
                color_ind += 1 
            plotmax = max(sum_data)*plotmax_fac    
        
        # fig.update_layout(hovermode="x unified")
        
        
    
    if legend_inside: 
        legend_dict= dict(
            yanchor="bottom",
            y=0.01,
            xanchor="left",
            x=0.01)
        bottomshift = 0 
    else: 
        legend_dict=dict(
            yanchor="top",
            y=-0.07,
            xanchor="left",
            x=0.01)
        bottomshift = 100
    
    
    if plot_type == "area_button": 
        fig.update_layout(
            updatemenus=[go.layout.Updatemenu(
                active=0,
                buttons=list(buttondata),
                x=-0.05,
                xanchor="left",
                y=1.16,
                yanchor="top"
                )])
        title_shift_x = 0.90
        title_shift_y = -0.05 
        margin_up_shift = 0
        xanchor = "right" 
        
        if plotmax_fac == 1: 
            fig.update_layout(
                yaxis_range=[plotmin, plotmax])
        
        
    else: 
        fig.update_layout(
            yaxis_range=[plotmin, plotmax])
        title_shift_x = 0
        title_shift_y = 0
        margin_up_shift = 0
        xanchor = "left"
    
    ### reduce spacing between legend groups 
    fig.update_layout(legend_tracegroupgap=0)
    
    fig.update_layout(
        yaxis_title= unit,
        autosize = True,
        legend=legend_dict,
        yaxis = dict(
            tickfont = dict(
                size = 12),
            ),
        xaxis = dict(
            tickfont = dict(
                size = 12)
            ),        
        title = dict(
            text = title,
            x = 0.05+title_shift_x,
            xanchor = xanchor,
            y = 0.99+title_shift_y,
            font = dict(
                size = 14)
            ),
        margin=dict(
            l=40,
            r=20,
            b=120-bottomshift,
            t=30+margin_up_shift,
            ),
        )
    
    if info_text != None: 
        info_add = "<br>"+info_text 
    else: 
        info_add = ""

    fig.update_layout(barmode="stack")


    fig.add_annotation(dict(
        font=dict(size=7),
        x=1,
        y=-0.06,
        showarrow=False,
        text=("Data source: " +source_text+info_add + "<br>"
              "Austria Transition Tracker | Chart by B.Thaler | "
            "<a href = \"https://creativecommons.org/licenses/by/4.0/\">CC BY 4.0</a>"),
        xanchor='right',
        yanchor = "top",
        xref="paper",
        yref="paper",
        align = "right"))

    
    
    """ show and save plot """
    if show_plot: fig.show(renderer = "browser")     
    if save: save_figure(filename, title, unit, data_plot, plot_type, time_res,
                         unit_fac=unit_fac, source_text=source_text,
                         info_text=info_text, initial_visible=None)
    



def plot_with_toggle(title="",
                   unit="",
                   data_plot={},
                   filename="",
                   show_plot=False,
                   unit_fac=1,
                   colors=None,
                   time_res="monthly",
                   legend_inside = True,
                   source_text=None,
                   info_text=None,
                   plotmax_fac=1.1,
                   save=True,
                   plot_type = "toggle",
                   initial_visible = "area"):

    if source_text is None:
        source_text = "eurostat (%s)" % (data_plot["meta"]["code"])
    
    if colors is None:
        colors = px.colors.qualitative.Dark2.copy()
        colors.remove('rgb(231,41,138)')  # removes pink
        colors[3], colors[4] = colors[4], colors[3]  # swap two colors
    
    if time_res == "monthly":
        hovertemplate = '%{x|%b-%Y}: %{y:.2f}'
    elif time_res == "yearly":
        hovertemplate = '%{x|%Y}: %{y:.2f}'
    
    fig = go.Figure()
    # Precompute ymax for each plot type
    ymax_line = 0
    ymax_area = 0
    ymax_bar = 0
    
    color_ind = 0
    sum_data = None
    
    for data in data_plot["data"]:
        y_data = np.array(data_plot["data"][data]["y"]) / unit_fac
        ymax_line = max(ymax_line, max(y_data))
    
        if sum_data is None:
            sum_data = y_data
        else:
            if len(sum_data) > len(y_data): 
                sum_data = sum_data[:len(y_data)] + y_data 
            elif len(sum_data) < len(y_data): 
                sum_data += y_data[:len(sum_data)]
            else: 
                sum_data += y_data
    
    ymax_area = sum_data * plotmax_fac
    
    # for data in data_plot["data"]:
    #     y_data = np.array(data_plot["data"][data]["y"]) / unit_fac
    #     ymax_area = max(max(y_data), ymax_area)
    
    # ymax_area = ymax_area * plotmax_fac
    ymax_bar = ymax_area  # Same as area for stacked bar charts
    
    # Add traces for each chart type
    for data in data_plot["data"]:
        y_data = np.array(data_plot["data"][data]["y"]) / unit_fac
        color = colors[color_ind % len(colors)]
    
        # Area traces
        if data in ["Total", "Domestic consumption"]: 
            visible = {0: "area",
                        1: "bar",
                        2: "line"}
            for k in range(3): 
                fig.add_trace(
                    go.Scatter(x = data_plot["data"][data]["x"], 
                                y = np.array(data_plot["data"][data]["y"])/unit_fac,
                                mode='lines',
                                name = data,
                                customdata = y_data,
                                legendgroup = data,
                                xhoverformat = "<b>%Y<b>",
                                visible = initial_visible == visible[k],
                                line = dict(color = [color[1] for color in greys if color[0] == 0.875][0]),
                                hovertemplate = hovertemplate))
            ymax_area -= max(np.array(data_plot["data"][data]["y"])/unit_fac)
            ymax_bar -= max(np.array(data_plot["data"][data]["y"])/unit_fac)

        else: 
            
            # Line traces
            fig.add_trace(
                go.Scatter(
                    x=data_plot["data"][data]["x"],
                    y=y_data,
                    mode="lines",
                    name=f"{data}",
                    line=dict(color=color),
                    visible = initial_visible == "line",
                    hovertemplate = hovertemplate
                )
            )
            
            fig.add_trace(
                go.Scatter(
                    x=data_plot["data"][data]["x"],
                    y=y_data,
                    stackgroup="one",
                    name=f"{data}",
                    line=dict(color=color),
                    fill="tonexty",
                    fillcolor=color.replace("rgb", "rgba").replace(")", ",0.6)"),
                    visible = initial_visible == "area",
                    hovertemplate = hovertemplate,
                )
            )
        
            # Bar traces
            fig.add_trace(
                go.Bar(
                    x=data_plot["data"][data]["x"],
                    y=y_data,
                    name=f"{data}",
                    marker_color=color,
                    customdata = y_data,
                    visible = initial_visible == "bar",
                    hovertemplate = hovertemplate
                                    )
            )
    
        color_ind += 1
    
      
    # Add buttons for toggling chart types
    fig.update_layout(
        updatemenus=[
            go.layout.Updatemenu(
                type="buttons",
                direction="down",
                xanchor = "left",
                font=dict(size=9),  # Smaller font size
                pad=dict(l=1, r=1, t=1, b=1),  # Reduce padding
                x=1.01,  # Position outside the plot
                y=1,
                buttons = [
                    dict(
                        label="Line",
                        method="update",
                        args=[
                            {"visible": [True, False, False] * len(data_plot["data"])},
                            {"yaxis": {
                                "range": [0, ymax_line * plotmax_fac],
                                "title": {"text": unit, "font": {"size": 12}},  # Correctly setting the title font
                                "tickfont": {"size": 12}  # Correctly setting the tick font
                            }},
                        ],
                    ),
                    dict(
                        label="Area",
                        method="update",
                        args=[
                            {"visible": [False, True, False] * len(data_plot["data"])},
                            {"yaxis": {
                                "range": [0, ymax_area * plotmax_fac],
                                "title": {"text": unit, "font": {"size": 12}},  # Apply the same font settings
                                "tickfont": {"size": 12}
                            }},
                        ],
                    ),
                    dict(
                        label="Bar",
                        method="update",
                        args=[
                            {"visible": [False, False, True] * len(data_plot["data"])},
                            {"yaxis": {
                                "range": [0, ymax_bar * plotmax_fac],
                                "title": {"text": unit, "font": {"size": 12}},  # Apply the same font settings
                                "tickfont": {"size": 12}
                            }},
                        ],
    ),
],
            )
        ]
    )
    
    # Update layout for stacked bar mode and initial state
    fig.update_layout(barmode="stack", yaxis_range=[0, ymax_area])
        
    if legend_inside: 
        legend_dict= dict(
            yanchor="bottom",
            y=0.01,
            xanchor="left",
            x=0.01)
        bottomshift = 0 
    else: 
        legend_dict=dict(
            yanchor="top",
            y=-0.07,
            xanchor="left",
            x=0.01)
        bottomshift = 100
    
    
    ### reduce spacing between legend groups 
    fig.update_layout(legend_tracegroupgap=0)
    
    title_shift_x = 0
    title_shift_y = 0
    margin_up_shift = 0
    xanchor = "left"

    
    fig.update_layout(
        yaxis_title= unit,
        autosize = True,
        legend=legend_dict,
        yaxis = dict(
            # autorange = True,
            tickfont = dict(
                size = 12),
            ),
        xaxis = dict(
            # autorange = True,
            tickfont = dict(
                size = 12)
            ),        
        title = dict(
            text = title,
            x = 0.05+title_shift_x,
            xanchor = xanchor,
            y = 0.99+title_shift_y,
            font = dict(
                size = 14)
            ),
        margin=dict(
            l=40,
            r=20,
            b=120-bottomshift,
            t=30+margin_up_shift,
            ),
        )
    
    

    
    if info_text != None: 
        info_add = "<br>"+info_text 
    else: 
        info_add = ""

    fig.add_annotation(dict(
        font=dict(size=7),
        x=1,
        y=-0.06,
        showarrow=False,
        text=("Data source: " +source_text+info_add + "<br>"
              "Austria Transition Tracker | Chart by B.Thaler | "
            "<a href = \"https://creativecommons.org/licenses/by/4.0/\">CC BY 4.0</a>"),
        xanchor='right',
        yanchor = "top",
        xref="paper",
        yref="paper",
        align = "right"))      

    if show_plot: fig.show(renderer = "browser")
    if save: save_figure(filename, title, unit, data_plot, plot_type, time_res,
                         unit_fac=unit_fac, source_text=source_text,
                         info_text=info_text, initial_visible=initial_visible)
    



def save_figure(filename, title, unit, data_plot, plot_type, time_res,
                unit_fac=1, source_text=None, info_text=None, initial_visible=None):
    """Hand the chart to the manifest. No HTML: the frontend renders from data.

    This used to also write a complete standalone Plotly document per chart into
    docs/_includes/ -- 4.3 MB of generated HTML that Jekyll then inlined into a
    page, producing nested HTML documents -- and then patch two modebar buttons
    into it by reading the file back and splitting a line on the literal
    "zoom2d". Both the second copy of every data point and the string surgery
    are gone; the toggle, legend and download buttons are frontend behaviour now.
    """
    # area_button was an undocumented sixth plot_type whose data_plot is nested
    # one level deeper: a chart with a dataset selector. Named for what it is.
    if plot_type == "area_button":
        plot_type = "groups"

    page, section, order = pages.lookup(manifest.chart_id(filename))
    return manifest.register(
        filename=filename,
        title=title,
        unit=unit,
        data_plot=data_plot,
        plot_type=plot_type,
        time_res=time_res,
        unit_fac=unit_fac,
        source_text=source_text,
        info_text=info_text,
        initial_visible=initial_visible,
        page=page,
        section=section,
        order=order,
    )
