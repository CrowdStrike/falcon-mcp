# Display Fields | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-displaying-fields.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

Content was updated:Aug 9, 2023

## Display Fields

The [Fields panel](searching-data-displaying-fields.html "Display Fields") available from the [`Search`](searching-data.html "Search Data") page contains the following: 

  * Columns lists those fields displayed in the [Event list](searching-data-changing-the-events-display.html "Display Results and Events") in the [Results panel](searching-data-changing-the-events-display.html "Display Results and Events"). It must contain at least one column selected. 

  * Fields lists all the other fields available for queries, which can be displayed by clicking +. Clicking the third column near each field will add a star (for example ★) and move the field to the top of known fields. 

  * # indicates the number of distinct values observed for that field, for example, the field cardinality. 

  * % indicates the percentage of events that have this field. 

  * 🔄 resets columns and removes the ones previously added. 

  * ⋮ three-dot menu to trigger [Field Interactions](searching-data-field-interactions.html "Field Interactions"). 

  * Filter fields allows searching of a field by typing its name in the field. 

  * Fetch more allows getting more than the 200 events displayed by default. 

The fields presented after clicking this button are a representative subset of the data in the repository, but do not necessarily include all fields, as we do not look at _all_ data: newer data is favored, so older data within your selected time interval is not likely to be returned. 

Conversely, if older and newer data have roughly the same fields, then the results will most likely be accurate because the data is relatively uniform. 

This behavior improves field statistics, as the fields presented in the Fields panel might not be in the events you are currently looking at. 




![Fields Panel](images/search-data/search-fields.png)  
---  
  
**Figure 75. Fields Panel**

  


The Fields panel can be expanded and collapsed by clicking the arrow next to it. 

![Screenshot showing the button to expand the Fields Panel](images/search-data/expand-field-panel.png)  
---  
  
**Figure 76. Expand the Fields Panel**
