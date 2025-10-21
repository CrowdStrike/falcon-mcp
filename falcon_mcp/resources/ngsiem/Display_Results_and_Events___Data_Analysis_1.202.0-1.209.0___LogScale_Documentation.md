# Display Results and Events | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-changing-the-events-display.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

Content was updated:Jun 10, 2025

## Display Results and Events

LogScale presents the data returned from a search in a list format. By default, this list includes the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) and [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) columns, plus any columns selected in the [Fields panel](searching-data-displaying-fields.html "Display Fields"). 

### Display tabs

Depending on the contents and functions used in the query, different tabs for displaying output data appear based on the query, for example if the query includes [Aggregate Query Functions](functions-aggregate.html "Aggregate Query Functions"). Available tabs are: 

  * **[Results](searching-data-changing-the-events-display.html "Display Results and Events") tab**

Sometimes also referred to as the [Event list](searching-data-changing-the-events-display.html "Display Results and Events") that displays the results of a query, presents the final results from the query once all of the elements of the source query including filters and aggregations (for example using [`groupBy()`](functions-groupby.html "groupBy\(\)")) have been completed. 

![](images/ui/search-results-tab.png)  
---  
  
Different forms of the [Results](searching-data-changing-the-events-display.html "Display Results and Events") tab may be available in different contexts: 

    * **[Results](searching-data-changing-the-events-display.html "Display Results and Events") tab grouped by prefix**

When using a query prefix, for example with the [`correlate()`](functions-correlate.html "correlate\(\)") function, the results will be shown grouped by the name of the prefix query. When grouping in this format, each result is set for a given [`correlate()`](functions-correlate.html "correlate\(\)") query. 

For example: 

![](images/ui/search-results-tab-named-prefix.png)  
---  
  
    * **Named Prefix[ Events](searching-data-changing-the-events-display.html "Display Results and Events") tabs**

For version 1.197.0 and above

When using [`correlate()`](functions-correlate.html "correlate\(\)"), matching event sets for each named query are available as separate tabs, one per prefix used within the [`correlate()`](functions-correlate.html "correlate\(\)") function. Each event tab will contain the events matching each named query in the [`correlate()`](functions-correlate.html "correlate\(\)") definition, including the raw event data after matches and filtering, but before aggregation. When grouping in this format, each result is set for a given [`correlate()`](functions-correlate.html "correlate\(\)") query. 

For example, the [`correlate()`](functions-correlate.html "correlate\(\)") function in this query has two named queries, `machineCheck` and `hardwareError` which each have a tab of matching results: 

![](images/ui/search-results-tab-named-events.png)  
---  
  
  * **[Events](searching-data-changing-the-events-display.html "Display Results and Events") tab**

For queries without a prefix, the [Events](searching-data-changing-the-events-display.html "Display Results and Events") tab includes the raw event data after matches and filtering, but before aggregation. 

![](images/ui/search-events-tab.png)  
---  
  
  * **Table tab**

Appears for each table defined by [`defineTable()`](functions-definetable.html "defineTable\(\)"), when this function is used in the source query. The display of matching entries for the table is limited to the first 500 rows. For more information, see [How to Use Ad-hoc Tables in Queries](query-joins-methods-adhoc-tables.html#query-joins-methods-adhoc-tables-query "How to Use Ad-hoc Tables in Queries"). 

![](images/ui/search-table-tab.png)  
---  
  
  * ** Query graph tab**

Appears when the [`correlate()`](functions-correlate.html "correlate\(\)") function is used in the source query, to provide a graphical representation of two correlated events. The graph helps users author complex queries using [`correlate()`](functions-correlate.html "correlate\(\)"), as it displays the structure of the query including correlation query nodes and links that represent the relationship between event fields. For more information, see [`correlate()`](functions-correlate.html "correlate\(\)"). 

![](images/ui/search-graph-tab.png)  
---  
  



### Display options

You can change the way events are displayed from the toolbar above the [Event list](searching-data-changing-the-events-display.html "Display Results and Events"): 

![Screenshot showing the toolbar for setting how to display events](images/search-data/events-display.png)  
---  
  
**Figure 82. Results Tab and Display Modes**

  


Display options are (left to right in the toolbar): 

  * **Filter match highlighting** allows highlighting results based on the filters applied in queries. See [Highlight Filter Match](searching-data-filter-highlighting.html "Filter Match Highlighting") for more information. 

  * **Scroll to selected event** makes it possible to scroll fields starting from a selected event. 

  * **Text wrapping** is used to wrap lines or truncate fields after the first line. 

  * **Sort events** changes the order of fields in the event. You can choose whether newest events appear at the bottom or top of the list. 

  * **Hide event distribution chart** allows hiding the event histogram to get more space when looking at data. 

  * **Toggle fullscreen** displays events in full-screen mode.
