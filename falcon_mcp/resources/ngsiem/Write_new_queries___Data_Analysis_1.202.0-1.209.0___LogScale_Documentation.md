# Write new queries | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/writing-queries-manage-write.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Write Queries](writing-queries.html)

/ [Query management](writing-queries-manage.html)

### Write new queries

The Query editor is fully editable and you can enter single-line and multiple-line queries. For a comprehensive list of LogScale's query functions with descriptions, see [_Query Functions_](functions.html "Query Functions"). 

To write a new query in LogScale: 

  1. Go to Repositories and Views menu and click on the repository or view in which you want to search. 

  2. From the [`Search`](searching-data.html "Search Data") page, enter one or more search terms in the Query editor, then press **Enter** or click Run. 

  3. If needed, adjust the size of the Query editor by dragging manually or clicking the small Fit to query arrows to make it fit the query. 




Here is an example of very simple search with just one value: 

![Screenshot showing a simple one-value search](images/queries/search-one-term.png)  
---  
  
**Figure 129. One-Value Search**

  


The Query editor contains your query, and the search result appears in the [Event list](searching-data-changing-the-events-display.html "Display Results and Events") panel, under the Results tab. 

In the example, filtering is made by selecting only events that contain the text `example.com` anywhere in their log message. 

This is essentially the same as using **grep** on the Unix command-line, except with LogScale UI you can do it across all the logs, and from all servers and services at once. 

Taking this example a little further, when adding a second search term to display only results for `proxyRequest`, the results are filtered further: 

![Screenshot showing a two-value search](images/queries/search-two-terms.png)  
---  
  
**Figure 130. Two-Value Search**

  


For much more details on the possible operations you can perform with queries, see [Common Queries](writing-queries-operations.html "Frequent query operations").
