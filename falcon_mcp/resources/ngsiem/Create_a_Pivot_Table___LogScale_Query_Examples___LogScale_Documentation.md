# Create a Pivot Table | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-transpose-pivot.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Create a Pivot Table

Creating a view of LogScale activity 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Drop Field\\] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#2ac76d; click 3 #examples-transpose-pivot-3

logscale
    
    
    groupBy([type,actor.user.id],function={groupBy(actor.user.id, function=max(@timestamp))})
    |transpose(header=type)
    |drop(column)

### Introduction

The [humio-audit](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-audit.html) repository contains audit events for the LogScale cluster. Reporting on this information can provide a wealth of information, but a useful summary can be created based on the activities, users and which the latest user of that particular operation. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Drop Field\\] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#2ac76d; click 3 #examples-transpose-pivot-3 style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy([type,actor.user.id],function={groupBy(actor.user.id, function=max(@timestamp))})

The first step to creating a pivot table is the base query that will create the initial summary of the information. In this fragment, a nested [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) aggregation. The embedded aggregation creates a group of the maximum access time for a given user, by using [`max()`](https://library.humio.com/data-analysis/functions-max.html) on the @timestamp against the actor.user.id. This creates a table of the last event by the user. The outer [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) then creates an aggregation of this maximum user time against the type which defines the operation performed. 

The result is a table of the last user and time for a specific operation; for example, the last time a query was executed. An example of this table can be seen below: 

type |  actor.user.id |  _max  
---|---|---  
`alert.clear-error` |  `0O7WGPBX9YbvZbKOrBMd5fgH` |  1700546666592   
`alert.create` |  `0O7WGPBX9YbvZbKOrBMd5fgH` |  1699004139419   
`alert.update` |  `0O7WGPBX9YbvZbKOrBMd5fgH` |  1700546666676   
`dashboard.create` |  `0O7WGPBX9YbvZbKOrBMd5fgH` |  1698417330709   
`dataspace.query` |  `0O7WGPBX9YbvZbKOrBMd5fgH` |  1700721296197   
  
  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Drop Field\\] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#2ac76d; click 3 #examples-transpose-pivot-3 style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         |transpose(header=type)

The [`transpose()`](https://library.humio.com/data-analysis/functions-transpose.html) will convert individual columns into rows, switching the orientation. For example, the type column will now become the type row. However, there are no row titles, so the title for the resulting table will by default create a header row containing the column and row numbers, like this: 

column |  row[1] |  row[2] |  row[3] |  row[4] |  row[5]  
---|---|---|---|---|---  
_max |  1700546666592 |  1699004139419 |  1700546666676 |  1698417330709 |  1700722209214   
actor.user.id |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH   
type |  alert.clear-error |  alert.create |  alert.update |  dashboard.create |  dataspace.query   
  
However, the aggregate grouping, type could be used instead as a valid header for each column. To achieve that, use the [_`header`_](https://library.humio.com/data-analysis/functions-transpose.html#query-functions-transpose-header) parameter to specify type as the column. The resulting table now looks like this: 

alert.clear-error |  alert.create |  alert.update |  column |  dashboard.create |  dataspace.query  
---|---|---|---|---|---  
1700546666592 |  1699004139419 |  1700546666676 |  _max |  1698417330709 |  1700722210073   
0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  actor.user.id |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH   
  
  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Drop Field\\] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#2ac76d; click 3 #examples-transpose-pivot-3 style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         |drop(column)

The table created contains the summarized information pivoted around the user ID and last event time further summarized by the type of the event. However, there is a column in the table, column, which is now a field in the event stream that was generated from the old row before the table was pivoted. 

That column can be removed by dropping the column field from the event using [`drop()`](https://library.humio.com/data-analysis/functions-drop.html) to remove the column from the events. 

  5. Event Result set.




### Summary and Results

Pivoting an event set of data allows for the information to be displayed and summarized in a format that may make more logical sense as a display format. The final table will look like this: 

alert.clear-error |  alert.create |  alert.update |  dashboard.create |  dataspace.query   
---|---|---|---|---  
1700546666592 |  1699004139419 |  1700546666676 |  1698417330709 |  1700722210073   
0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH
