# Look Up Events | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-lookup-events.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

Content was updated:Jun 18, 2025

## Look Up Events

The [`Search`](searching-data.html "Search Data") page supports event interactions in [`Table`](widgets-table.html "Table") widgets when results contain [@id](searching-data-event-fields.html#searching-data-event-fields-metadata-id) fields. Use this option to look for specific events through their IDs. 

To look up an event ID: 

  1. Under the [Results](searching-data-changing-the-events-display.html "Display Results and Events") tab, locate a row in the table 

  2. Click the ⋮ icon for that row 

![Lookup Events row interaction](images/search-data/lookup-events.png)  
---  
  
**Figure 86. Lookup Events**

  

  3. The [`Search`](searching-data.html "Search Data") page opens and displays a query in this format: 

logscale Syntax
         
         in(@id, values=[idnumber])

The query will look for details on that specific event by returning the [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field in the results. 




As a related feature, the [`Table`](widgets-table.html "Table") widget also supports timestamp visualization when looking up events. When the table results include [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) fields, hovering over a table row highlights with a blue bar the corresponding time period in the histogram: 

**Figure 87. Timestamp Highlight**
