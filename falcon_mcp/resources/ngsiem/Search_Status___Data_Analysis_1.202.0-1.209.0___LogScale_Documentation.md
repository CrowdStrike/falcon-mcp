# Search Status | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-check-status.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

## Search Status

The Status bar at the very bottom of the User Interface provides information on the status of a search. 

  * **Query status** indicates whether the query execution is completed. 

  * **Execution time** indicates the time spent on running the query. The more specific you can be when writing a query, the fewer results LogScale will have to sort through and the faster the query will run. 

  * **Hits** are the number of events actually visited by the first aggregate, not to be misled by the total number of events returned. For example, in a query that specifies a certain number of events in the [`tail()`](functions-tail.html "tail\(\)") function, should there be any filter specified before that function, then the number of actual hits for that query is given by the filter, not by the function. 

  * **Speed** is the query speed in terms of GB per second. 

  * **EPS** (Events per Second), number of events hit each second. 

  * **Work** indicates the cost of a query in terms of CPU usage and memory allocation combined. Can be used as benchmark value to compare two different queries. The lower the work, the better the query. 

  * **Completion** shows the percentage of completion of the running query.
