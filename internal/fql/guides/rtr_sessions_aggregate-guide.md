RTR Session Aggregation Guide

Use falcon_aggregate_rtr_sessions to summarize RTR session activity without pulling every
individual session record.

Recommended aggregation fields:
- hostname: Which hosts have the most RTR activity
- aid: Which host agent IDs have RTR activity
- user_id: Which Falcon users or API clients created sessions
- origin: Which integration or source created sessions
- base_command: Which RTR commands are most common
- created_at: Time-based activity buckets with aggregate_type=date_range

Recommended filters:
- created_at:>'now-7d'
- user_id:'@me'
- hostname:'DC*'
- offline_queued:true
- commands_queued:true

Example terms aggregation:
- aggregate_type: terms
- field: base_command
- filter: created_at:>'now-7d'
- size: 10

Example date range aggregation:
- aggregate_type: date_range
- field: created_at
- date_ranges: [{"from": "now-7d", "to": "now"}]

Use this before detailed searches when the user asks "how much", "which hosts", "which users",
or "what commands" across many RTR sessions.
