# Drop Multiple Fields from Events | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-drop-multiple-fields.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Drop Multiple Fields from Events

Remove multiple fields from all events using an array and the [`drop()`](https://library.humio.com/data-analysis/functions-drop.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Drop Field\\] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#2ac76d; click 1 #examples-drop-multiple-fields-1

logscale
    
    
    drop([header,value])

### Introduction

The [`drop()`](https://library.humio.com/data-analysis/functions-drop.html) function can be used to remove multiple unwanted fields from events simultaneously, helping to clean up data and reduce storage requirements efficiently. 

In this example, the [`drop()`](https://library.humio.com/data-analysis/functions-drop.html) function is used to remove both the header and value fields from all events in the dataset using an array syntax. 

Example incoming data might look like this: 

@timestamp| header| message| status| value| user_id  
---|---|---|---|---|---  
2025-09-15T10:00:00Z| HTTP/1.1| User login successful| 200| temp_data| user123  
2025-09-15T10:00:01Z| HTTP/1.1| File uploaded| 201| cache_info| user456  
2025-09-15T10:00:02Z| HTTP/2.0| Authentication failed| 401| debug_val| user789  
2025-09-15T10:00:03Z| HTTP/1.1| Data retrieved| 200| session_id| user123  
2025-09-15T10:00:04Z| HTTP/2.0| Connection timeout| 408| retry_count| user456  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Drop Field\\] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#2ac76d; click 1 #examples-drop-multiple-fields-1 style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         drop([header,value])

Removes both the header and value fields from all events using array syntax. The [`drop()`](https://library.humio.com/data-analysis/functions-drop.html) function accepts an array of field names enclosed in square brackets, allowing multiple fields to be eliminated simultaneously in a single operation. 

  3. Event Result set.




### Summary and Results

The query is used to remove multiple fields (header and value) from all events in the dataset in a single operation. 

This query is useful, for example, to clean up log data by removing multiple redundant fields at once, eliminate several sensitive or temporary fields before data export, or reduce data volume efficiently by dropping multiple unnecessary metadata fields simultaneously. 

Sample output from the incoming example data: 

@timestamp| message| status| user_id  
---|---|---|---  
2025-09-15T10:00:00Z| User login successful| 200| user123  
2025-09-15T10:00:01Z| File uploaded| 201| user456  
2025-09-15T10:00:02Z| Authentication failed| 401| user789  
2025-09-15T10:00:03Z| Data retrieved| 200| user123  
2025-09-15T10:00:04Z| Connection timeout| 408| user456  
  
Note that once fields are dropped, they cannot be recovered in subsequent operations within the same query. Both the header and value fields are completely removed from all events. Using array syntax is more efficient than multiple separate [`drop()`](https://library.humio.com/data-analysis/functions-drop.html) operations.
