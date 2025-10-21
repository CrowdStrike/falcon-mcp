# Remove ANSI Escape Codes From Text | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-stripansicodes-message.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Remove ANSI Escape Codes From Text

Clean text containing ANSI color codes using the [`stripAnsiCodes()`](https://library.humio.com/data-analysis/functions-stripansicodes.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] 3["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    message := "\x1b[93;41mColor"
    stripAnsiCodes(message)
    @display := message

### Introduction

The [`stripAnsiCodes()`](https://library.humio.com/data-analysis/functions-stripansicodes.html) function can be used to remove ANSI escape sequences from text fields. These sequences are commonly used to add color and formatting to terminal output but may interfere with log analysis. 

In this example, the [`stripAnsiCodes()`](https://library.humio.com/data-analysis/functions-stripansicodes.html) function is used to clean a text field containing ANSI color codes and assign the result to a display field. 

Example incoming data might look like this: 

@timestamp| message  
---|---  
2025-08-06T10:15:30.000Z| \x1b[93;41mColor  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] 3["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         message := "\x1b[93;41mColor"

Creates a variable [message](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-action.html) containing text with ANSI escape codes. The sequence `\x1b[93;41m` sets bright yellow text (93) on a red background (41). 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] 3["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         stripAnsiCodes(message)

Removes all ANSI escape sequences from the content of the [message](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-action.html) field, leaving only the plain text. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] 3["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         @display := message

Assigns the cleaned text to the @display field for output. 

  5. Event Result set.




### Summary and Results

The query is used to clean text by removing ANSI escape codes that control color and formatting in terminal output. 

This query is useful, for example, to process log files that contain terminal output or to clean data for display in interfaces that don't support ANSI formatting. 

Sample output from the incoming example data: 

@timestamp| @timestamp.nanos| @timezone| @display| message  
---|---|---|---|---  
1754475330000| 0| Z| Color| \x1b[93;41mColor
