# Regular Expression Syntax Patterns | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/syntax-regex-syntax.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Language Syntax](syntax.html)

/ [Regular Expression Syntax](syntax-regex.html)

### Regular Expression Syntax Patterns

The following tables detail the supported functionality within LogScale compared to the standard JitRex or RE2J implementations. The tables detail each syntax and whether it is supported by LogScale. 

  * [Single Characters](syntax-regex-syntax.html#table_syntax-regex-characters "Table: Single Characters")

  * [Character Classes](syntax-regex-syntax.html#table_syntax-regex-character-classes "Table: Character Classes")

  * [Predefined Character Classes](syntax-regex-syntax.html#table_syntax-regex-character-predefined "Table: Predefined Character Classes")

  * [Logical Operators](syntax-regex-syntax.html#table_syntax-regex-logical-operators "Table: Logical Operators")

  * [Boundary Matchers](syntax-regex-syntax.html#table_syntax-regex-boundary-matchers "Table: Boundary Matchers")

  * [Quantifiers](syntax-regex-syntax.html#table_syntax-regex-quantifiers "Table: Quantifiers")

  * [Groups](syntax-regex-syntax.html#table_syntax-regex-groups "Table: Groups")

  * [Quotation](syntax-regex-syntax.html#table_syntax-regex-quotation "Table: Quotation")




The Single Characters table lists the single characters supported: 

**Table: Single Characters**

Syntax |  Description   
---|---  
`x` |  The character x   
`\\` |  The backslash character   
`\0n` |  The character with octal value 0n (0 <= n <= 7)   
`\0nn` |  The character with octal value 0nn (0 <= n <= 7)   
`\0mnn` |  The character with octal value 0nn (0 <= n <= 7)   
`\xhh` |  The character with hexadecimal value 0xhh   
`\uhhhh` |  The character with hexadecimal value 0xhhhh   
`\t` |  The tab character   
`\n` |  The newline character   
`\r` |  The carriage-return character   
`\f` |  The form-feed character   
`\a` |  The alert (bell) character   
`\cK` |  The control character ^K   
  
  


The Character Classes table lists the different character classes and ranges supported when needing to match multiple characters: 

**Table: Character Classes**

Syntax |  Description   
---|---  
`[abc]` |  a, b, or c (simple class)   
`[^abc]` |  Not a, b, or c (negated class)   
`[a-zA-Z]` |  a through z or A through Z, inclusive (range)   
  
  


The Pre-defined Character Classes table lists the character classes that cover multi-character groups such as whitespace, words or non-letter/digit characters: 

**Table: Predefined Character Classes**

Syntax |  Description   
---|---  
`.` |  Any character except newline (unless given flag `d`)   
`\d` |  A digit: [0-9]   
`\D` |  A non-digit: [^0-9]   
`\s` |  A whitespace character   
`\S` |  A non-whitespace character   
`\w` |  A word character: `[a-zA-Z_0-9]`  
`\W` |  A non-word character (inverse of above, equivalent to `[^a-zA-Z_0-9]`)   
  
  


The Logical Operators table lists logical matching operators: 

**Table: Logical Operators**

Syntax |  Description   
---|---  
`XY` |  X followed by Y   
`X|Y` |  Either X or Y   
  
  


The Boundary Matchers table lists the supported boundary matchers, such as word or line boundaries. See [m regex flag](syntax-regex-flags.html#syntax-regex-flags-m), which governs what is considered a line. 

**Table: Boundary Matchers**

Syntax |  Description   
---|---  
`^` |  The beginning of a line   
`$` |  The end of a line   
`\b` |  A word boundary   
`\B` |  A non-word boundary   
`\A` |  The beginning of the input   
`\Z` |  The end of the input but for the final [terminator](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/util/regex/Pattern.html#lt), if any   
`\z` |  The end of the input   
  
  


The Quantifiers table lists the quantifiers that provide numeric validation to a given character or character class: 

**Table: Quantifiers**

Syntax |  Description   
---|---  
`X?` |  X, once or not at all   
`X*` |  X, zero or more times   
`X+` |  X, one or more times   
`X{n}` |  X, exactly n times   
`X{n,}` |  X, at least n times   
`X{n,m}` |  X, at least n times but not more than m times   
`X??` |  X, once or not at all, prefer less   
`X*?` |  X, zero or more times, prefer less   
`X+?` |  Not supported   
`X{n}?` |  X, exactly n times   
`X{n,}?` |  X, at least n times, prefer less   
`X{n,m}?` |  X, at least n times but not more than m times, prefer less   
  
  


The Groups table lists the groups that support special matching rules for adding further explicit qualification within the regular expression: 

**Table: Groups**

Syntax |  Description |  Notes   
---|---|---  
`(X)` |  X, as a numbered capturing group |  Works as a non-capturing group.   
`(?<name>X)` |  X, as a named capturing group |  Note that LogScale supports a broader set of names than is usual (for example containing `#` and `@`).   
`(?P<name>X)` |  X, as a named capturing group |   
`(?:X)` |  X, as a non-capturing group |   
`(?flags)` |  Sets flags in the group |  Uses different flags to LogScale (see [Regular Expression Flags](syntax-regex-flags.html "Regular Expression Flags"))   
`(?flags:X)` |  Sets flags in X |  Uses different flags to LogScale (see [Regular Expression Flags](syntax-regex-flags.html "Regular Expression Flags"))   
`(?=X)` |  X, as a zero-width positive lookahead |   
`(?!X)` |  X, as a zero-width negative lookahead |   
  
  


The Quotation table lists methods for quoting special characters and regex characters within a regular expression: 

**Table: Quotation**

Syntax |  Description   
---|---  
`\` |  Quotes the following character for certain characters (for example regex meta-characters).   
`\Q` |  Quotes all characters until \E   
`\E` |  Ends quoting started by \Q
