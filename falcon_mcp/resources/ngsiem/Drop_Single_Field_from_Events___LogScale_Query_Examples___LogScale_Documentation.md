# Drop Single Field from Events | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-drop-single-header-field.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Drop Single Field from Events

Remove the header field from all events using the [`drop()`](https://library.humio.com/data-analysis/functions-drop.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Drop Field\\] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#2ac76d; click 1 #examples-drop-single-header-field-1

logscale
    
    
    drop(header)

### Introduction

The [`drop()`](https://library.humio.com/data-analysis/functions-drop.html) function can be used to remove unwanted fields from events, helping to clean up data and reduce storage requirements. 

In this example, the [`drop()`](https://library.humio.com/data-analysis/functions-drop.html) function is used to remove the header field from all events in the dataset. 

Example incoming data might look like this: 

@timestamp| header| message| status| user_id  
---|---|---|---|---  
2025-09-15T10:00:00Z| HTTP/1.1| User login successful| 200| user123  
2025-09-15T10:00:01Z| HTTP/1.1| File uploaded| 201| user456  
2025-09-15T10:00:02Z| HTTP/2.0| Authentication failed| 401| user789  
2025-09-15T10:00:03Z| HTTP/1.1| Data retrieved| 200| user123  
2025-09-15T10:00:04Z| HTTP/2.0| Connection timeout| 408| user456  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Drop Field\\] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#2ac76d; click 1 #examples-drop-single-header-field-1 style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         drop(header)

Removes the header field from all events. The [`drop()`](https://library.humio.com/data-analysis/functions-drop.html) function permanently eliminates the specified field from the event data, reducing the amount of data stored and processed in subsequent operations. 

  3. Event Result set.




### Summary and Results

The query is used to remove the header field from all events in the dataset. 

This query is useful, for example, to clean up log data by removing redundant protocol information, eliminate sensitive fields before sharing data, or reduce data volume by dropping unnecessary metadata fields. 

Sample output from the incoming example data: 

@timestamp| message| status| user_id  
---|---|---|---  
2025-09-15T10:00:00Z| User login successful| 200| user123  
2025-09-15T10:00:01Z| File uploaded| 201| user456  
2025-09-15T10:00:02Z| Authentication failed| 401| user789  
2025-09-15T10:00:03Z| Data retrieved| 200| user123  
2025-09-15T10:00:04Z| Connection timeout| 408| user456  
  
Note that once a field is dropped, it cannot be recovered in subsequent operations within the same query. The header field is completely removed from all events.
