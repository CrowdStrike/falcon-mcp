# Remove Fixed-Length Prefix and Suffix From Text | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-textsubstring-remove-fixed-prefix-suffix.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Remove Fixed-Length Prefix and Suffix From Text

Remove characters from both ends using the [`text:substring()`](https://library.humio.com/data-analysis/functions-text-substring.html) function with [`text:length()`](https://library.humio.com/data-analysis/functions-text-length.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    text:substring(message, begin=7, end=text:length(message) - 9)

### Introduction

The [`text:substring()`](https://library.humio.com/data-analysis/functions-text-substring.html) function can be used with [`text:length()`](https://library.humio.com/data-analysis/functions-text-length.html) to extract a portion of text using both fixed positions and dynamically calculated positions based on the string length. The [`text:length()`](https://library.humio.com/data-analysis/functions-text-length.html) function returns the total number of characters in a string. 

In this example, the [`text:substring()`](https://library.humio.com/data-analysis/functions-text-substring.html) function is used with [`text:length()`](https://library.humio.com/data-analysis/functions-text-length.html) to extract text starting from a fixed position and ending at a position calculated relative to the string's end. 

Example incoming data might look like this: 

@timestamp| message  
---|---  
2025-08-06T10:15:00.000Z| [START]Important message content here[END_NOW]  
2025-08-06T10:15:01.000Z| [START]Another test message here[END_NOW]  
2025-08-06T10:15:02.000Z| [START]Processing completed OK[END_NOW]  
2025-08-06T10:15:03.000Z| [START]Error in module XYZ[END_NOW]  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         text:substring(message, begin=7, end=text:length(message) - 9)

Extracts a portion of the [message](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-action.html) field using: 

     * A fixed starting position of 7 (skipping "[START]") 

     * A dynamic end position calculated by [`text:length()`](https://library.humio.com/data-analysis/functions-text-length.html) getting the total length of the message and subtracting 9 characters (length of "[END_NOW]") 

This effectively removes both the prefix and suffix from the message. 

  3. Event Result set.




### Summary and Results

The query is used to extract the main content from messages that have fixed-length prefixes and suffixes. 

This query is useful, for example, to clean up formatted log messages, extract the meaningful content from standardized message formats, or remove known wrapping text from strings. 

Sample output from the incoming example data: 

message| result  
---|---  
[START]Important message content here[END_NOW]| Important message content here  
[START]Another test message here[END_NOW]| Another test message here  
[START]Processing completed OK[END_NOW]| Processing completed OK  
[START]Error in module XYZ[END_NOW]| Error in module XYZ  
  
Note that [`text:substring()`](https://library.humio.com/data-analysis/functions-text-substring.html) uses zero-based numbering, so position 7 is actually the 8th character in the string. 

In the first event, the 8th character is, therefore, `I`: 
    
    
    [ S T A R T ] I
    0 1 2 3 4 5 6 7

The end position is calculated dynamically for each message based on its total length using [`text:length()`](https://library.humio.com/data-analysis/functions-text-length.html).
