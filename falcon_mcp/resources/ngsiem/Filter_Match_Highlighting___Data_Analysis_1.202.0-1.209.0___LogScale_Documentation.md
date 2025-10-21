# Filter Match Highlighting | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-filter-highlighting.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

## Filter Match Highlighting

Filter Match Highlighting in LogScale visually emphasizes search results that match applied filters in the Event List widget by using different colors to highlight matching text and log lines. The feature can be enabled through Account Settings and works with free-text searches and regular expressions, though it has some limitations with structured data formats like JSON and XML, and may not show all overlapping matches when multiple filters are applied. 

From the Search page it is possible to highlight results that match the filters applied in the query, by clicking the Filter match highlighting icon at the top right corner of the Results panel: 

![Filter Highlight](images/search-data/filter-highlight.png)  
---  
  
**Figure 101. Filter Highlight**

  


**Displaying with different filter colors**

Filter match highlighting with different colors is supported in the [Event list](searching-data-changing-the-events-display.html "Display Results and Events") for the [field data types](searching-data-types.html "Field Data Types"); Text and Log Line, and results are highlighted in the [Inspection panel](searching-data-inspecting-events.html "Inspect Events") as well. 

**Enabling the filter match highlighting feature**

To enable the Filter match highlighting option, go to your User icon → Manage your account → Account settings and select the Automatically highlight filter matches on search page checkbox: 

![Enabling Filter Highlight from Settings](images/search-data/filter-highlight-enable.png)  
---  
  
**Figure 102. Enabling Filter Highlight from Settings**

  


When using this feature, the following conditions apply: 

  * Highlighting is currently available for the [`Event List`](widgets-eventlist.html "Event List") widget type, supporting both free-text searches and regular expressions. 

  * Filter match highlighting does not work when highlighting JSON, XML and other structured column formats where syntax highlighting is already applied. 

  * The matching is done on a best-effort basis and performed after the search pipeline is executed. This means that highlighting may not be completely correct, especially in complex queries — when branching using case-statements for example. 

  * If several filters match the same text in a field and the matches overlap, parts or all of some matches from different filters may not be shown.
