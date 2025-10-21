# Change the Time Interval | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-expand-timeframe.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

## Change the Time Interval

The time range of the query can be set in the UI. It is strongly recommended to limit the time range of queries as much as possible. This ensures that LogScale is searching the relevant data to the information required, improving efficiency and reducing unnecessary data processing. 

![Screenshot showing the Time Interval dialog](images/search-data/search-time-frame.png)  
---  
  
**Figure 103. Query Time Selector**

  


Elements of the time range include: 

  * Time zone picker to set a temporary time zone for your search. This setting will influence how time ranges using calendar definitions such as fixed time range and intervals like `today` or last month and calculate the query's start and end timestamps. For more information on setting the time zone, see [Set Time Zone](searching-data-set-timezone.html "Set the Time Zone"). 

  * Time Selector to specify the time range for the query. 

    * Use the navigation arrows < and > to move the time interval earlier or later. 

    * Use the magnifiericon to to quickly extend the time range by the same interval (for example, from 5 min to 10 min ago), making it easy to expand your search scope incrementally. 

  * Live  checkbox. LogScale offers two modes for running queries: live and static. 

    * Live queries are ideal for monitoring scenarios where you need to observe the data as it arrives. 

      * These queries use a time interval relative to the current moment (for example, last 5 minutes, last 1 day). 

      * When enabled, results will update as soon as new data becomes available. 

      * Time intervals that use anchoring (for example: today, yesterday) are not supported in live queries. 

    * Static queries are better suited for investigating past events. 

      * All time interval definitions are supported in this mode. 




Available time intervals: 

  * Presets enables quick selection from commonly used time intervals. 

    * Use case: ideal for frequent searches, allowing you to select standard time ranges, like `last 24 hours` or `last 7 days` with a single click. 

  * Relative Time Range allows selecting a relative time range. 

    * The Simple tab provides flexible adjustment of the start of the time interval, with the most common units like days, hours, minutes etc. The time interval is always relative to Now. 

    * ![Screenshot showing the advanced time selection](images/search-data/time-selector-advanced.png)  
---  
  
The Advanced tab provides a fully customizable approach to the specified time range: 

      * You can set the relative time ranges that end in the past. For example, you might want to analyze the last 24 hours of data but exclude the most recent hour to account for data delays. 

      * You can specify [calendar-based intervals](syntax-time-relative.html#syntax-time-relative-advanced-calendar "Calendar-Based Units"), such as the last three calendar months, rather then fixed intervals like 90 days. Specifying the calendar-based time ranges requires using the [anchoring syntax](syntax-time-relative.html#syntax-time-relative-advanced-anchor "Anchoring to Specific Time Units"). 

The Advanced tab utilizes LogScale relative time syntax. 

      * The **`@`** symbol allows snapping time intervals to a specific point, like the beginning of the day or month. Whatever follows **`@`** is treated as the anchor point. You can use specific time syntax, or a function such as **`@month-1ms`** which means "beginning of the month, minus 1 millisecond". 

      * The **`calendar:`** keyword interprets time ranges using calendar terms (for example, months are defined by the calendar rather than fixed 30-day period). 

For more information on using advanced relative time selectors, see [Advanced Time Syntax](syntax-time-relative.html#syntax-time-relative-advanced "Advanced Time Syntax"). 

  * Fixed Time Range allows selecting fixed start and end dates as the time interval. 




Additional features include: 

  * Time intervals can be copied and pasted between search session using the Copy and Paste icons available from the Time Selector. 

![](images/search-data/time-selector-copypaste.png)  
---  
  
  * The [Time field](searching-data-expand-timeframe.html#searching-data-expand-timeframe-time-field) selection controls which time field ([@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) or [@ingesttimestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-ingesttimestamp)) is used when evaluating the time range for a query. By default, [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) is used. 

For example, use [@ingesttimestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-ingesttimestamp) when validating an [Aggregate Alert](automated-alerts.html#trigger_types-alerts-aggregate) query, see [Select alert timestamp](https://library.humio.com/data-analysis-1.177/automated-alerts-editing-new-properties.html#automated-alerts-editing-new-properties-timestamp) for more information. 




### Note

The following specific behaviors exist when using the time interval selection: 

  * Live mode is only available when using relative time ranges. 

  * When you change the timetable from the **Time dropdown** , the liveness of the query is not impacted unless you enable the Live checkbox in order to run it as a live query instead, while the timeframe previously selected is kept. 

  * When you disable the Live checkbox, the query running will be stopped. 

  * The query on the Search page also stops if you change to a relative or fixed time while it is running. Press **Enter** or click Run in the query editor to make it run again. 




### Warning

The Time Selector becomes ineffective when a query includes the [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") function. This means that the panel will display the time specified in the query, along with a Custom time label: 

![](images/search-data/custom-time.png)  
---  
  
The [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") function also prevents zooming in on the events distribution chart.
