# Inspect Events | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-inspecting-events.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

Content was updated:May 15, 2025

## Inspect Events

Click the ⋮ icon next to an event and select the [Inspect](searching-data-inspecting-events.html "Inspect Events") option to look deeper at a single event. Alternatively, click on the event directly in the [Event list](searching-data-changing-the-events-display.html "Display Results and Events"). 

![Inspect an event](images/search-data/inspect-menu.png)  
---  
  
**Figure 83. Inspect an event**

  


This option opens the [Inspection panel](searching-data-inspecting-events.html "Inspect Events"), which includes three tabs: 

  * Fields shows **Name** and **Value** of all the fields in the selected event. You can filter to see certain fields only by entering field names (case-insensitive) in the box, separated by comma. 

  * Message shows the full, unaltered log message that was sent to LogScale. The full message is also available on all events in a special field called [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring). 

  * JSON shows the log message in JSON format. It is the same visualization as when you choose the [Field Data Types](searching-data-types.html "Field Data Types"). Click on any field under JSON to get some contextual menus — they are described at [Field Interactions](searching-data-field-interactions.html "Field Interactions"). 




![Inspection Panel](images/search-data/inspection-panel.png)  
---  
  
**Figure 84. Inspection Panel**

  


The small icons next to each field name provide quickly access to filtering and groupby options: 

  * ⋮ — three-dot menu to trigger [Field Interactions](searching-data-field-interactions.html "Field Interactions"). 

  * ⊜ — Match value in query 

  * — Exclude value in query 

  * — Group by value
