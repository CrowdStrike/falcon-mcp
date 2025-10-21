# Field Data Types | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-types.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

## Field Data Types

Use the [Data type](searching-data-format-column.html#searching-data-format-column-data-type) column formatting option (appears when clicking the up-arrow-head next to column header) to assign a relevant data type to field names, thus affecting how data is displayed in the Event list. 

Available data types are: 

  * Bytes formats the data size in bytes, with prefixes. Example: `1500000` will be displayed as `1.5 MB`. 

  * JSON offers a view of JSON data with expandable and collapsible nodes, allowing the interaction with its tree structure. 




![JSON Formatting Type](images/search-data/json-format.png)  
---  
  
**Figure 94. JSON Formatting Type**

  


  * Log line highlights data in different colors on all columns if the data format is supported — supported formats are JSON, XML and accesslog. This is the default format for field [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring). 

### Note

An Invalid value error message is shown in the string in case of unsupported data format. 

  * Number displays numbers with thousands separators and right-aligned column. Example: `1,000.24`. 

  * Text displays data as plain text. This is the default format for all fields except [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring), [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) and [@ingesttimestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-ingesttimestamp). 

  * Time Ago converts Unix timestamp with milliseconds in Time ago relative time. Example: `47m 12s ago`. 

  * Time Duration displays the milliseconds elapsed as duration. Example: `3000` is shown as `3s`. 

  * XML shows highlighted XML. 

  * Make default for field saves the selected format as the default for that field (instead of the field's standard format type), so that the data type previously chosen is kept when the field is removed and re-added in the [Event list](searching-data-changing-the-events-display.html "Display Results and Events"). These settings will never override the formatting chosen for any dashboard or widget already configured with different data types.
