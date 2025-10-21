# Differences from Other Regex Implementations | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/syntax-regex-diffs.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Language Syntax](syntax.html)

/ [Regular Expression Syntax](syntax-regex.html)

### Differences from Other Regex Implementations

There are many differences between the implementation within LogScale and other environments. The differences are categorized into two major groups; differences in how the regular expression is applied and how matching values are returned, and differences in the regular expression syntax: 

  * **Match String**

In other regular expression environments the string or variable to be searched be explicitly named. Within LogScale, the string used when matching a regular expression depends on the syntax or function being used: 

    * [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring)

The raw string of an event is used by default when using [`/regex/`](syntax-filters.html#syntax-filters-regex "Regular Expression Filters") or [`regex()`](functions-regex.html "regex\(\)"). 

    * All fields 

The [`/regex/`](syntax-filters.html#syntax-filters-regex "Regular Expression Filters") form searches all fields in an event. 

    * Single field 

A single field can be specified when using [`regex()`](functions-regex.html "regex\(\)") and the [_`field`_](functions-regex.html#query-functions-regex-field): 

logscale
          
          regex("fatal", field=errormsg)

This will explicitly search only the errormsg field within an event. 

Alternatively, you can use a regex match against a single field using: 

logscale
          
          errormsg = /fatal/

    * Array 

If you have an array, the [`array:regex()`](functions-array-regex.html "array:regex\(\)") function can be used to search using a regular expression across each element of the array. 

  * **Return Values**

As there is no implied language or procedure within the LogScale event search system, how the regular expressions are used and applied is adapted to apply within the CrowdStrike Query Language. 

    * **Event Filtering**

The simplest method of using and applying a regular expression is as a searching mechanism, when the regular expression is used to include or exclude events in the filter results. Within LogScale, the incoming stream of events is used as the basis of the comparison to the regular expression, with a matching event being included in the result set, and non-matching events dropped. This is identical within a procedural environment as an `if` or other logical comparison. 

For example, within Perl you might use: 

perl Syntax
          
          if ($string =~ /orgName/)
          ...

Or within Java: 

java Syntax
          
          Pattern pattern = Pattern.compile("orgName");
          Matcher matcher = pattern.matcher('{"actor":{"ip":"172.17.0.1","orgRoot"...');
          boolean matchFound = matcher.find();
          if (matchFound) ...

In both cases, this results in a logical result. 

Within LogScale, matching against the incoming stream of events is implied, so the CQL would simply be: 

logscale
          
          /orgName/

Note that the above searches the [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) of an event by default. To apply a regular expression to a specific field you would use: 

logscale
          
          LogScale = /orgName/

The output will only include events that match the supplied regular expression. 

    * **Data Extraction**

When extracting data with a regular expressio, the basic method is to identify a group within the regular expression to capture/extract the corresponding text string. Within LogScale the output must be a field in the event stream, since this is the only method of sharing a named value. Within a procedural language you would assign the value to a variable, like this expression within JavaScript: 

javascript
          
          const myRe = new RegExp("orgName=(b+)", "g");
          const myArray = myRe.exec(rawstring");

The `myArray` variable now contains zero or more matches of the value of the `orgName=**`value`**` key/value pair. 

Within LogScale, the name of the field for the capture group must be defined within the regular expression, since a the [`regex()`](functions-regex.html "regex\(\)") or [`/regex/`](syntax-filters.html#syntax-filters-regex "Regular Expression Filters") syntax does not return a value. Hence, the equivalent expression within CQL is: 

logscale
          
          /orgName=(?<myorgName>\w+?)/

This will extract the data into a new field from the original [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring). 

The resultant event stream now contains a new named field myorgName. 

Note that the field name `orgName` is placed before the named group expression capturing the value after the `=` sign. 

  * **Regex Flags**

CQL regular expressions support these flags, `d`, `g`, `i`, and `m`. Many other regular expression implementations support many more flags. 

For some flags, this requires a different or more explicit approach. 




#### Perl Compatible Regular Expressions (PCRE) Differences

As an interpreted language, the main differences between [regular expressions in Perl](https://perldoc.perl.org/perlre) and LogScale are about the implementation of the string used to when applying the regular expression, and how explicit elements are extracted. These differences are listed in the following: 

  * **Group Matching**

In scripting language environments, extracting of data into a named variable is performed through group definition within the regular expression and then capturing the groups when the regex is executed. For example, in Perl: 

perl
        
        my ($orgid, $orgname) = ($event =~ m{orgId=([^\s]+?) orgName=([^\s]+?)});

This code fragment would extract the `orgId` and `orgName` by matching the non-whitespace characters after the `=`, returning the two matching groups in order, which are then assigned to the two variables `$orgid` and `$orgname`. 

Within LogScale, fieldnames are specified within the regular expression as part of a named field extension. The equivalent in CQL would be: 

logscale
        
        /orgId=(?<orgId>[^\s]+) orgName=(?<orgName>[^\s]+)/

The name of the fields is in the angle brackets, and note that the `(?<name>)` is the group specification like the `()` syntax in Perl. 

  * **Global (Repeating) Matches**

Perl regular expressions support the notion of 'global' or repeating matches where a regular expression can match multiple times returning every occurrence by using the `g` flag. For example: 

perl
        
        my (@errors) = ($string =~ m/error=([a-z]+)/g);

Here the `g` indicates that Perl should match multiple times against the given expression, returning each match in the original string to the array. 

The `g` flag is supported within LogScale, but only when used against specific fields, or when extracting a value that creates a field. It cannot be used to match multiple times in the same event. 

Within CQL, you can also use the [_`repeat`_](functions-regex.html#query-functions-regex-repeat) argument: 

logscale
        
        regex("error=(?<errortext>[a-z]+)",repeat=true)

Will create multiple error fields in the event. 

### Important

The [`regex()`](functions-regex.html "regex\(\)") does not support the _`/g`_ regular expression flag; instead the [_`repeat`_](functions-regex.html#query-functions-regex-repeat) parameter must be used for global or repeating matches. 




#### JavaScript Regular Expression Differences

  * Within Javascript, the same could be achieved with the following code: 

javascript
        
        const regexp = /orgId=([^\s]+?) orgName=([^\s]+?)/;
        const matches = event.matchAll(regexp);

Here the `matches` variable is an array with each matching item. 

Within CQL, we can explicitly name the group matches: 

logscale
        
        /orgId=(?<orgId>[^\s]+) orgName=(?<orgName>[^\s]+)/

The name of the fields is in the angle brackets, and note that the `(?<name>)` is the group specification like the `()` syntax in Perl. 




#### re2 Regular Expressions Differences

Among the main differences between [Google RE2 regular expression syntax](https://github.com/google/re2/wiki/Syntax) and LogScale syntax there is: 

  * **Name Group Matching**

Google RE2 uses this syntax for named group matches: 

googleRE2 Syntax
        
        (?P<orgName>)

LogScale does not support this notation, but does support the simpler form: 

logscale Syntax
        
        (?<fieldname>)
