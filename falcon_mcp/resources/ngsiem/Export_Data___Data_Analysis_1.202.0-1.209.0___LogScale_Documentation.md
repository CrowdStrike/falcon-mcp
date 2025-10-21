# Export Data | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-data-export.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

## Export Data

You can export your data in different formats and download the information to a local file. To export data programmatically, use the [Search API](https://library.humio.com/logscale-api/api-search.html). 

  1. In the Results panel, click Save, and select Export to file. 

![Export Data](images/search-data/export-data.png)  
---  
  
**Figure 105. Export Data**

  

  2. In the appearing Export to file dialog box, select one of the following file types: 

     * CSV. Exports a selection of fields in a `.csv` file. The Fields to export option allows selecting field names that are suggested based on the query results, or enabling the Select all checkbox to have them all. 

![Suggested Fields to Export in CSV](images/search-data/fields-to-export.png)  
---  
  
**Figure 106. Suggested Fields to Export in CSV**

  


     * JSON. Exports the entire dataset ([@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring), [#repo](searching-data-event-fields.html#searching-data-event-fields-tag-repo), [#type](searching-data-event-fields.html#searching-data-event-fields-tag-type), [@id](searching-data-event-fields.html#searching-data-event-fields-metadata-id) etc.) in a `.json` file. Use this format to get one entire JSON record, with one JSON array where each element of the array is a JSON object for the event. 

     * Newline delimited JSON. Exports the entire event dataset in a `.ndjson` file. The event dataset consists of [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) and all other fields in the event such as [#repo](searching-data-event-fields.html#searching-data-event-fields-tag-repo), [#type](searching-data-event-fields.html#searching-data-event-fields-tag-type), [@id](searching-data-event-fields.html#searching-data-event-fields-metadata-id) and any fields created during ingest parsing and/or searching. Use this format to get a streamable JSON file, with each event on a single line as a single JSON object: 

JSON
           
           {"name":"storage-download","alloc":"16","cputime":"72270","#repo":"humio","#humioAutoShard":"0","class":"c.h.u.TimerExecutor$","@timestamp.nanos":"0","@rawstring":"2022-03-02T12:00:32.543+0000 [storage-download-1] INFO  c.h.u.TimerExecutor$ 1 - Job completed: name=storage-download cputime=72270 wallclock=78600 alloc=16","wallclock":"78600","@timestamp":1646222432543,"@ingesttimestamp":"1646222432545","source":"console.log","#type":"humio","#vhost":"1","thread":"storage-download-1","@host":"localhost:8080","@timezone":"Z","#kind":"logs","@id":"VfLBYh9oqH58Brx69sux0JRl_53_912_1646222432","loglevel":"INFO"}
           {"name":"delete-local-segments","alloc":"64","cputime":"45756","#repo":"humio","#humioAutoShard":"3","class":"c.h.u.TimerExecutor$","@timestamp.nanos":"0","@rawstring":"2022-03-02T12:00:32.405+0000 [delete-local-segments-1] INFO  c.h.u.TimerExecutor$ 1 - Job completed: name=delete-local-segments cputime=45756 wallclock=50500 alloc=64","wallclock":"50500","@timestamp":1646222432405,"@ingesttimestamp":"1646222432406","source":"console.log","#type":"humio","#vhost":"1","thread":"delete-local-segments-1","@host":"localhost:8080","@timezone":"Z","#kind":"logs","@id":"0LYr06NkzENWQDoXeYKl6k2R_40_887_1646222432","loglevel":"INFO"}

     * Plain text. Exports the [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field in a `.txt` file. 

  3. Enter a name for the exported file (required). 

  4. Click Export. 




When exporting data: 

  * If your search is aggregate, the exported events would normally reflect the same order as the UI. Conversely, non-aggregate queries will return a streaming export with unordered events. 

  * When exporting timestamp fields, such as [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp), the data is exported as the integer value of the timestamp, not a formatted value as may be displayed within the Search UI. To export the information with a formatted date or time, add a field to the events, using [`formatTime()`](functions-formattime.html "formatTime\(\)") to output a formatted version of the timestamp. For example, adding: 

logscale
        
        formatTime(format="%Y-%m-%d", as=fmtted)

Will add a date to each event.
