# Transpose a Basic Table | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-transpose-basic.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Transpose a Basic Table

Transposing an event set effectively switches rows (each event) into columns (an event) 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Drop Field\\] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#2ac76d; click 3 #examples-transpose-basic-3

logscale
    
    
    groupBy([loglevel])
    | transpose(header=loglevel)
    | drop(column)

### Introduction

By transposing event set, the information can be viewed and summarized in a more human readable form. Transposing also allows for aggregated data to be viewed in a form where the value of an aggregated field becomes the columns. This can be used to summarize the information further by showing multiple rows of data. For example, in the [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) repository the event information contains a list of errors, warnings, or informational events for activity within the cluster. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Drop Field\\] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#2ac76d; click 3 #examples-transpose-basic-3 style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy([loglevel])

Aggregates the lows by the loglevel. This field will either be `WARN`, `ERROR` or `INFO` depending on the level of the event log entry. The default function is used, which results in a count in the number of times an event of this type has been seen: 

loglevel |  _count  
---|---  
`ERROR` |  27424   
`INFO` |  18840156   
`WARN` |  2059898   
  
In this output, each event is a row in the table, each with two fields, loglevel and _count. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Drop Field\\] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#2ac76d; click 3 #examples-transpose-basic-3 style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | transpose(header=loglevel)

Transposing the events within the [`transpose()`](https://library.humio.com/data-analysis/functions-transpose.html) will make each field in each event a row in the new stream of events, for example, the loglevel field with the value `ERROR` will become the field ERROR, swapping the rows for columns. By using the [_`header`_](https://library.humio.com/data-analysis/functions-transpose.html#query-functions-transpose-header) parameter, [`transpose()`](https://library.humio.com/data-analysis/functions-transpose.html) uses the value of the aggregated field as the fieldname. The output will now be a table with a column (field) for each value, and a single row with the count: 

ERROR |  INFO |  WARN |  column  
---|---|---|---  
97159 |  63719404 |  5716733 |  _count   
  
  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Drop Field\\] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#2ac76d; click 3 #examples-transpose-basic-3 style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | drop(column)

In the final output, the column field in the events is the one generated from the field names of the original events and it's not needed, so it can be removed by using the [`drop()`](https://library.humio.com/data-analysis/functions-drop.html) function to remove the field from the event set. 

  5. Event Result set.




### Summary and Results

The [`transpose()`](https://library.humio.com/data-analysis/functions-transpose.html) is a great way of reorganizing data into a format is either more readable, or easily applied to other display formats as part of a widget. The final table looks like this: 

ERROR |  INFO |  WARN  
---|---|---  
97159 |  63719404 |  5716733   
  
However, the information as it is now formatted can more easily be applied to a variety of visualizations. For example, the data can be formatted as a bar chart, as we now have a list of fields and a value: 

![](images/functions/examples/transpose/transpose-basic-bar.png)  
---  
  
The difference is that without [`transpose()`](https://library.humio.com/data-analysis/functions-transpose.html), the aggregate result set is a list of events with a field name and value. With [`transpose()`](https://library.humio.com/data-analysis/functions-transpose.html), the result set is a single event with multiple fields, and this is interpreted by the bar chart as a series of values.
