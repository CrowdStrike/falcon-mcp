# Field Interactions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-field-interactions.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

Content was updated:Feb 19, 2025

## Field Interactions

LogScale UI offers contextual menus for various interactions with fields. What interactions are supported depends on the [Field Data Types](searching-data-types.html "Field Data Types") of the selected field. 

To access these menus: 

  1. Locate the ⋮ icon next to a field in any of these areas: 

     * [Results panel](searching-data-changing-the-events-display.html "Display Results and Events")

     * [Fields panel](searching-data-displaying-fields.html "Display Fields")

     * [Inspection panel](searching-data-inspecting-events.html "Inspect Events")

  2. Click the ⋮ icon to open the contextual menu. In the example screenshot below, the field interaction menu is opened from the [Results panel](searching-data-changing-the-events-display.html "Display Results and Events"): 




![Screenshot showing the field interaction options](images/search-data/drilldown-menu.png)  
---  
  
**Figure 95. Field Interactions**

  


Available interactions are: 

  * Copy — copies the value or the field's name, which you can paste in the Query editor. It works in any field interaction within the Fields panel and Inspection panel. It also works in the [Event list](searching-data-changing-the-events-display.html "Display Results and Events") when the data type is JSON or Log line. 

You can copy the field in different formats: 

    * Field name copies the field's name. Click inside a nested field in a JSON structure and copy the field name — the whole path will be copied into the field and this corresponds to the field inside LogScale. 

    * Value copies the field's value. 

    * Value as escaped string escapes the string in LogScale format, ready to paste it directly into any query. This can be useful in case of special characters that need escaping; the same applies for the field name — if they include special characters, they are also going to be escaped. 

    * Value as regex copies the field's value as a regular expression. 

  * Add as column — adds the selected field as a column. The size of the column fits the name of the field or the content of that field, whichever is largest. 




Additional interactions are available on both value fields and name fields. These are: 

  * Aggregate — enables two aggregate options: 

    * Find top 10 values

    * Group by value

  * Array — allows filtering based on array values on any position of the array, using the [`array:contains()`](functions-array-contains.html "array:contains\(\)") query function to query data. It only shows for JSON array fields. Two options are available: 

    * Contains value filters events by requiring a string value to be present in the array. For example, given a list of users with different access permissions in the Event List, it is possible to filter for any user who has WRITE permissions, independent on where the WRITE value is in the array. The following query is applied when this interaction is selected: 

logscale
          
          array:contains("user.permissions[]", value=WRITE)

    * Does not contain value allows for inverted filters, meaning it filters events by requiring a string value that is not present in the array. For example, given a list of users with different access permissions in the [Event List](searching-data-changing-the-events-display.html "Display Results and Events"), it is possible to filter any user who does not have WRITE permissions. The following query applies when using this interaction: 

logscale
          
          not array:contains("user.permissions[]", value=WRITE)

### Note

Because [`array:contains()`](functions-array-contains.html "array:contains\(\)") checks for a single value at the time, you must run multiple Array interactions, if you wish to filter on multiple values in the array. 

  * Filter — used to filter out or keep items, can be done on the value or on the field name. Filter interaction options include: 

    * Match value allows including events that match the selected value. 

    * Match value (Regex) guides you to how to apply a regex to a field using the literal syntax. 

    * Exclude value allows excluding events that have the selected value. 

    * Has field allows including events with the selected field. 

    * Does not have field allows excluding events without the selected field. 

  * IP — available on fields that contain IP addresses, such as actor.ip . This option allows for filtering IP values by appending specific query functions. IP interaction options include: 

    * IP location generates a new query using the [`ipLocation()`](functions-iplocation.html "ipLocation\(\)") function. The new query uses the name of the selected IP field as the [_`field`_](functions-iplocation.html#query-functions-iplocation-field) argument. 

    * Worldmap generates a new query using the [`worldMap()`](functions-worldmap.html "worldMap\(\)") query function. The new query uses the name of the selected IP field as the [_`ip`_](functions-worldmap.html#query-functions-worldmap-ip) argument. 

    * IOC Lookup generates a new query using the [`ioc:lookup()`](functions-ioc-lookup.html "ioc:lookup\(\)") query function. The new query uses the name of the selected IP field as the [_`field`_](functions-ioc-lookup.html#query-functions-ioc-lookup-field) argument. Click and IP field, say ip_address, to generate a new query in the Query editor, like this: 

logscale
          
          ioc:lookup(field=[actor.ip], type="ip_address", confidenceThreshold="unverified", strict=true)

  * Number — available on fields where a number is detected. The options Max, Min, Avg and Sum apply these aggregates to the field. 

### Note

Numbers that exceed the range of safe integers in Javascript are replaced in JSON by reading the associated LogScale value directly. This is to avoid that incorrect numbers are displayed. These replaced numbers are highlighted in JSON data to indicate that they might be wrong. For more information, see [Troubleshooting: **UI Warning: The actual value is different from what is displayed**](https://library.humio.com/kb/kb-bignumbers.html). 

  * Parse — available on fields that have JSON, URL and Timestamps content, it parses the field as a LogScale field. This is possible because LogScale is able to detect the type of each field. This detection enables specific interaction options for different field types. For example: 

    * When LogScale detects a JSON string in a field, it displays the Parse → JSON option in the menu. 

    * When LogScale detects a URL in a field, it displays the Parse → URL option in the menu. This option splits the URL into its component parts. 

  * Timechart — field interaction options include: 

    * Use field as series generates a [`Time Chart`](widgets-timechart.html "Time Chart") with individual series for each value in the selected field. 

    * Count occurrences gives the number of occurrences for the field. 

    * Max value and Percentiles are available on number fields only — for example, when LogScale detects a number, it will generate a [`timeChart()`](functions-timechart.html "timeChart\(\)") percentile query. 




When you hover over one of the available options under Timechart, you will get a tooltip describing the query update. In the following example, the option selected appends [`timeChart()`](functions-timechart.html "timeChart\(\)") to the query, for the #repo field. 

![Screenshot showing a query update tooltip when selecting a field interaction](images/search-data/query-update-tooltip.png)  
---  
  
**Figure 96. Query Update Tooltip**

  


### Tip

Use **SHIFT** +**click** to add the suggested option to the query string without running a new search.
