# Deploying to Amazon Bedrock AgentCore

## Prerequisites

### Environment Variables

Create an API key in the CrowdStrike platform with the necessary scopes as outlined in [Available Modules, Tools & Resources](https://github.com/CrowdStrike/falcon-mcp/tree/main?tab=readme-ov-file#available-modules-tools--resources) for the modules you intend to load with the MCP server. You'll use the output as values for the following environment variables when deploying the agent:

- `FALCON_CLIENT_ID`
- `FALCON_CLIENT_SECRET`
- `FALCON_BASE_URL`

### VPC Requirements

We recommend deploying the MCP Server in an existing VPC used for your agentic tools. Your VPC must have:

- An Internet Gateway or NAT Gateway
- Outbound communication allowed to `api.crowdstrike.com`

## IAM Configuration

You'll need to run the MCP server with the necessary policies and trust permissions on the execution role. The policies below provide the required permissions for the MCP server to function properly within the Bedrock AgentCore environment.

**Important**: Replace all placeholder values (e.g., `{{region}}`, `{{accountId}}`, `{{agentName}}`) with values specific to your environment.

### IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ECRImageAccess",
      "Effect": "Allow",
      "Action": ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"],
      "Resource": [
        "arn:aws:ecr:{{region}}:709825985650:repository/crowdstrike/falcon-mcp"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["logs:DescribeLogStreams", "logs:CreateLogGroup"],
      "Resource": [
        "arn:aws:logs:{{region}}:{{accountId}}:log-group:/aws/bedrock-agentcore/runtimes/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["logs:DescribeLogGroups"],
      "Resource": ["arn:aws:logs:{{region}}:{{accountId}}:log-group:*"]
    },
    {
      "Effect": "Allow",
      "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
      "Resource": [
        "arn:aws:logs:{{region}}:{{accountId}}:log-group:/aws/bedrock-agentcore/runtimes/*:log-stream:*"
      ]
    },
    {
      "Sid": "ECRTokenAccess",
      "Effect": "Allow",
      "Action": ["ecr:GetAuthorizationToken"],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "xray:PutTraceSegments",
        "xray:PutTelemetryRecords",
        "xray:GetSamplingRules",
        "xray:GetSamplingTargets"
      ],
      "Resource": ["*"]
    },
    {
      "Effect": "Allow",
      "Resource": "*",
      "Action": "cloudwatch:PutMetricData",
      "Condition": {
        "StringEquals": {
          "cloudwatch:namespace": "bedrock-agentcore"
        }
      }
    },
    {
      "Sid": "GetAgentAccessToken",
      "Effect": "Allow",
      "Action": [
        "bedrock-agentcore:GetWorkloadAccessToken",
        "bedrock-agentcore:GetWorkloadAccessTokenForJWT",
        "bedrock-agentcore:GetWorkloadAccessTokenForUserId"
      ],
      "Resource": [
        "arn:aws:bedrock-agentcore:{{region}}:{{accountId}}:workload-identity-directory/default",
        "arn:aws:bedrock-agentcore:{{region}}:{{accountId}}:workload-identity-directory/default/workload-identity/{{agentName}}-*"
      ]
    }
  ]
}
```

### IAM Trust Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AssumeRolePolicy",
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock-agentcore.amazonaws.com"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "{{accountId}}"
        },
        "ArnLike": {
          "aws:SourceArn": "arn:aws:bedrock-agentcore:{{region}}:{{accountId}}:*"
        }
      }
    }
  ]
}
```
