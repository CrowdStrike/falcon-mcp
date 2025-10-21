# text:substring() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-text-substring.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Page was created:Sep 23, 2025

## [`text:substring()`](functions-text-substring.html "text:substring\(\)")

The [`text:substring()`](functions-text-substring.html "text:substring\(\)") function extracts a substring from a string based on specified start and end positions. 

[`text:substring()`](functions-text-substring.html "text:substring\(\)") is, for example, useful for: 

  * Extracting parts of email addresses (local-part or domain). 

  * Getting segments of URIs (authority or path). 

  * Parsing fixed-format data strings. 

  * Extracting date components, for example the year of a date an so on. 




Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-text-substring.html#query-functions-text-substring-as)|  string| optional[a] | `_string`|  The name of the field to store the substring in.   
[_`begin`_](functions-text-substring.html#query-functions-text-substring-begin)|  expression| optional[[a]](functions-text-substring.html#ftn.table-functions-text-substring-optparamfn) | `0`|  The starting position of the substring in the original string. Starts from `0`. Defaults to the start of the string (`position 0`).   
[_`end`_](functions-text-substring.html#query-functions-text-substring-end)|  expression| optional[[a]](functions-text-substring.html#ftn.table-functions-text-substring-optparamfn) |  |  The end position of the substring in the original string. Must be positive. Defaults to the end of the string.   
[_`string`_](functions-text-substring.html#query-functions-text-substring-string)[b]| expression| required |  |  The string or field from which to compute the substring.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`string`_](functions-text-substring.html#query-functions-text-substring-string) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`string`_](functions-text-substring.html#query-functions-text-substring-string) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     text:substring("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     text:substring(string="value")
> 
> These examples show basic structure only.

### [`text:substring()`](functions-text-substring.html "text:substring\(\)") Function Operation

The [`text:substring()`](functions-text-substring.html "text:substring\(\)") function extracts a portion of text from a string using zero-based numbering. The start of the string has position `0` (first character position is `0`). 

The substring starts at position `begin` and extends to the character at position `end - 1`, meaning that the substring has length of [_`end`_](functions-text-substring.html#query-functions-text-substring-end) \- [_`begin`_](functions-text-substring.html#query-functions-text-substring-begin). 

For example, `begin=0` and `end=4`, returns the characters at position `0`, `1`, `2`, and `3`. 

The [`text:substring()`](functions-text-substring.html "text:substring\(\)") function works on extended grapheme clusters as defined by the [Unicode Standard Annex #29](https://www.unicode.org/reports/tr29/), specifically [ UAX29-C1-1](https://www.unicode.org/reports/tr29/#C1-1). That is, a position refers to what is usually considered to be a whole character by most users. For example, the character 🇩🇰 is actually a grapheme cluster that consists of two Unicode code points, namely `U+1F1E9` 🇩 and `U+1F1F0` 🇰, which themselves can further be represented by multiple characters depending on the encoding choice made by the programming language and platform. For Java and the JVM this is `UTF-16` as described in, for example, the [Java Character documentation](https://docs.oracle.com/en/java/javase/24/docs/api/java.base/java/lang/Character.html#unicode), meaning that each code point can be represented by up to two Java characters. This is why, for example, the [`length()`](functions-length.html "length\(\)") function reports the length of the 🇩🇰 character to be 4 bytes; each of the two code points that it consists of is furthermore represented by two 16-bit Java characters. 

#### Invalid Parameter Handling

The system passes events unchanged when the [_`string`_](functions-text-substring.html#query-functions-text-substring-string), [_`begin`_](functions-text-substring.html#query-functions-text-substring-begin) or [_`end`_](functions-text-substring.html#query-functions-text-substring-end) parameters contain invalid values. In these cases, the system does not add the field specified by the [_`as`_](functions-text-substring.html#query-functions-text-substring-as) argument. 

Valid parameter values: 

  * [_`string`_](functions-text-substring.html#query-functions-text-substring-string) parameter: Accepts existing field references or string literals. 

  * [_`begin`_](functions-text-substring.html#query-functions-text-substring-begin) parameter: Accepts non-negative numbers that are less than or equal to the string length. 

  * [_`end`_](functions-text-substring.html#query-functions-text-substring-end): Accepts positive numbers that are less than or equal to the string length. 




### [`text:substring()`](functions-text-substring.html "text:substring\(\)") Syntax Examples

As an example, consider the data string `6800091A3C5B78F4468` that is an instance of the following data format: 

It can be broken into: 

  * The first 2 characters represent the ID for the producer of the data. 

  * The next 4 characters denote the payload length, let this value be N. 

  * The next N characters encode the data. 

  * The remaining M characters represent the transaction ID that produced the data. 

  * The given data string `6800091A3C5B78F4468` can then be broken into: 

  * The id: 68 

  * The payload length: 0009 

  * The payload: 1A3C5B78F 

  * The transaction ID: 4468 




Since the payload length `N` and the length of the transaction ID `M` are both variable, LogScale regexes cannot properly extract the payload. Instead, you can extract the payload length and use [`text:substring()`](functions-text-substring.html "text:substring\(\)") to extract the rest. 

This example shows how to extract components from a fixed format data string where the payload length is variable: 

logscale
    
    
    // Break the data string into its components
    | data = /^(?<id>\d{2})(?<payloadLength>\d{4})(?<remaining>.*)$/
    | payload := text:substring(remaining, end=payloadLength)
    | transactionID := text:substring(remaining, begin=payloadLength)

If input data for event 1 was `data=6800091A3C5B78F4468` and input data for event 2 was `data=420004E2E228930`, it would return: 
    
    
    "data","id","payload","payloadLength","remaining","transactionID"
    "6800091A3C5B78F4468","68","1A3C5B78F","0009","1A3C5B78F4468","4468"
    "420004E2E228930","42","E2E2","0004","E2E228930","28930"

This example shows how to combine [`text:substring()`](functions-text-substring.html "text:substring\(\)") with [`text:positionOf()`](functions-text-positionof.html "text:positionOf\(\)") to extract the local part of an email address: 

logscale
    
    
    text:substring(email, end=text:positionOf(email, character="@"), as=localPart)

If input data for event 1 was `email=kermit.the.frog@example.com`, input data for event 2 was `email=courage.the.cowardly.dog@example.com` and input data for event 3 was `email=samurai_jack@example.com `, it would return: 
    
    
    "localPart"
    "kermit.the.frog"
    "courage.the.cowardly.dog"
    "samurai_jack"

This example shows how to combine [`text:substring()`](functions-text-substring.html "text:substring\(\)") with [`text:length()`](functions-text-length.html "text:length\(\)") to remove a certain number of characters from each end of the string. In this case, to cut `5` characters from the beginning of the string, and `10` characters from the end: 

logscale
    
    
    text:substring(message, begin=5, end=text:length(message) - 10)

If input data for event 1 was `message="Courage the Cowardly Dog is an American animated comedy horror television series created by John R. Dilworth for Cartoon Network."` and input data for event 2 was `message="It's not easy bein' green."`, it would return: 
    
    
    "_substring"
    "ge the Cowardly Dog is an American animated comedy horror television series created by John R. Dilworth for Cartoo"
    "not easy be"

### [`text:substring()`](functions-text-substring.html "text:substring\(\)") Examples

Click + next to an example below to get the full details.

#### Extract Alert Type From Security Event String Using Substring With Position-based Delimiters

**Extract alert type from a security event string using the[`text:substring()`](functions-text-substring.html "text:substring\(\)") function with [`text:positionOf()`](functions-text-positionof.html "text:positionOf\(\)") **

##### Query

logscale
    
    
    alertType := text:substring(securityEvent, begin=text:positionOf(securityEvent, character=",", occurrence=1) + 1, end=text:positionOf(securityEvent, character=",", occurrence=2))

##### Introduction

In this example, the [`text:substring()`](functions-text-substring.html "text:substring\(\)") and [`text:positionOf()`](functions-text-positionof.html "text:positionOf\(\)") functions work together to extract the alert type from a security event string. The [`text:positionOf()`](functions-text-positionof.html "text:positionOf\(\)") function finds the positions of comma delimiters, which are then used by [`text:substring()`](functions-text-substring.html "text:substring\(\)") to extract the text between them. 

Example incoming data might look like this: 

@rawstring| @timestamp  
---|---  
securityEvent="ALERT,malware_detected,endpoint123,trojan.exe,high_risk"| 1757568587006  
securityEvent="ALERT,brute_force_attempt,server456,ssh_service,medium_risk"| 1757568587006  
securityEvent="ALERT,suspicious_process,endpoint789,unusual_powershell,medium_risk"| 1757568587006  
securityEvent="ALERT,data_exfiltration,endpoint234,large_upload,high_risk"| 1757568587006  
securityEvent="ALERT,ransomware_behavior,endpoint567,encryption_activity,critical_risk"| 1757568587006  
securityEvent="ALERT,privilege_escalation,server789,sudo_abuse,high_risk"| 1757568587006  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         alertType := text:substring(securityEvent, begin=text:positionOf(securityEvent, character=",", occurrence=1) + 1, end=text:positionOf(securityEvent, character=",", occurrence=2))

Extracts the second field from the security event string using two functions: 

     * The [`text:positionOf()`](functions-text-positionof.html "text:positionOf\(\)") function is used twice on the securityEvent field: 

       * First to find the position of the first comma by setting [_`occurrence`_](functions-text-positionof.html#query-functions-text-positionof-occurrence)=1 

       * Then to find the position of the second comma by setting [_`occurrence`_](functions-text-positionof.html#query-functions-text-positionof-occurrence)=2 

     * The [`text:substring()`](functions-text-substring.html "text:substring\(\)") function then extracts the text between these positions: 

       * The [_`begin`_](functions-text-substring.html#query-functions-text-substring-begin) parameter is set to the position after the first comma (adding 1 to skip the comma) 

       * The [_`end`_](functions-text-substring.html#query-functions-text-substring-end) parameter is set to the position of the second comma 

The results are returned in a new field named alertType that contains the actual alert type (such as `malware_detected` or `brute_force_attempt`) extracted from the securityEvent field. 

Alternatively, the string could also be: `| alertType := text:substring(securityEvent, begin=text:positionOf(securityEvent, character=",") + 1, end=text:positionOf(securityEvent, character=",", occurrence=2))`. The difference is, that the string in the example makes it possible to extract, for example, `malware_detected,endpoint123` by using `occurrence=1` and `occurrence=3`. 

  3. Event Result set.




##### Summary and Results

The query is used to extract the specific alert type from a security event string by finding the positions of the delimiter characters and then extracting the text between them. 

This query is useful, for example, to parse specific alert types from security event strings where the data is embedded in a single field with comma-separated values. This is common in security logs where multiple pieces of information are combined into a single event string. 

Sample output from the incoming example data: 

alertType| securityEvent  
---|---  
malware_detected| ALERT,malware_detected,endpoint123,trojan.exe,high_risk  
brute_force_attempt| ALERT,brute_force_attempt,server456,ssh_service,medium_risk  
suspicious_process| ALERT,suspicious_process,endpoint789,unusual_powershell,medium_risk  
data_exfiltration| ALERT,data_exfiltration,endpoint234,large_upload,high_risk  
ransomware_behavior| ALERT,ransomware_behavior,endpoint567,encryption_activity,critical_risk  
privilege_escalation| ALERT,privilege_escalation,server789,sudo_abuse,high_risk  
  
Note that the extracted values in the alertType field contains the actual alert types, making it easier to analyze and categorize different types of security incidents. 

To extract other parts of the security event string, you could create similar queries with different [_`occurrence`_](functions-text-positionof.html#query-functions-text-positionof-occurrence) values. For example, to get the affected endpoint, use `occurrence=2` and `occurrence=3`, or for the risk level, use the last two comma positions. 

#### Extract Components from Fixed-Length Data

**Extract Components from Variable Length Data using the[`text:substring()`](functions-text-substring.html "text:substring\(\)") function with regex **

##### Query

logscale
    
    
    data = /^(?<id>\d{2})(?<payloadLength>\d{4})(?<remaining>.+)$/
    payload := text:substring(remaining, end=payloadLength)
    transactionID := text:substring(remaining, begin=payloadLength)

##### Introduction

In this example, the [`text:substring()`](functions-text-substring.html "text:substring\(\)") function is used with a regular expression to break down variable-length data strings into their component parts based on predefined positions and lengths. 

Example incoming data might look like this: 

@timestamp| data  
---|---  
2025-08-06T10:15:00.000Z| 6800091A3C5B78F4468  
2025-08-06T10:15:01.000Z| 420004E2E228930  
2025-08-06T10:15:02.000Z| 7800123ABC45DE6789  
2025-08-06T10:15:03.000Z| 910007DEFG89HI1234  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         data = /^(?<id>\d{2})(?<payloadLength>\d{4})(?<remaining>.+)$/

Uses a regular expression to parse the data field with these capture groups: 

     * id: `^` matches the start of the string, followed by `\d{2}` which captures exactly two digits. 

     * payloadLength: `\d{4}` captures exactly four digits after the id. 

     * remaining: `.+` captures one or more of any character until `$` (end of string). 

The regex pattern ensures that the entire string matches this format with no additional characters before or after, due to the `^` (start) and `$` (end) anchors. 

  3. logscale
         
         payload := text:substring(remaining, end=payloadLength)

Extracts a substring from the remaining field starting at position 0 and ending at the position specified by payloadLength (extracted by the regular expression in the previous line) and returns the result in a new field named payload. 

The [_`end`_](functions-text-substring.html#query-functions-text-substring-end) parameter specifies the exclusive end position of the substring. 

  4. logscale
         
         transactionID := text:substring(remaining, begin=payloadLength)

Extracts a substring from the remaining field starting at the position specified by payloadLength until the end of the string and returns the result in a new field named transactionID. 

The [_`begin`_](functions-text-substring.html#query-functions-text-substring-begin) parameter specifies the inclusive start position of the substring. 

  5. Event Result set.




##### Summary and Results

The query is used to parse variable-length data strings where different portions of the string represent specific pieces of information in a predefined format. 

This query is useful, for example, to process type-length-value like data formats, which are common in network protocols, or any variable-length formatted messages where different segments of the data have specific meanings based on their position and length. 

Sample output from the incoming example data: 

data| id| payload| payloadLength| remaining| transactionID  
---|---|---|---|---|---  
6800091A3C5B78F4468| 68| 1A3C5B78F| 0009| 1A3C5B78F4468| 4468  
420004E2E228930| 42| E2E2| 0004| E2E228930| 28930  
7800123ABC45DE6789| 78| 3ABC45DE6789| 0012| 3ABC45DE6789| <no value>  
910007DEFG89HI1234| 91| DEFG89H| 0007| DEFG89HI1234| I1234  
  
Note that the payloadLength field determines exactly how many characters to extract for the payload field. When the payloadLength equals the length of remaining, then the transactionID field will be empty. 

Also note that the payload and transactionID fields together make up the complete remaining field. 

#### Extract Email Local Part

**Extract email username using the[`text:substring()`](functions-text-substring.html "text:substring\(\)") function with [`text:positionOf()`](functions-text-positionof.html "text:positionOf\(\)") **

##### Query

logscale
    
    
    text:substring(email, end=text:positionOf(email, character="@"), as=localPart)

##### Introduction

In this example, the [`text:substring()`](functions-text-substring.html "text:substring\(\)") function is used together with [`text:positionOf()`](functions-text-positionof.html "text:positionOf\(\)") to extract the local part of email addresses. The [`text:positionOf()`](functions-text-positionof.html "text:positionOf\(\)") function returns the location of a character or substring in a string, in this case, the position of the `@` character. 

Example incoming data might look like this: 

@timestamp| email  
---|---  
2025-08-06T10:15:00.000Z| john.doe@example.com  
2025-08-06T10:15:01.000Z| jane.smith@company.org  
2025-08-06T10:15:02.000Z| support@service.net  
2025-08-06T10:15:03.000Z| user123@domain.com  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         text:substring(email, end=text:positionOf(email, character="@"), as=localPart)

Extracts the local part (the portion before the domain) of an email address using two nested functions: 

     * The [`text:positionOf()`](functions-text-positionof.html "text:positionOf\(\)") function finds the position of the `@` character in the email field using the [_`character`_](functions-text-positionof.html#query-functions-text-positionof-character) parameter. 

     * The [`text:substring()`](functions-text-substring.html "text:substring\(\)") function extracts all characters from the start of the string up to (but not including) the `@` position (defined by the [_`end`_](functions-text-substring.html#query-functions-text-substring-end) parameter), and returns the result in a new field named localPart. 

  3. Event Result set.




##### Summary and Results

The query is used to extract the username portion of email addresses by dynamically finding the `@` symbol position and extracting everything before it. 

This query is useful, for example, to analyze email patterns, group by usernames, or standardize email processing while keeping only the local part. 

Sample output from the incoming example data: 

email| localPart  
---|---  
john.doe@example.com| john.doe  
"jane.smith@company.org,"jane.smith"|   
support@service.net| support  
user123@domain.com| user123  
  
Note that the [`text:substring()`](functions-text-substring.html "text:substring\(\)") function's [_`end`_](functions-text-substring.html#query-functions-text-substring-end) parameter is exclusive, ensuring the @ symbol is not included in the extracted local part. 

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

#### Extract a Field From CSV String

**Extract data between specific commas using the[`text:substring()`](functions-text-substring.html "text:substring\(\)") function with [`text:positionOf()`](functions-text-positionof.html "text:positionOf\(\)") **

##### Query

logscale
    
    
    motor := text:substring(myCSV, begin=text:positionOf(myCSV, character=",") + 1, end=text:positionOf(myCSV, character=",", occurrence=2))

##### Introduction

In this example, the functions are used together to extract the second field from a CSV string by finding the positions of the first and second commas. 

Example incoming data might look like this: 

@rawstring| @timestamp  
---|---  
myCSV="Bluesmobile,cop motor,440cu in,cop tires,cop suspension,cop shock"| 1757503124225  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         motor := text:substring(myCSV, begin=text:positionOf(myCSV, character=",") + 1, end=text:positionOf(myCSV, character=",", occurrence=2))

Extracts the second field from the CSV string using: 

     * The [_`begin`_](functions-text-positionof.html#query-functions-text-positionof-begin) position is set to one character after the first comma (adding 1 to skip the comma itself) 

     * The _`end`_ position is set to the second comma's position 

     * The [_`occurrence`_](functions-text-positionof.html#query-functions-text-positionof-occurrence) parameter is used to find the second comma in the string 

The result - the extracted text - is returned in a new field named motor. 

  3. Event Result set.




##### Summary and Results

The query extracts text between the first and second commas in a CSV string. 

This query is useful when working with CSV data where you need to extract specific fields based on their position in the string. 

Sample output from the incoming example data: 

motor| myCSV  
---|---  
cop motor| Bluesmobile,cop motor,440cu in,cop tires,cop suspension,cop shock  
  
Note that [`text:positionOf()`](functions-text-positionof.html "text:positionOf\(\)") returns the position of the specified character, and adding 1 to the begin position skips over the comma itself. 

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
