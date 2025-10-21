# Select and Copy Rows | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-copy-rows.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

Page was created:Sep 3, 2025

## Select and Copy Rows

The [`Search`](searching-data.html "Search Data") page supports selecting and copying rows in [`Table`](widgets-table.html "Table") widgets. 

To copy rows: 

  1. Hover over the table row you want to copy to reveal the checkbox, or click the checkbox in the header column to select all rows in the table. If row numbers were enabled, they'll be replaced by the checkboxes. 

  2. Click the copy button popping up for the selected rows: the rows will be copied to the clipboard. Table display options affect copied data - the clipboard content will match what you see in the table.

  3. Paste the copied data to your desired destination: the data will be in CSV format with column headers, with identical CSV formatting as the [Export Data](searching-data-data-export.html "Export Data") to CSV file feature. 




**Figure 85. Copy rows**

  


### Note

If a live query is running, it will automatically pause when you start selecting rows.
