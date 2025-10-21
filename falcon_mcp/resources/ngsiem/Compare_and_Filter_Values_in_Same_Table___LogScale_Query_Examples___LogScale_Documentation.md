# Compare and Filter Values in Same Table | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-selfjoinfilter.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Compare and Filter Values in Same Table

Retrieves all emails with attachments sent from one given person to another given person using the [`selfJoinFilter()`](https://library.humio.com/data-analysis/functions-selfjoinfilter.html) function matching only the ID 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    selfJoinFilter(field=email_id, where=[{ from=peter }, {to=paul}])
    | attachment=*

### Introduction

The [`selfJoin()`](https://library.humio.com/data-analysis/functions-selfjoin.html) function is a join query that matches events across the same event sets. [`selfJoin()`](https://library.humio.com/data-analysis/functions-selfjoin.html) joins an event set to itself and allows you to combine events from the same table based on two fields in the same event. In order to do this, the event set must have a common field with a unique ID, a primary field, and a secondary (or subquery) field that will be matched to each other. The [`selfJoinFilter()`](https://library.humio.com/data-analysis/functions-selfjoinfilter.html) function differs from the [`selfJoin()`](https://library.humio.com/data-analysis/functions-selfjoin.html) function as this is a filter query. 

Where [`selfJoin()`](https://library.humio.com/data-analysis/functions-selfjoin.html) uses the _`where`_ parameter to find the values of a given field where the conditions are met and return them as a result, [`selfJoinFilter()`](https://library.humio.com/data-analysis/functions-selfjoinfilter.html) passes the events containing values that meet the condition on to a second phase, where a filter function is run on the ID of the event itself - the events need only match the ID, not any of the where clauses; unless prefilter=true is set. 

In this example, emails are logged with one event for each header (each email has its own ID) and the [`selfJoinFilter()`](https://library.humio.com/data-analysis/functions-selfjoinfilter.html) function is used to find all attachments for emails sent from one given person to another given person. Notice, that this query does two passes over the data and, therefore, cannot be used in a live query. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         selfJoinFilter(field=email_id, where=[{ from=peter }, {to=paul}])

Finds all the values in the emails_id field that correspond to mails from `Peter` to `Paul`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | attachment=*

Finds all log messages with one of those values in the emails_ids field that has been passed on from first phase that also have an attachment. 

  4. Event Result set.




### Summary and Results

The query is used to find all emails with attachments sent from one given person to another person. In general, the [`selfJoinFilter()`](https://library.humio.com/data-analysis/functions-selfjoinfilter.html) function is useful for narrowing down a set of events in a fairly efficient manner, in cases where the total set of events is too voluminous.
