# Convert Values Between Units | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-unitconvert-file-size.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Convert Values Between Units

Convert file size and transfer time units using the [`unit:convert()`](https://library.humio.com/data-analysis/functions-unit-convert.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] 2>Augment Data] 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    unit:convert(field=file_size, from="B", to="MB")
    | unit:convert(field=transfer_time, from="ms", to="s")
    | table([file_size, transfer_time])

### Introduction

The [`unit:convert()`](https://library.humio.com/data-analysis/functions-unit-convert.html) function is used to convert values between different units. 

Sometimes, in order to have accuracy and avoid confusion in measurement, it is necessary to convert one unit to another. A unit conversion expresses the same property as a different unit of measurement. For instance, time can be expressed in minutes instead of hours, `514 μs` to `0.514` or `sizeInKiB=4` to `size=4096`. 

In this example, the [`unit:convert()`](https://library.humio.com/data-analysis/functions-unit-convert.html) function is used to convert file sizes and transfer times units. The [`unit:convert()`](https://library.humio.com/data-analysis/functions-unit-convert.html) function automatically handles the mathematical conversion between units, making it easier to work with different measurement scales in the event set. 

Note that any unit is supported in LogScale. 

Example incoming data might look like this: 

timestamp| file_name| file_size| transfer_time| status  
---|---|---|---|---  
2025-05-15 05:30:00| doc1.pdf| 1048576| 3500| complete  
2025-05-15 05:31:00| img1.jpg| 2097152| 4200| complete  
2025-05-15 05:32:00| video1.mp4| 5242880| 12000| complete  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] 2>Augment Data] 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         unit:convert(field=file_size, from="B", to="MB")

Converts file sizes from Bytes (B) to Megabytes (MB). 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] 2>Augment Data] 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | unit:convert(field=transfer_time, from="ms", to="s")

Converts transfer times from milliseconds (ms) to seconds (s) 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] 2>Augment Data] 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | table([file_size, transfer_time])

Displays the result of the fields file_size and transfer_time in a table. 

  5. Event Result set.




### Summary and Results

The query is used to convert file sizes and transfer times units. A table showing file sizes and transfer times is, for example, useful to spot unusually large file transfers, to identify slow transfers or bottlenecks (for debugging). 

The [`unit:convert()`](https://library.humio.com/data-analysis/functions-unit-convert.html) function is useful to standardize the units for better comparison and make data more readable. 

Note that any unit is supported in LogScale. For more examples, see [`unit:convert()`](https://library.humio.com/data-analysis/functions-unit-convert.html). 

Sample output from the incoming example data: 

file_name| file_size| transfer_time  
---|---|---  
doc1.pdf| 1.0| 3.5  
img1.jpg| 2.0| 4.2  
video1.mp4| 5.0| 12.0
