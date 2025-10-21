# Filter and Collect Values in Same Table | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-selfjoin.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Filter and Collect Values in Same Table

Retrieves all emails sent from one given person to another given person using the [`selfJoin()`](https://library.humio.com/data-analysis/functions-selfjoin.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    selfJoin(email_id, where=[{from=*peter*}, {to=*anders*}], collect=[from,to])

### Introduction

The [`selfJoin()`](https://library.humio.com/data-analysis/functions-selfjoin.html) function is a join query that matches events across the same event sets. [`selfJoin()`](https://library.humio.com/data-analysis/functions-selfjoin.html) joins an event set to itself and allows you to combine events from the same table based on two fields in the same event. In order to do this, the event set must have a common field with a unique ID, a primary field, and a secondary (or subquery) field that will be matched to each other. 

In this example, emails are logged with one event for each header (each email has its own ID) and the [`selfJoin()`](https://library.humio.com/data-analysis/functions-selfjoin.html) function is used to find and collect all emails sent from one given person to another given person. Notice, that this query does two passes over the data and, therefore, cannot be used in a live query. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         selfJoin(email_id, where=[{from=*peter*}, {to=*anders*}], collect=[from,to])

Finds and collects all the values in the emails_id field that correspond to mails from `Peter` to `Anders`. 

  3. Event Result set.




### Summary and Results

The query is used to find and collect all emails sent from one given person to another person. In general, the [`selfJoin()`](https://library.humio.com/data-analysis/functions-selfjoin.html) function is useful for narrowing down a set of events in a fairly efficient manner, in cases where the total set of events is too voluminous.
