# Concatenate Multiple Tables | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-readfile-concatenate-multiple-tables.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Concatenate Multiple Tables

Combine data from multiple tables into a single result set using the [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    readFile("users_2024", "users_2025", "temp_users")

### Introduction

The [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) function can be used to read data from CSV files, lookup files and tables. When provided with multiple file or table names, it concatenates the data from all specified sources, combining them into a single result set. 

In this example, the [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) function is used to concatenate data from multiple lookup tables named `users_2024`, `users_2025`, and `temp_users`, combining all events into a single result set. 

Example data in the lookup tables might look like this: 

Table `users_2024`: 

user_id| name| department| join_date  
---|---|---|---  
001| Alice Johnson| Engineering| 2024-01-15  
002| Bob Smith| Marketing| 2024-03-22  
003| Carol Davis| Sales| 2024-06-10  
  
Table `users_2025`: 

user_id| name| department| join_date  
---|---|---|---  
004| David Wilson| Engineering| 2025-01-08  
005| Emma Brown| HR| 2025-02-14  
006| Frank Miller| Sales| 2025-03-01  
  
Table `temp_users`: 

user_id| name| department| join_date  
---|---|---|---  
007| Grace Lee| Marketing| 2025-07-20  
008| Henry Taylor| Engineering| 2025-08-15  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         readFile("users_2024", "users_2025", "temp_users")

Reads and concatenates data from three lookup tables: `users_2024`, `users_2025`, and `temp_users`. The [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) function processes each table in the order specified and combines all events into a single result set, with events from the first table appearing first, followed by events from subsequent tables. 

  3. Event Result set.




### Summary and Results

The query is used to combine data from multiple lookup tables into a single unified event set by concatenating their contents. 

This query is useful, for example, to merge historical data stored in separate yearly tables, combine data from different regional databases, or consolidate temporary and permanent datasets for comprehensive analysis. 

Sample output from the incoming example data: 

user_id| name| department| join_date  
---|---|---|---  
001| Alice Johnson| Engineering| 2024-01-15  
002| Bob Smith| Marketing| 2024-03-22  
003| Carol Davis| Sales| 2024-06-10  
004| David Wilson| Engineering| 2025-01-08  
005| Emma Brown| HR| 2025-02-14  
006| Frank Miller| Sales| 2025-03-01  
007| Grace Lee| Marketing| 2025-07-20  
008| Henry Taylor| Engineering| 2025-08-15  
  
Note that the tables could be different formats (field names and content), but typically the schemas would match which will make it easier to query and display in a widget. 

The events appear in the output in the same order as the files are specified in the function call, with all events from the first table appearing before any events from the second table, and so on.
