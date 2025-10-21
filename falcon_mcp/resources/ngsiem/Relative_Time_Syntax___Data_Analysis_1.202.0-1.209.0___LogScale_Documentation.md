# Relative Time Syntax | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/syntax-time-relative.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Language Syntax](syntax.html)

/ [Time Syntax](syntax-time.html)

### Relative Time Syntax

The documentation explains how to use relative time syntax in LogScale for specifying time intervals and durations, including basic time units (from milliseconds to years), calendar-based units, and advanced anchoring capabilities. The syntax can be used for query time ranges and bucket definitions, with detailed examples showing how to express time periods like "2 hours ago" or "start of last quarter," though some limitations apply for live queries and scheduled searches. 

Relative time syntax allows you to specify a time interval as a duration relative to a specific endpoint, typically the current moment ("now"). This syntax is versatile and can be used in various parts of the platform, including: 

  * Specifying the time range for a query using the UI or API. 

  * Defining the length of the span for buckets when using functions like [`timeChart()`](functions-timechart.html "timeChart\(\)") or [`bucket()`](functions-bucket.html "bucket\(\)"). 




To make specifying a time more flexible, LogScale supports a relative time syntax. This lets you express a simple time duration, rather than specifying two absolute times. 

You specify a relative time modifier as a number followed by a word. The following table shows which words you can use: 

Time Unit |  Accepted Values |  Notes   
---|---|---  
Milliseconds |  `millisecond`, `milliseconds`, `millis`, `ms` |   
Seconds |  `second`, `seconds`, `s`, `sec`, `secs` |   
Minutes |  `minute`, `minutes`, `m`, `min` |   
Hours |  `hour`, `hours`, `h`, `hr`, `hrs` |   
Days |  `day`, `days`, `d` |  Interpreted as 24h in milliseconds   
Weeks |  `week`, `weeks`, `w` |  Interpreted as 7 days in milliseconds   
Months |  `month`, `months`, `mon` |  Interpreted as 30 days in milliseconds   
Quarters |  `quarter`, `quarters`, `q`, `qtr`, `qtrs` |  Interpreted as 90 days in milliseconds   
Years |  `year`, `years`, `y`, `yr`, `yrs` |  Interpreted as 365 days in milliseconds   
  
You can include a space character between the number and the unit of time. 

#### Relative Time Syntax Examples

Two hours: 

logscale Syntax
    
    
    2h

Two hours: 

logscale Syntax
    
    
    2 hours

Three weeks: 

logscale Syntax
    
    
    3 weeks

Ten seconds: 

logscale Syntax
    
    
    10s

Ten seconds: 

logscale Syntax
    
    
    10seconds

#### Advanced Time Syntax

LogScale supports two additional relative time syntax structures: 

  * [Calendar-Based Units](syntax-time-relative.html#syntax-time-relative-advanced-calendar "Calendar-Based Units") enables you to specify a time relative to the calendar. For example, specifying a time, days or months, in the past relative to the current time. 

  * [Anchoring to Specific Time Units](syntax-time-relative.html#syntax-time-relative-advanced-anchor "Anchoring to Specific Time Units") enables you to specify a point in time to use as the 'anchor' point for relative time declarations. For example, setting the anchor point to the beginning of the week, and then specifying the time relative to that anchor. 




##### Calendar-Based Units

The default interpretation of time units is fixed-duration in milliseconds. However, you can change this to a calendar-based interpretation by adding the `calendar:` prefix to the entire time string. Example: 

  * **Current Date** : May 24th 

  * **Syntax** : `calendar: 2months`

  * **Result** : March 24th (two calendar months back) 




Without the `calendar:` prefix, `2months` would be interpreted as 60 days (2 * 30 days), resulting in March 25th. 

##### Anchoring to Specific Time Units

Relative time syntax also supports anchoring (or snapping) to a specific time unit, allowing you to define specific points in time, such as `yesterday`, `week to date` or `last quarter`. Anchoring is indicated by the `@` (at) symbol in the syntax. For example: `1d@d+12h`, will be interpreted as `yesterday at 12PM`. 

For a detailed interpretation of this example, assuming that the current time is **August 14th, 1 PM (13:00)** , the anchor specification `1d@d+12h`: 

  * Go back 24 hours (to August 13th, 1 PM) (`1d`) 

  * Anchor to the beginning of the day (August 13th, 00:00) (`@d`) 

  * Add 12 hours, resulting in August 13th, 12 PM (interpreted as "yesterday at 12 PM") (`+12h`) 




###### Anchored Time Points - Syntax

The general form of an anchored time point is: 

logscale Syntax
    
    
    calendar:base offset@anchor unit _anchor offsets_

Where: 

  * `calendar:` (Optional) — Prefix for calendar-based interpretation. 

  * Base Offset: A relative offset, `_`number`_**`time unit`**` (for example, `30min` or `1year`). 

  * Anchor Unit Specifies the time unit to snap to (for example, `@d` for the start of the day). 

  * Anchor Offsets: A sequence of additional relative offsets, separated by `+` or `-` (for example, `+24h-30min`). 




The syntax is intepreted as follows: 

Given a point in time `t` (representing the current date and time): 

  1. Base Offset — Go back the duration specified by the base offset relative to `t`. 

  2. Anchor Unit — Snap to the specified anchor unit. For example, `...@d` would snap to the beginning of the day. 

  3. Anchor Offsets — Apply any additional offsets. For example, `...@...+24h-30min` means "go forward 24 hours, then back 30 minutes." 




When using both calendar-based units and anchoring, the time zone specified in the query is applied. 

LogScale applies different default time zones depending on how you submit the query: 

  * Query submitted via API: applies Coordinated Universal Time (UTC) if you do not specify a time zone. 

  * Query submitted via UI: applies the time zone you select in the [time zone dropdown field](searching-data-set-timezone.html#searching-data-set-timezone-temporarily "Changing the Time Zone Temporarily"). 




###### Important Limitations

The following limitations apply for anchored relative time syntax: 

  * Unsupported in live queries and scheduled searches: 

Calendar-based time units and anchoring are not supported in these scenarios. 

  * Unsupported for span length in [`timeChart()`](functions-timechart.html "timeChart\(\)") and [`bucket()`](functions-bucket.html "bucket\(\)") functions: 

You cannot use calendar-based time units and anchoring to define the span length in these functions. 




###### Calendar-based Units and Anchoring Examples

Example |  Interpretation |  Notes   
---|---|---  
`now@d` |  Start of today (00:00:00 at the current date) |   
`now@w` |  Monday this week |   
`calendar: 1d@d` |  Yesterday at 00:00:00 |  calendar: 1d@d allows to account for Daylight Saving Time change, unlike 1d@d which can produce results shifted by 1 hour because 1d means 24h.   
`calendar: 2months` |  The same day, two months ago. For example: If `now=May 27 2024 11:28:29` then result is March 27 2024 11:28:29 |  This is not equivalent to 2months because 1month (without calendar prefix) is defined as 30 days.   
`now@quarter` |  Start of the current quarter |   
`6h@h+30min` |  The 30th minute of the hour, 6 hours ago |  Adding `calendar: ` to this example has no effect because the units (hours, minutes) are not date-based.   
  
#### Regular Expression

This regular expression describes the format: 

logscale Syntax
    
    
    ^(\d+) ?(years?
    | y
    | yrs?
    | quarters?
    | q
    | qtrs?
    | months?
    | mon
    | weeks?
    | w
    | days?
    | d
    | hours?
    | hr?
    | hrs
    | minutes?
    | m
    | min
    | seconds?
    | s
    | secs?
    | milliseconds?
    | millis
    | ms)$
