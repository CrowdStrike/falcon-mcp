# Truncate a String or Message | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-replace-truncate-100.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Truncate a String or Message

Truncate a string or message to exact 100 characters using [`replace()`](https://library.humio.com/data-analysis/functions-replace.html) function and regex capturing groups 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    replace("^(.{100}).*", with="$1", field=message, as="truncated_message")

### Introduction

Regex capturing groups are a way to treat multiple characters as a single unit. The capturing groups are created by placing the characters to be grouped inside a set of parentheses. The parentheses capture the text matched by the regex inside them into a numbered group that can be reused with a numbered backreference. This way you can get the integer part of a number. 

The [`regex()`](https://library.humio.com/data-analysis/functions-regex.html) function works as a filter and can extract new fields using a regular expression. The regular expression can contain one or more named capturing groups. Fields with the names of the groups will be added to the events. 

In this example, the [`replace()`](https://library.humio.com/data-analysis/functions-replace.html) function together with regex capturing group, is used to truncate a string, chop of last part of a message, to only show the first `100` characters, replace the last character with a digit (number) at the end of the line. and then store the truncated string in the new field truncated_message, leaving the field message untouched. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         replace("^(.{100}).*", with="$1", field=message, as="truncated_message")

Captures group that matches exactly 100 characters of any type starting from the beginning of the line and replaces the last character at the end of the truncated string with a digit, then returns the truncated version in a new field named truncated_message. The original message field remains unchanged. 

`with="$1"` means that it replaces the entire match with the defined number of characters, in this case 100 characters. 

  3. Event Result set.




### Summary and Results

The query is used to truncate strings. 

Truncation can, for example, be used to speed up download times and complete searches faster. In file systems, the truncate operation is used to reduce the size of a file by removing data from the end. This can be helpful when you need to reclaim storage space or when dealing with log files that need to be periodically truncated. 

Another advantage of truncation is, that it allows you to search for a word that could have multiple endings. This way it will broaden the results and look for variations of words. 

Truncation of numbers is also useful to shorten digits past a certain point in the number.
