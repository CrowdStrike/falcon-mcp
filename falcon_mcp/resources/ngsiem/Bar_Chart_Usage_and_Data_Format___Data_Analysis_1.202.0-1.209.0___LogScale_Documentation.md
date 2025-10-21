# Bar Chart Usage and Data Format | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/widgets-barchart-data-mapping.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Data Visualization](data-visualization.html)

/ [Widgets](widgets.html)

/ [Bar Chart](widgets-barchart.html)

### Bar Chart Usage and Data Format

Bar charts can be of two types: 

  * **Single series**. Displays one data series with individual bars representing single values. 

  * **Multiple series**. Displays one or more metrics per category, or one metric broken down by two dimensions. For example, by severity and vendor name. 




The following example use cases and variations apply. 

Bar Chart Type |  Description |  Use Case |  Example   
---|---|---|---  
Single Series Bar Chart |  Displays one data series with individual bars representing single values |  Ideal for comparing single metrics across categories |  Compare the number of detection events across different severity levels (Critical, High, Medium, Low). See [Event Detection Across Severity Levels](widgets-barchart-howto-severity-levels.html "Event Detection Across Severity Levels").   
Multiple Series - Grouped Bars |  Shows multiple data series side by side for each category |  Compare multiple related sub-categories simultaneously |  Compare failed and successful authentication attempts by department. See [Failed and Successful Authentication Attempts](widgets-barchart-howto-authentication-attempts.html "Failed and Successful Authentication Attempts").   
Multiple Series - Stacked Bars |  Bars are stacked on top of each other, showing both individual values (and their relation to totals) and totals |  Display component parts of a whole while maintaining visibility of total values |  Visualize threat types (Malware, Ransomware, Phishing) distribution within each time period. See [Threat Type Distribution](widgets-barchart-howto-threat-distribution.html "Threat Type Distribution").   
Multiple Series - 100% Stacked Bars |  Similar to stacked bars but normalized to 100% to show proportion to total |  Focus on proportional distribution rather than absolute values |  Show the relative proportion of different alert types within each detection source. See [Alert Type Proportion in Detection Sources](widgets-barchart-howto-alert-and-detection-sources.html "Alert Type Proportion in Detection Sources").   
Bar Chart with [Line Overlay](widgets-barchart-properties.html#line-overlay) |  Combines the chart with a line series to show related but different metrics |  Compare volume metrics against trend indicators or averages |  Display daily detection counts as bars with a line showing the 7-day moving average of detection severity. See [Daily Detection Counts with Detection Severity Average](widgets-barchart-howto-daily-detection-counts.html "Daily Detection Counts with Detection Severity Average").   
  
The [`Bar Chart`](widgets-barchart.html "Bar Chart") widget maps data fields based on the query result as the default behavior. This behavior can be overwritten by manually mapping from fields in the query result to visual properties, using the [Data Mapping](widgets-barchart-properties.html#data-mapping) property. For example, the default mapping assigns the first field from a [`groupBy()`](functions-groupby.html "groupBy\(\)") query to the category axis. When multiple fields define the category axis, the chart creates a category for each unique value combination. 

The [Series definition](widgets-barchart-properties.html#series-definition) property configures the chart to create multiple series from a single data table, with the following options: 

  * With the default `Auto` mode, the chart interprets query results to select either `Fields` mode or `Field values` mode. 

  * The chart activates `Field values` mode when the query contains multiple group fields, as in [`groupBy([a,b])`](functions-groupby.html "groupBy\(\)"). 

  * In all other cases, the chart operates on `Fields` mode. 




In `Field values` mode, the chart creates a series name for the unique value of a field column. A secondary column determines the series values. When multiple fields define the series names, the chart creates a series for each unique value combination. Example: 

![Bar Chart Selecting Fields Mode View](images/dashboards/widgets/long-format-tableview.png)  
---  
  
**Figure 199. Field Values Mode View**

  


In `Fields` mode, the chart creates a series from each field column. The field name (column header) becomes the series name, and the corresponding field values (cell values) become the series values. Example: 

![Bar Chart Selecting Fields Mode](images/dashboards/widgets/bar-chart-wide.png)  
---  
  
**Figure 200. Fields Mode View**
