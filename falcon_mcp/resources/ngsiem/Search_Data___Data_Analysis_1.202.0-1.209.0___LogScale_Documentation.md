# Search Data | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

# Search Data

The data stored in repositories in LogScale can be searched — that's its main point and value. Searches are primarily done through the User Interface from the Search page (available when a repository is selected). 

The following provides links to pages which explain what you can do when searching. 

## Basic Search Items

The following listed linked pages are related to the basics of searching a repository. 

  * **[Query Editor](searching-data-searchbox.html "Query Editor")**

LogScale's search functionality using the **Query editor** allows for robust, fast regex searches of server logs and metrics in your repositories. As a first step to searching data, you enter a query in the query editor. This linked page covers this essential component of the User Interface. 

  * **[Event Fields](searching-data-event-fields.html "Event Fields")**

For each data record in a repository, each event is parsed into multiple fields for easy sorting and searching. This linked page explains the fields available. 

  * **[Search Status](searching-data-check-status.html "Search Status")**

Whenever a repository is searched, status information on that search is displayed in the Status bar (bottom line of LogScale's User Interface). This linked page explains those statuses. 




## Better Search Results Display

The default way in which search results are displayed is usually adequate — especially when first constructing a query. 

The following listed linked pages provide information on how to improve the way the results are displayed. 

  * **[Display Fields](searching-data-displaying-fields.html "Display Fields")**

In the UI, there are several event fields listed on which you may search. This linked page explains the Field Panel for a repository. 

  * **[Format Columns](searching-data-format-column.html "Format Columns")**

You can add, eliminate, and reorder the field columns in search results. You can also reformat the contents of those columns for a more meaningful display. 

  * **[Highlight Filter Match](searching-data-filter-highlighting.html "Filter Match Highlighting")**

Search results can be highlighted based on the filters applied in queries. Highlighting helps you identify where in the event text a query matches the results. 

  * **[Different Visuals](searching-data-change-data-display.html "Different Visuals")**

Search results are ingested as text and, therefore, as default displayed as text. You can easily change the display for search results to show the data in a variety of ways, including graphs, pie charts, and other graphics. 

  * **[Display Results and Events](searching-data-changing-the-events-display.html "Display Results and Events")**

Events are displayed in the search results in a specific way, in a specific order. You can change how results are displayed, though. 




## Refine Search Results

You do not have to accept data as it comes, as the data is stored in the repository. 

The following listed linked pages explain how you can refine search results. 

  * **[Select and Filter Fields](searching-data-selecting-fields.html "Select and Filter Fields")**

When searching a repository, you can select fields to search. You can also select fields on which to filter the results. 

  * **[Add and Remove Fields](searching-data-add-remove-fields.html "Add and Remove Fields")**

For a more simplified display that is easier to review, you can select which fields in a query results to display — and which to hide. 

  * **[Change Time Interval](searching-data-expand-timeframe.html "Change the Time Interval")**

Search results are for a specific time interval: such as, the past day, the past month, other time ranges. Instead of static data, you can also display data for a time interval that includes the current moment, known as live data. 

  * **[Set Time Zone](searching-data-set-timezone.html "Set the Time Zone")**

Data is ingested into LogScale with a time stamp for each event. Those time stamps are for a specific time zone, but the time zone can be changed in your search results. 




## Search Deeper

Without refining or rerunning a search, you can get more information from a search that appears on the surface. 

The following listed linked pages explain how to go deeper into search results. 

  * **[Inspect Events](searching-data-inspecting-events.html "Inspect Events")**

When you search a repository, you get a list of events in the [Results panel](searching-data-changing-the-events-display.html "Display Results and Events"). You can click on a specific event in the [Event list](searching-data-changing-the-events-display.html "Display Results and Events") to get more details in the [Inspection panel](searching-data-inspecting-events.html "Inspect Events") (that appears below the [Results panel](searching-data-changing-the-events-display.html "Display Results and Events") when a specific event is selected from the [Event list](searching-data-changing-the-events-display.html "Display Results and Events")). 

  * **[Show in Context](searching-data-show-context.html "Show Events in Context")**

You can have a detail view in context of a single event and search for value matches with a different time interval. 

  * **[Event List Interactions](searching-data-search-interactions.html "Event List Interactions")**

You may find the search results fairly limited. Depending on your user permission, it is possible to interact with the results to reveal much more information. This linked page provides details and illustrations on how to create event list interactions. 

  * **[Field Interactions](searching-data-field-interactions.html "Field Interactions")**

In the [Results panel](searching-data-changing-the-events-display.html "Display Results and Events"), [Fields panel](searching-data-displaying-fields.html "Display Fields"), and [Inspection panel](searching-data-inspecting-events.html "Inspect Events"), you can click the 

⋮ icon for a field to get a list of interaction options. 

  * **[Field Aliasing](searching-data-field-aliasing.html "Field Aliasing")**

Implementing _Field Aliasing_ in your workflow simplifies data correlation from various sources. You can provide alternative names — or aliases — to fields created at parse time, across a view, or the entire organization. 




## Save and Export Searches

Search queries can be saved for future use and search results can be exported. 

The following listed linked pages provide information about the different saving options and export formats. 

  * **[Saved Searches](searching-data-saving-a-search.html "Saved Searches")**

Besides search queries, also dashboard widgets and scheduled searches can be saved. As it can take some time to construct a search query and if used often, saving searches and different dashboards for reuse is time saving. 

  * **[Export Data](searching-data-data-export.html "Export Data")**

Search results can be exported to a file for use in another application. This linked page explains how to export the results as they are, to a plain text file. It also explains how to export to a file in CSV, Newline delimited JSON, or JSON format.
