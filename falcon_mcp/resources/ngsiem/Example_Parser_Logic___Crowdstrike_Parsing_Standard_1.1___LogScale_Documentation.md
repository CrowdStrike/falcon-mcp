# Example Parser Logic | Crowdstrike Parsing Standard 1.1 | LogScale Documentation

**URL:** https://library.humio.com/logscale-parsing-standard/pasta-parser-guidelines-parser-yaml.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Crowdstrike Parsing Standard 1.1](pasta.html)

/ [Parser Guidelines](pasta-parser-guidelines.html)

### Example Parser Logic

The following is an example of how to implement parser logic. This example is from the Ansible Parser, see [redhat/ansible](https://library.humio.com/integrations/integrations-redhat-ansible.html) for more information. 
    
    
    | case {
          // Play Recap
          remainder = /^PLAY RECAP/;
    
          // Play initiated
          remainder = /^PLAY\s\[(?<play>[^\]]+)/;
    
          // Task initiated
          remainder = /^TASK\s\[(?<task>[^\]]+)\]/;
    
          // Task completed on host
          remainder = /^(?<state>[^:]+)\:\s\[(?<host>[^\]]+)\]$/;
    
          // To parse events such as : 2022-11-03 17:01:27,374 p=692789 u=root n=ansible | [DEPRECATION WARNING]: The 'ec2'....
          //                           2023-04-18 10:28:30,681 p=22161 u=root n=ansible | [WARNING]:  * Failed to parse /tmp
          remainder = /^\[(?<warning>(WARNING)|(.*\sWARNING)+)\]\:\s(?<details>.*)$/;
    
          // To parse events such as : 2022-11-23 02:19:24,584 p=1273538 u=root n=ansible | ok: [localhost -> 184.169.203.139] => (item=...
          remainder = /^(?<state>[^:]+)\:\s\[(?<host>\S+) -> (?<delegatedHost>[^\]]+)\]\s\=>\s(?<details>.*)$/;
    
          // To parse events such as: 2022-11-03 17:23:19,811 p=693741 u=root n=ansible | changed: [localhost] => (item={'id': 'i-043deb1385cedee11', 'ami_launch_index': '0' ...
          remainder = /^(?<state>[^:]+)\:\s\[(?<host>[^\]]+)\]\s\=>\s(?<details>.*)$/;
    
          // To parse events such as : 2022-12-27 16:00:01,833 p=1805354 u=root n=ansible | Using /etc/ansible/ansible.cfg as config file
          remainder = /^Using\s(?<configFile>.+)\sas\s/;
    
          // To parse events such as : 2022-09-08 16:18:08,002 p=211339 u=root n=ansible | fatal: [203.0.113.168]: FAILED! => {"changed": ...
          remainder = /^(?<state>[^:]+)\:\s\[(?<host>[^]]+)\]\:\s(?<reason>[^\!]+)\!\s=>\s(?<details>.*)$/;
    
          // To parse events like: 2023-04-18 10:28:30,737 p=22161 u=root n=ansible | skipping: no hosts matched
          remainder = /^skipping\:\s(?<details>.*)$/ | state := "skipping";
    
          // To parse events such as : 2022-11-03 17:00:55,846 p=692788 u=root n=ansible | 203.0.113.05: ok=0    changed=0    unreachable=1    failed=0    skipped=0    rescued=0    ignored=0
          remainder = /^(?<host>\S*)\s*\:\s+(?<statuses>.*)$/
              | kvparse(field=statuses)
              | drop(statuses);
    
          // To parse events like: 2023-04-18 12:20:16,099 p=31428 u=root n=ansible | ...ignoring
          remainder = "...ignoring" | failureIgnored := "true";
    
          // To parse events like: 2023-01-18 15:00:44,510 p=2165722 u=root n=ansible | Install apache --------------------------------------------------------- 13.73s
          remainder = /^(?<task>.+?)\s-*\s(?<duration>.+)$/;
    
          *
      }
