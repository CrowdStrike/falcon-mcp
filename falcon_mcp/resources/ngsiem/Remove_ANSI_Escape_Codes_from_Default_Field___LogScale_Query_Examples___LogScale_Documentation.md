# Remove ANSI Escape Codes from Default Field | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-stripansicodes-default.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Remove ANSI Escape Codes from Default Field

Remove ANSI Escape Codes from Default Field using the [`stripAnsiCodes()`](https://library.humio.com/data-analysis/functions-stripansicodes.html) function without parameters 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    stripAnsiCodes()

### Introduction

The [`stripAnsiCodes()`](https://library.humio.com/data-analysis/functions-stripansicodes.html) function can be used to remove ANSI escape sequences from text fields. When used without parameters, it processes the default field containing the event text. 

In this example, the [`stripAnsiCodes()`](https://library.humio.com/data-analysis/functions-stripansicodes.html) function is used to clean ANSI escape codes from the default field. 

Example incoming data might look like this: 

@timestamp| @rawstring  
---|---  
2025-08-06T10:15:30.000Z| \x1b[93;41mWarning: System overload\x1b[0m  
2025-08-06T10:15:31.000Z| \x1b[32mStatus: Normal\x1b[0m  
2025-08-06T10:15:32.000Z| \x1b[31mError: Connection failed\x1b[0m  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         stripAnsiCodes()

Removes all ANSI escape sequences from the default field. When no field is specified, the function processes the [@rawstring](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field, removing color codes and other ANSI formatting sequences while preserving the plain text content. 

  3. Event Result set.




### Summary and Results

The query is used to clean text by removing ANSI escape codes that control color and formatting in terminal output, operating on the default field. 

This query is useful, for example, to process raw log data that contains terminal output with color coding, making the text suitable for analysis and display in any context. 

Sample output from the incoming example data: 

@timestamp| @timestamp.nanos| @timezone| @rawstring  
---|---|---|---  
1754475330000| 0| Z| Warning: System overload  
1754475331000| 0| Z| Status: Normal  
1754475332000| 0| Z| Error: Connection failed
