# Show Events in Context | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-show-context.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

Content was updated:May 15, 2025

## Show Events in Context

Click the ⋮ icon next to an event and select the [Show in context](searching-data-show-context.html "Show Events in Context") option to get a detailed view of that event, or find the selected event and surrounding events in another context. 

![Show in Context](images/search-data/show-context-menu.png)  
---  
  
**Figure 88. Show in Context**

  


The [Show in context](searching-data-show-context.html "Show Events in Context") option opens the [Find event](searching-data-show-context.html "Show Events in Context") dialog box, which allows you to search for matching values using the checkboxes, and then select the desired time interval. You can also search for a specific field in case the list of available fields exceeds the size of the dialog. 

![Find a Selected Event in Context](images/search-data/show-context.png)  
---  
  
**Figure 89. Find a Selected Event in Context**

  


The [Find event](searching-data-show-context.html "Show Events in Context") dialog shows the list of fields for the selected event and enables you to search for similar events using the values selected with the checkboxes. 

To search for similar events: 

  * Search for and select fields to be used as the basis for the new search. The values chosen here will be used to create a new search that searches for these fields and exact values. 

  * Select the interval, either: 

    * Plus or minus 10 minutes around the timestamp of the current event 

    * The time interval for the current search that returned this event 

  * Once you have selected the new search options, click Search to start a new search that will look for the field/value combinations selected across the selected time range. 




The [Show in context](searching-data-show-context.html "Show Events in Context") option can be used in cases where you find a specific value and then want to look for that same field/value combination around the same timespan, for example, to identify when the same error occurred, or if someone has tried the same security attack in a short period of time. 

Similar results can be obtained using the `around` object in queries to return the events around a reference event. See [Pagination of Results](https://library.humio.com/logscale-api/api-search-pagination.html) for more information.
