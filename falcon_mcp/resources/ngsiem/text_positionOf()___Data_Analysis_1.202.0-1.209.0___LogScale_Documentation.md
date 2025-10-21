# text:positionOf() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-text-positionof.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Page was created:Sep 23, 2025

## [`text:positionOf()`](functions-text-positionof.html "text:positionOf\(\)")

The [`text:positionOf()`](functions-text-positionof.html "text:positionOf\(\)") function computes the position of a given character or substring within a string. [`text:positionOf()`](functions-text-positionof.html "text:positionOf\(\)") is particularly useful in combination with the [`text:substring()`](functions-text-substring.html "text:substring\(\)") function for more programmatically extracting snippets of another text (specific text segments from strings). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-text-positionof.html#query-functions-text-positionof-as)|  string| optional[a] | `_position`|  The name of the field to store the position in.   
[_`begin`_](functions-text-positionof.html#query-functions-text-positionof-begin)|  expression| optional[[a]](functions-text-positionof.html#ftn.table-functions-text-positionof-optparamfn) | `0`|  The position at which to begin searching the string for the given character or substring. Default to the start of the string (position `0`). Must be non-negative.   
[_`character`_](functions-text-positionof.html#query-functions-text-positionof-character)|  expression| required |  |  The character or substring of which to compute the position.   
[_`occurrence`_](functions-text-positionof.html#query-functions-text-positionof-occurrence)|  expression| optional[[a]](functions-text-positionof.html#ftn.table-functions-text-positionof-optparamfn) | `1`|  Which occurrence of the character or substring to find. Defaults to the first occurrence (`1`). Must be positive.   
[_`string`_](functions-text-positionof.html#query-functions-text-positionof-string)[b]| expression| required |  |  The string or field from which to compute the position of a character or substring.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`string`_](functions-text-positionof.html#query-functions-text-positionof-string) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`string`_](functions-text-positionof.html#query-functions-text-positionof-string) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     text:positionOf("value",character="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     text:positionOf(string="value",character="value")
> 
> These examples show basic structure only.

### [`text:positionOf()`](functions-text-positionof.html "text:positionOf\(\)") Function Operation

The [`text:positionOf()`](functions-text-positionof.html "text:positionOf\(\)") function uses zero-based numbering. In a string, `position 0` represents the first character. The last position equals the string length minus 1 (`text:length(string) - 1`). 

The [`text:positionOf()`](functions-text-positionof.html "text:positionOf\(\)") function works on extended grapheme clusters as defined by the [Unicode Standard Annex #29](https://www.unicode.org/reports/tr29/), specifically [ UAX29-C1-1](https://www.unicode.org/reports/tr29/#C1-1). That is, a position refers to what is usually considered to be a whole character by most users. For example, the character 🇩🇰 is actually a grapheme cluster that consists of two Unicode code points, namely `U+1F1E9` 🇩 and `U+1F1F0` 🇰, which themselves can further be represented by multiple characters depending on the encoding choice made by the programming language and platform. For Java and the JVM this is `UTF-16` as described in, for example, the [Java Character documentation](https://docs.oracle.com/en/java/javase/24/docs/api/java.base/java/lang/Character.html#unicode), meaning that each code point can be represented by up to two Java characters. This is why, for example, the [`length()`](functions-length.html "length\(\)") function reports the length of the 🇩🇰 character to be 4 bytes; each of the two code points that it consists of is furthermore represented by two 16-bit Java characters. 

### [`text:positionOf()`](functions-text-positionof.html "text:positionOf\(\)") Syntax Examples

This example shows how to compute the position of the `@` character in an email address: 

logscale
    
    
    text:positionOf(adress, character="@")>

If input data was `address=courage.the.cowardly.dog@example.com `, it would return: 
    
    
    "_position"
    "24"

This example shows how to combine [`text:positionOf()`](functions-text-positionof.html "text:positionOf\(\)") with [`text:substring()`](functions-text-substring.html "text:substring\(\)") to extract the local part of an email address: 

logscale
    
    
    text:substring(email, end=text:positionOf(email, character="@"), as=localPart)

If input data for event 1 was `email=kermit.the.frog@example.com`, input data for event 2 was `email=courage.the.cowardly.dog@example.com` and input data for event 3 was `email=samurai_jack@example.com `, it would return: 
    
    
    "localPart"
    "kermit.the.frog"
    "courage.the.cowardly.dog"
    "samurai_jack"

For more information about the used [_`end`_](functions-text-substring.html#query-functions-text-substring-end) parameter, see [`text:substring()`](functions-text-substring.html "text:substring\(\)"). 

This example shows how to extract the second entry of a CSV-file: 

logscale
    
    
    motor := text:substring(myCSV, begin=text:positionOf(myCSV, character=",") + 1, end=text:positionOf(myCSV, character=",", occurrence=2))

If input data was `myCSV="Bluesmobile,cop motor,440cu in,cop tires,cop suspension,cop shock"`, it would return: 
    
    
    "motor"
    "cop motor"

### [`text:positionOf()`](functions-text-positionof.html "text:positionOf\(\)") Examples

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
