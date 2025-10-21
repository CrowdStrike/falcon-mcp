# replace() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-replace.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`replace()`](functions-replace.html "replace\(\)")

Replaces each substring of the specified fields value that matches the given regular expression with the given replacement. LogScale uses JitRex which closely follows the syntax of [re2j regular expressions](https://github.com/google/re2j), which has a syntax very close to Java's regular expressions. Check out LogScale [Regular Expression Syntax](syntax-regex.html "Regular Expression Syntax"). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-replace.html#query-functions-replace-as)|  string| optional[a] | `input field`|  Specifies the field to store the replaced string as.   
[_`field`_](functions-replace.html#query-functions-replace-field)|  string| optional[[a]](functions-replace.html#ftn.table-functions-replace-optparamfn) | `@rawstring`|  Specifies the field to run the replacement on.   
[_`flags`_](functions-replace.html#query-functions-replace-flags)|  string| optional[[a]](functions-replace.html#ftn.table-functions-replace-optparamfn) | [`m`](functions-replace.html#query-functions-replace-flags-value-m)|  Specifies other regex flags.   
|  |  | **Values**  
|  |  | [`d`](functions-replace.html#query-functions-replace-flags-value-d)| Period (.) includes newline characters  
|  |  | [`i`](functions-replace.html#query-functions-replace-flags-value-i)| Ignore case for matched values  
|  |  | [`m`](functions-replace.html#query-functions-replace-flags-value-m)| Multi-line parsing of regular expressions  
[ _`regex`_](functions-replace.html#query-functions-replace-regex)[b]| string| required |  |  The regular expression to match.   
[_`replacement`_](functions-replace.html#query-functions-replace-replacement)|  string| optional[[a]](functions-replace.html#ftn.table-functions-replace-optparamfn) | `""`|  The string to substitute for each match (same as _`with`_).   
[_`with`_](functions-replace.html#query-functions-replace-with)|  string| optional[[a]](functions-replace.html#ftn.table-functions-replace-optparamfn) | `""`|  The string to substitute for each match.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`regex`_](functions-replace.html#query-functions-replace-regex) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`regex`_](functions-replace.html#query-functions-replace-regex) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     replace("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     replace(regex="value")
> 
> These examples show basic structure only.

### [`replace()`](functions-replace.html "replace\(\)") Examples

Click + next to an example below to get the full details.

#### Get Integer Part of Number

**Get the integer part of a number using the[`regex()`](functions-regex.html "regex\(\)") function and regex capturing groups **

##### Query

logscale
    
    
    regex("(?<b>\\d+)\\..*",field=a)

##### Introduction

In this example, regex pattern matching with a named capturing group is used to look at a filename and find something after the backslash, then store it in a new field named b, leaving the original field a unchanged. 

See also alternative method mentioned under the summary. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         regex("(?<b>\\d+)\\..*",field=a)

Looks for a sequence of characters in a capturing group and replaces the character with a digit (number): \\\ backslash (\\) \d+ one or more digits \\\ backslash (\\) . any character .* zero or more characters. If the sequence of characters in an event looks like this `\folder58\` instead of `\folder58\a` , then there is no filename as nothing comes after the `\`. 

  3. Event Result set.




##### Summary and Results

The query with regex pattern matching and named capturing group is used to get the integer part of a number, storing the replacement (the matched value) automatically in a new field named b. This is useful when searching for specific filenames. 

The query using the [`regex()`](functions-regex.html "regex\(\)") function is primarily used for pattern matching and extraction as regex is generally very concise for simple extraction tasks. 

Alternative

There is another way of achieving the same end result using the [`replace()`](functions-replace.html "replace\(\)") function in a query like this: `replace("(\\d+)\\..*", with="$1", field=a, as=b)`. This query uses the replace function with numbered references to perform substitution, whereas the first one uses regex pattern matching with a named capture group. 

The query using [`replace()`](functions-replace.html "replace\(\)") captures digits before the decimal point in an unnamed group, and explicitly creates a new field b with the result (\\\d+). 

This query using the [`replace()`](functions-replace.html "replace\(\)") function is more used for string manipulation and transformation in a replacement operation. 

#### Replace Word or Substring With Another

**Replace a word or substring with another in an event set using the[`replace()`](functions-replace.html "replace\(\)") function with a regular expression **

##### Query

logscale
    
    
    replace(regex=propperties, with=properties)

##### Introduction

In this example, the [`replace()`](functions-replace.html "replace\(\)") function is used to correct a spelling mistake. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         replace(regex=propperties, with=properties)

Replaces the word `propperties` with the word `properties`. 

  3. Event Result set.




##### Summary and Results

The query is used to correct spelling mistakes in an event set. Changing words or other substrings like this with a regular expression is useful in many situations, where it is necessary to make quick changes of field values. 

#### Truncate a String or Message

**Truncate a string or message to exact 100 characters using[`replace()`](functions-replace.html "replace\(\)") function and regex capturing groups **

##### Query

logscale
    
    
    replace("^(.{100}).*", with="$1", field=message, as="truncated_message")

##### Introduction

In this example, the [`replace()`](functions-replace.html "replace\(\)") function together with regex capturing group, is used to truncate a string, chop of last part of a message, to only show the first `100` characters, replace the last character with a digit (number) at the end of the line. and then store the truncated string in the new field truncated_message, leaving the field message untouched. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         replace("^(.{100}).*", with="$1", field=message, as="truncated_message")

Captures group that matches exactly 100 characters of any type starting from the beginning of the line and replaces the last character at the end of the truncated string with a digit, then returns the truncated version in a new field named truncated_message. The original message field remains unchanged. 

`with="$1"` means that it replaces the entire match with the defined number of characters, in this case 100 characters. 

  3. Event Result set.




##### Summary and Results

The query is used to truncate strings. 

Truncation can, for example, be used to speed up download times and complete searches faster. In file systems, the truncate operation is used to reduce the size of a file by removing data from the end. This can be helpful when you need to reclaim storage space or when dealing with log files that need to be periodically truncated. 

Another advantage of truncation is, that it allows you to search for a word that could have multiple endings. This way it will broaden the results and look for variations of words. 

Truncation of numbers is also useful to shorten digits past a certain point in the number.
