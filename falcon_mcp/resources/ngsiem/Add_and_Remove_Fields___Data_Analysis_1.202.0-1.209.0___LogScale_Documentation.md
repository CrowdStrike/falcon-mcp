# Add and Remove Fields | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-add-remove-fields.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

## Add and Remove Fields

To optimize the data visualized you can select which of the result fields should be displayed or hidden. 

Fields can be added/removed from both the [Fields panel](searching-data-displaying-fields.html "Display Fields") and the Tool panel under Search. From the Tool panel you can add formatting to the field as well. 

### Fields Panel

  1. Run a query as explained in [Write new queries](writing-queries-manage-write.html "Write new queries"). 

  2. In the [Fields panel](searching-data-displaying-fields.html "Display Fields"), click the + or - signs next to each field (see [Figure 75, “Fields Panel”](searching-data-displaying-fields.html#figure_searching-data-displaying-fields1 "Figure 75. Fields Panel")): 

     * + adds the field to the currently displayed result. 

     * - removes the field from the currently displayed result. 




### Note

By default, LogScale displays fields coming from 200 events at most. You can display more data by clicking Fetch more. 

From the [Fields panel](searching-data-displaying-fields.html "Display Fields"), you can also click on a field name and get quick access to filtering options: 

  * ⊜ — Match value in query 

  * — Exclude value in query 




### Tool Panel

  1. Run a query as explained in [Write new queries](writing-queries-manage-write.html "Write new queries"). 

  2. From the Tool panel, click the Format Event List icon (the brush) to expand it. 

![Expanding the Format Event List Panel](images/search-data/expand-format-panel.png)  
---  
  
**Figure 79. Expanding the Format Event List Panel**

  

  3. The Format event list panel, that appears when clicking the Format Event List icon (the brush), stands as a separate area on the right-hand side of the User Interface and shows only the fields added as columns in the Event list. 

![Format Event List Panel](images/search-data/column-format-panel.png)  
---  
  
**Figure 80. Format Event List**

  


From here, click + to add a new column in the [Event list](searching-data-changing-the-events-display.html "Display Results and Events") and format the field accordingly. 

Clicking - removes the field from the currently displayed result. See [Column Properties](searching-data-column-properties.html "Column Properties"). 

![Adding a New Field from the Format Event List Panel](images/search-data/add-field.png)  
---  
  
**Figure 81. Adding a New Field from the Format Event List Panel**

  




### Reset to default results

Click the 🔄 icon in the [Fields panel](searching-data-displaying-fields.html "Display Fields") to reset and remove any fields recently added and display the default results only.
