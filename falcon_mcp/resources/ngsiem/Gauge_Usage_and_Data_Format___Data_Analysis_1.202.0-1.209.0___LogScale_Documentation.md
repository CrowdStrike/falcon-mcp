# Gauge Usage and Data Format | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/widgets-gauge-usage-data.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Data Visualization](data-visualization.html)

/ [Widgets](widgets.html)

/ [Gauge](widgets-gauge.html)

### Gauge Usage and Data Format

The [`Gauge`](widgets-gauge.html#summary_widgets-gauge) widget is used for providing context, example use cases include: 

  * Show errors per day and indicate whether values are approaching critical levels 

  * Represent the progress of vulnerability assessment and remediation efforts 

  * Monitor system resource utilization, like CPU or memory utilization. 




You can customize your widget by changing its values range and formatting. Two representation types of the value are available: 

  * Needle representation, which mimics the traditional analog gauges such as speedometers. 

  * Filler representation, which provides a dynamic option to fill a segment of the gauge based on the current value. 




These are just two of the possible settings you can use to customize your [`Gauge`](widgets-gauge.html#summary_widgets-gauge) chart. For a complete list of configurable properties, refer to [Gauge Property Reference](widgets-gauge-properties.html "Gauge Property Reference"). 

For examples of possible widget layouts and creation instructions, refer to [Gauge Examples Gallery](widgets-gauge-howto.html "Gauge Examples Gallery"). 

For results based on grouping on a single field, the widget also supports data visualization in multiple charts arranged in a grid, allowing them to be easily compared, see [Display Small Multiple Charts](widgets-gauge-howto-multiple.html "Display Small Multiple Charts"). 

The [`Gauge`](widgets-gauge.html#summary_widgets-gauge) widget uses a numeric scale, hence it is compatible with query functions that output a single numeric field such as [`sum()`](functions-sum.html "sum\(\)"), [`count()`](functions-count.html "count\(\)"), or [`avg()`](functions-avg.html "avg\(\)") that is, functions that produce a single row with a single field (like _sum). 

For visualizing text values instead, see [Single Value](widgets-single-value.html "Single Value").
