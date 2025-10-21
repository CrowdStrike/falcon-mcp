# Query Editor | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-searchbox.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

## Query Editor

The data stored in a [repository](repositories.html "Manage Repositories and Views") can be searched by entering items and queries in the [Query Editor](searching-data-searchbox.html "Query Editor") available from the Search page. 

![A Data Search](images/search-data/split-search.png)  
---  
  
**Figure 74. A Data Search**

  


The **Query editor** allows for robust, fast regex searches of server logs and metrics in your repositories and provides an editing environment where you can write your query. The Query editor is fully editable and you can enter single and multiple-line queries. 

To create a new line, use **Shift** +**Enter**. 

### Tip

If you have used **Tab** to reach the search box, you may find that you cannot use **Tab** to tab out again, as **Tab** is a valid way of entering text within the box. To get out of the search box using only the keyboard, either use **Alt** +**Tab** , or you can change the way the browser captures the **Tab** key by using **Ctrl** +**M** on Windows or **Ctrl** +**Shift** +**M** to toggle between capturing or ignoring the **Tab** key. 

The **Search** functionality in LogScale is very powerful and searches can range from quite simple to very complex, leveraging the CrowdStrike [_Query Language Syntax_](syntax.html "Query Language Syntax"). 

For more information on how to write queries and use query functions and aggregates, see [_Write Queries_](writing-queries.html "Write Queries").
