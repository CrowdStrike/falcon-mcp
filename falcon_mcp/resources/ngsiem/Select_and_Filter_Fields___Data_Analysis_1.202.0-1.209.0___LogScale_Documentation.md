# Select and Filter Fields | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-selecting-fields.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

Content was updated:May 15, 2025

## Select and Filter Fields

Select single fields to search and filter on those fields. 

  1. Click on a field in the [Fields panel](searching-data-displaying-fields.html "Display Fields") — [#severity](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-action.html) in the example: a resizable flyout opens with the list of values found and the number of occurrences for each. 

![Select Fields](images/search-data/selecting-fields.png)  
---  
  
**Figure 77. Select**

  

  2. Click the ⋮ icon next to a field name to get several filtering options. 

![Filtering Options](images/search-data/filtering-fields.png)  
---  
  
**Figure 78. Filtering Options**

  

  3. Select one of the options: for example, Aggregate → Group by value will group events by the value of that field, Timechart → Use field as series will run the [`timeChart()`](functions-timechart.html "timeChart\(\)") function in the Query editor to show events that have that field grouped into series and plotted in a timechart. 




More filter options and interactions with fields are available, such as exclude () or include (⊜) in the search all events that have the selected field. 

When the menu is opened for [Field Interactions](searching-data-field-interactions.html "Field Interactions") with live queries, the [Fields panel](searching-data-displaying-fields.html "Display Fields") flyout will display a fixed list of top values. The top values are kept from the point in time when the menu was opened. See [Field Interactions](searching-data-field-interactions.html "Field Interactions") for more information.
