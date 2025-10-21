# Parser Sample Data | Crowdstrike Parsing Standard 1.1 | LogScale Documentation

**URL:** https://library.humio.com/logscale-parsing-standard/pasta-parser-guidelines-sample.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Crowdstrike Parsing Standard 1.1](pasta.html)

/ [Parser Guidelines](pasta-parser-guidelines.html)

### Parser Sample Data

We strongly recommend including sample data for tests in parsers and example data for demonstration purposes. 

Packages should not include any personally identifiable information (PII) and additionally we strive to not include 3rd party assets like company names/domain names/etc, unless they are directly related to the test. 

The following is a list of good sample data to be used in packages. For further inspiration we recommend looking at [Wikipedia's Placeholder names](https://en.wikipedia.org/wiki/Placeholder_name). 

#### Human names

We recommend using the name **John Doe** and **Jane Doe** in sample cases. 

#### Company names

  * **Acme** is a very common company name. 

  * **Octan** is a company that originates from a toy franchise which can also be used. 




#### Domain names

Name |  Purpose   
---|---  
`example.com` |  Completely generic domain that's reserved for example data, [RFC 2606](https://www.iana.org/go/rfc2606)  
`example.net` |  Completely generic domain that's reserved for example data, [RFC 2606](https://www.iana.org/go/rfc2606)  
`example.org` |  Completely generic domain that's reserved for example data, [RFC 2606](https://www.iana.org/go/rfc2606)  
`*.example` |  Top level domain reserved for related data, i.e. `acme.example.com`  
`mitre.org` |  Mitre is referenced in a lot of security use-cases and can be used in such cases.   
  
#### E-mail addresses

E-mail addresses can be almost any combination of human names and domain names within the rules of e-mail addresses: 

Address |  Purpose   
---|---  
`johndoe@example.com` |  a random private person   
`janedoe@acme.example` |  an employee of company Acme   
  
Note that `.`s are usually ignored (i.e. `jane.doe@example.com`) and `+` mail as well (i.e. `janedoe+urgent@example.com`) hence both schemes are allowed. 

##### Generic addresses

Common generic local parts are also allowed. This list is not exhaustive at this point, but here to provide some guidance. 

Address |  Purpose   
---|---  
`noreply@example.com` |  Commonly used email company mailbox   
`info@example.com` |  Commonly used company public mailbox   
`mailer-demon@example.com` |  System mailbox   
`postmaster@example.com` |  System mailbox   
`abuse@example.com` |  Abuse mailbox   
`webmaster@example.com` |  Homepage author mailbox, often from the 90s   
  
#### IP addresses

While IP addresses are public information, we again strive to not use any public routable IPs. A reason for that is we don't know the history of an IP address and have no control of how the data is being used. The safe option here is to make sure they can't be routed. 

##### Private networks

For local networks RFC 1918 networks should be used 

Block |  Purpose   
---|---  
`10.0.0.0/8` |  Private-Use Network   
`172.16.0.0/12` |  Private-Use Network   
`192.168.0.0/16` |  Private-Use Network   
`169.254.0.0/16`, `fe80::/10` |  Link-Local addresses   
`224.0.0.0/4` |  Multicast network. Typically used for devices to locate each other behind the same firewall   
`fc00::/7` |  Unique Local Addresses   
`ff00::/8` |  Multicast Addresses [RFC 4291](https://www.rfc-editor.org/rfc/rfc4291)  
  
##### Public networks

For public networks we generally only allow TEST-NET blocks, with a few exceptions. The list of exceptions is growing so please reach out to [humio_packages@crowdstrike.com](mailto:humio_packages@crowdstrike.com) if you have any additions. Generally we only allow IPs of services that are specific to an IP address, like DNS. 

Block |  Purpose   
---|---  
`192.0.2.0/24` |  TEST-NET-1, [RFC 5737](https://www.rfc-editor.org/rfc/rfc5737)  
`198.51.100.0/24` |  TEST-NET-2, [RFC 5737](https://www.rfc-editor.org/rfc/rfc5737)  
`203.0.113.0/24` |  TEST-NET-3, [RFC 5737](https://www.rfc-editor.org/rfc/rfc5737)  
`1.1.1.1`, `1.0.0.1` |  CloudFlare DNS   
`8.8.8.8`, `8.8.4.4` |  Google DNS   
`2001:db8::/32` |  Reserved for documentation and examples   
`2001:4860:4860::8888`, `2001:4860:4860::8844` |  Google DNS   
`2606:4700:4700::1111`, `2606:4700:4700::1001` |  CloudFoundry DNS
