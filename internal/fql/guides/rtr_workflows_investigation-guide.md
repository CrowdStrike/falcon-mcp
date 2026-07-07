Read-only RTR Investigation Guide

This guide helps agents use RTR safely for endpoint triage. The current RTR MCP module exposes
the read-only RTR command endpoint for host investigation. It does not expose RTR Admin,
Active Responder, remediation, or arbitrary script execution.

Recommended sequence:
1. Use Falcon detections, incidents, hosts, or NGSIEM to identify the host AID.
2. Use falcon_init_rtr_session to open or reuse a single-host RTR session.
3. Use falcon_run_rtr_read_only_command_and_wait for simple focused evidence collection.
4. Use falcon_execute_rtr_read_only_command plus falcon_check_rtr_command_status when you
   need manual control over request IDs, polling, or output sequence chunks.
5. Use falcon_search_rtr_audit_sessions when accountability or session history matters.
6. Use falcon_delete_rtr_session when the session is no longer needed.

Useful read-only command patterns:
- Processes: base_command=ps, command_string="ps"
- Directory listing: base_command=ls, command_string="ls C:\Path"
- File hash: base_command=filehash, command_string="filehash C:\Path\file.exe"
- File preview: base_command=cat, command_string="cat C:\Path\file.txt"
- Registry query: base_command=reg, command_string="reg query HKLM\Software\..."
- Network state: base_command=netstat, command_string="netstat"
- Event log review: base_command=eventlog, command_string="eventlog view Security 50"

Model behavior guidance:
- Prefer one host and one question at a time.
- Keep commands narrow and explain what evidence each command is collecting.
- Use audit and aggregation tools before broad RTR activity conclusions.
- Treat offline or queued behavior as a telemetry state, not proof the host is powered off.
- Do not attempt remediation, deletion, script execution, or active-response behavior through
  the read-only RTR tool.
