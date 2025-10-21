# text:length() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-text-length.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Page was created:Sep 23, 2025

## [`text:length()`](functions-text-length.html "text:length\(\)")

The [`text:length()`](functions-text-length.html "text:length\(\)") function computes the length of a string. [`text:length()`](functions-text-length.html "text:length\(\)") is particularly useful in combination with the [`text:substring()`](functions-text-substring.html "text:substring\(\)") function for more programmatically extracting snippets of another text. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-text-length.html#query-functions-text-length-as)|  string| optional[a] | `_length`|  The name of the field to store the length in.   
[_`string`_](functions-text-length.html#query-functions-text-length-string)[b]| expression| required |  |  The string or field from which to compute the length.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`string`_](functions-text-length.html#query-functions-text-length-string) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`string`_](functions-text-length.html#query-functions-text-length-string) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     text:length("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     text:length(string="value")
> 
> These examples show basic structure only.

### [`text:length()`](functions-text-length.html "text:length\(\)") Function Operation

Notably, the length of a string is the number of extended grapheme clusters as defined by the [Unicode Standard Annex #29](https://www.unicode.org/reports/tr29/), specifically [ UAX29-C1-1](https://www.unicode.org/reports/tr29/#C1-1). This means that the length returned by the [`text:length()`](functions-text-length.html "text:length\(\)") function more closely matches the "natural" character count, as opposed to the [`length()`](functions-length.html "length\(\)") function, whose returned length is the number of java characters used to represent the string. 

For example, given the string 🇩🇰, the [`text:length()`](functions-text-length.html "text:length\(\)") function returns `1`, whereas the [`length()`](functions-length.html "length\(\)") function returns `4`. This is because 🇩🇰 is actually a grapheme cluster that consists of two Unicode code points, namely `U+1F1E9` (🇩) and `U+1F1F0` (🇰), which themselves are represented by 2 16-bit Java characters as [Java and the JVM encode strings using UTF-16](https://docs.oracle.com/en/java/javase/24/docs/api/java.base/java/lang/Character.html#unicode). 

### [`text:length()`](functions-text-length.html "text:length\(\)") Syntax Examples

This example shows how to compute the length of a string with emojis: 

logscale
    
    
    text:length(CommandLine)

If input data was `CommandLine=🎯data_exfil.zip📦→💾backup_srv🔓admin123🚨 `, it would return: 
    
    
    "_length"
    "38"

This example shows how to combine [`text:length()`](functions-text-length.html "text:length\(\)") with [`text:substring()`](functions-text-substring.html "text:substring\(\)") to remove a certain number of characters from each end of the string. In this case, to cut `5` characters from the beginning of the string, and `10` characters from the end: 

logscale
    
    
    text:substring(message, begin=5, end=text:length(message) - 10)

If input data for event 1 was `message="Courage the Cowardly Dog is an American animated comedy horror television series created by John R. Dilworth for Cartoon Network."` and input data for event 2 was `message="It's not easy bein' green."`, it would return: 
    
    
    "_substring"
    "ge the Cowardly Dog is an American animated comedy horror television series created by John R. Dilworth for Cartoo"
    "not easy be"

For more information about the used [_`begin`_](functions-text-substring.html#query-functions-text-substring-begin) and [_`end`_](functions-text-substring.html#query-functions-text-substring-end) parameters, see [`text:substring()`](functions-text-substring.html "text:substring\(\)"). 

### [`text:length()`](functions-text-length.html "text:length\(\)") Examples

Click + next to an example below to get the full details.

#### Count Characters Including Emojis in String

**Get string length including emojis using the[`text:length()`](functions-text-length.html "text:length\(\)") function **

##### Query

logscale
    
    
    text:length(CommandLine)

##### Introduction

In this example, the [`text:length()`](functions-text-length.html "text:length\(\)") function is used to count characters in a command line string that contains emojis. 

Example incoming data might look like this: 

CommandLine=🎯data_exfil.zip📦&rarr;💾backup_srv🔓admin123  
---  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         text:length(CommandLine)

Counts the total number of characters in the CommandLine field, counting each emoji as a single character, and returns the result in a new field named _length. 

  3. Event Result set.




##### Summary and Results

The query is used to determine the exact length of strings that may contain special characters or emojis. 

This query is useful, for example, to analyze command line lengths, validate string sizes, or identify unusually long commands that might indicate malicious activity. 

Sample output from the incoming example data: 

_length  
---  
38  
  
Note that each emoji is counted as a single character in the total length calculation. 

#### Extract Portion of Text From Message

**Extract specific characters from a message using the[`text:substring()`](functions-text-substring.html "text:substring\(\)") function with [`text:length()`](functions-text-length.html "text:length\(\)") **

##### Query

logscale
    
    
    text:substring(message, begin=4, end=text:length(message) - 4)

##### Introduction

In this example, the [`text:substring()`](functions-text-substring.html "text:substring\(\)") function is used with [`text:length()`](functions-text-length.html "text:length\(\)") to extract a portion of text from messages. It removes a certain number of characters from each end of the string using the _`begin`_ and _`end`_ parameters. 

Example incoming data might look like this: 

@timestamp| message  
---|---  
2025-08-06T10:15:00.000Z| The quick brown fox jumps over the lazy dog  
2025-08-06T10:15:01.000Z| Pack my box with five dozen liquor jugs  
2025-08-06T10:15:02.000Z| How vexingly quick daft zebras jump  
2025-08-06T10:15:03.000Z| The five boxing wizards jump quickly  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         text:substring(message, begin=4, end=text:length(message) - 4)

Extracts characters from the [message](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-action.html) field by: 

     * Starting at position 4 (the 5th character) 

     * Ending 4 characters before the end of the string, calculated by [`text:length()`](functions-text-length.html "text:length\(\)")

  3. Event Result set.




##### Summary and Results

The query is used to extract a portion of text by specifying start and end positions. 

This query is useful, for example, to extract specific parts of messages, remove certain number of characters from the beginning and end of strings, or process text of varying lengths. 

Sample output from the incoming example data: 

message| result  
---|---  
The quick brown fox jumps over the lazy dog| quick brown fox jumps over the lazy  
Pack my box with five dozen liquor jugs| k my box with five dozen liquor  
How vexingly quick daft zebras jump| vexingly quick daft zebras  
The five boxing wizards jump quickly| five boxing wizards jump quic  
  
Note that [`text:substring()`](functions-text-substring.html "text:substring\(\)") uses zero-based numbering, so position 4 refers to the 5th character in the string (after positions 0,1,2,3,4). The end position is calculated dynamically for each message based on its total length using [`text:length()`](functions-text-length.html "text:length\(\)"). 

#### Remove Fixed-Length Prefix and Suffix From Text

**Remove characters from both ends using the[`text:substring()`](functions-text-substring.html "text:substring\(\)") function with [`text:length()`](functions-text-length.html "text:length\(\)") **

##### Query

logscale
    
    
    text:substring(message, begin=7, end=text:length(message) - 9)

##### Introduction

In this example, the [`text:substring()`](functions-text-substring.html "text:substring\(\)") function is used with [`text:length()`](functions-text-length.html "text:length\(\)") to extract text starting from a fixed position and ending at a position calculated relative to the string's end. 

Example incoming data might look like this: 

@timestamp| message  
---|---  
2025-08-06T10:15:00.000Z| [START]Important message content here[END_NOW]  
2025-08-06T10:15:01.000Z| [START]Another test message here[END_NOW]  
2025-08-06T10:15:02.000Z| [START]Processing completed OK[END_NOW]  
2025-08-06T10:15:03.000Z| [START]Error in module XYZ[END_NOW]  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         text:substring(message, begin=7, end=text:length(message) - 9)

Extracts a portion of the [message](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-action.html) field using: 

     * A fixed starting position of 7 (skipping "[START]") 

     * A dynamic end position calculated by [`text:length()`](functions-text-length.html "text:length\(\)") getting the total length of the message and subtracting 9 characters (length of "[END_NOW]") 

This effectively removes both the prefix and suffix from the message. 

  3. Event Result set.




##### Summary and Results

The query is used to extract the main content from messages that have fixed-length prefixes and suffixes. 

This query is useful, for example, to clean up formatted log messages, extract the meaningful content from standardized message formats, or remove known wrapping text from strings. 

Sample output from the incoming example data: 

message| result  
---|---  
[START]Important message content here[END_NOW]| Important message content here  
[START]Another test message here[END_NOW]| Another test message here  
[START]Processing completed OK[END_NOW]| Processing completed OK  
[START]Error in module XYZ[END_NOW]| Error in module XYZ  
  
Note that [`text:substring()`](functions-text-substring.html "text:substring\(\)") uses zero-based numbering, so position 7 is actually the 8th character in the string. 

In the first event, the 8th character is, therefore, `I`: 
    
    
    [ S T A R T ] I
    0 1 2 3 4 5 6 7

The end position is calculated dynamically for each message based on its total length using [`text:length()`](functions-text-length.html "text:length\(\)").
