# Comments | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/syntax-comments.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Language Syntax](syntax.html)

## Comments

The CrowdStrike Query Language (CQL) supports both single-line and multi-line commenting capabilities for code documentation. Single-line comments using // are ideal for end-of-line annotations, while multi-line comments using /* */ allow for more detailed search descriptions and comprehensive documentation within queries. 

The CrowdStrike Query Language (CQL) supports // single-line and /* multi-line */ comments. 

Single-line comments should be used at the end of a line, for example: 

logscale
    
    
    #host=github #parser=json 
    | // Search for host and parser
    repo.name=docker/*
    | groupBy(repo.name, function=count()) 
    | sort()

Multi-line comments are useful to provide a deeper description or documentation for a search. For example: 

logscale
    
    
    /* Search for killed processes
       Set the <signal> type and <process> name */
    ?{signal="*" }
    | ?{process="*"}
    | /Service exited due to (?<signal>\S+)/
    | signal = ?signal
    | /sent by (?<process>\S+)\[\d+\]/
    | process = ?process
