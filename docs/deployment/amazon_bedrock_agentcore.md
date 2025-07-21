# Deploying to Amazon Bedrock AgentCore

This guide walks you through deploying the Falcon MCP Server to Amazon Bedrock AgentCore. You'll configure the necessary AWS resources, set up IAM permissions, and prepare your environment.

## Prerequisites

Before deploying to Amazon Bedrock AgentCore, ensure you have your CrowdStrike API credentials and AWS environment properly configured.

### CrowdStrike API Credentials

You'll need to create API credentials in the CrowdStrike platform with the appropriate scopes for your intended use case.

1. **Create API Key**: Generate an API key in the CrowdStrike platform with the necessary scopes as outlined in [Available Modules, Tools & Resources](https://github.com/CrowdStrike/falcon-mcp/tree/main?tab=readme-ov-file#available-modules-tools--resources)

2. **Prepare Environment Variables**: You'll configure these values during agent deployment:
   - `FALCON_CLIENT_ID` - Your CrowdStrike API client ID
   - `FALCON_CLIENT_SECRET` - Your CrowdStrike API client secret
   - `FALCON_BASE_URL` - Your CrowdStrike API base URL (region-specific)

### AWS VPC Requirements

The MCP Server requires internet connectivity to communicate with CrowdStrike's APIs. We recommend deploying in an existing VPC used for your agentic tools.

**Required VPC Configuration:**

- **Internet Gateway or NAT Gateway** - Enables outbound internet connectivity
- **Outbound HTTPS Access** - Allow communication to `api.crowdstrike.com` on port 443
- **Security Groups** - Configure appropriate security group rules for your network requirements

## IAM Configuration

The MCP server requires specific IAM permissions to function within the Amazon Bedrock AgentCore environment. You'll create an execution role with the necessary policies and trust relationships.

> [!IMPORTANT]
> Replace all placeholder values with your specific environment details:
>
> - `{{region}}` - Your AWS region (e.g., `us-east-1`)
> - `{{accountId}}` - Your AWS account ID
> - `{{agentName}}` - Your agent name with no spaces or special characters (e.g., `falcon`). You'll need to decide the agent name **before** creating the role and AgentCore Runtime.

### Step 1: Create the IAM Execution Role

Create an IAM role with the following policy that grants the necessary permissions for container access, logging, monitoring, and Bedrock operations:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ECRImageAccess",
      "Effect": "Allow",
      "Action": [
        "ecr:BatchGetImage",
        "ecr:GetDownloadUrlForLayer"
      ],
      "Resource": [
        "arn:aws:ecr:us-east-1:709825985650:repository/crowdstrike/falcon-mcp"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:DescribeLogStreams",
        "logs:CreateLogGroup"
      ],
      "Resource": [
        "arn:aws:logs:{{region}}:{{accountId}}:log-group:/aws/bedrock-agentcore/runtimes/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:DescribeLogGroups"
      ],
      "Resource": [
        "arn:aws:logs:{{region}}:{{accountId}}:log-group:*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": [
        "arn:aws:logs:{{region}}:{{accountId}}:log-group:/aws/bedrock-agentcore/runtimes/*:log-stream:*"
      ]
    },
    {
      "Sid": "ECRTokenAccess",
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken"
      ],
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
      "Resource": [
        "*"
      ]
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
    },
    {
      "Sid": "BedrockModelInvocation",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/*",
        "arn:aws:bedrock:{{region}}:{{accountId}}:*"
      ]
    }
  ]
}
```

> [!NOTE]
> Save the ARN of the IAM role - you'll need it for the deployment of the Amazon Bedrock AgentCore agent.

### Step 2: Create the IAM Trust Policy

Create a trust policy that allows the Bedrock AgentCore service to assume the execution role:

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

### Step 3: Associate the Trust Policy

Attach the trust policy to the IAM execution role you created in Step 1. This completes the IAM configuration required for the MCP server to operate within Amazon Bedrock AgentCore.

## Next Steps

### Important Variables

To host this agent in Amazon Bedrock AgentCore, the following variables will need to be known:

| Variable | Description |
| :--- | :--- |
| `FALCON_CLIENT_ID` | The Client ID for your Falcon API credentials |
| `FALCON_CLIENT_SECRET` | The Client Secret for your Falcon API credentials |
| `FALCON_BASE_URL` | The base URL for your Falcon API environment |
| `AGENT_NAME` | The name of the agent (_ex: falconmcp_) |
| `AGENT_DESCRIPTION` | A description of the agent |
| `AGENT_ROLE_ARN` | The ARN of the IAM execution role created in Step 1 |

With your IAM configuration complete and variables prepared, you can now return to the **AWS Marketplace listing** to complete the deployment of your Falcon MCP Server agent in Amazon Bedrock AgentCore.

#### Example Deployment

```bash
aws bedrock-agentcore-control create-agent-runtime \
  --region us-east-1 \
  --agent-runtime-name "falconmcp" \
  --description "Falcon MCP Server Agent" \
  --agent-runtime-artifact '{
    "containerConfiguration": {
      "containerUri": "709825985650.dkr.ecr.us-east-1.amazonaws.com/crowdstrike/falcon-mcp:0.1.1"
    }
  }' \
  --role-arn "arn:aws:iam::example:role/bedrock-core-falcon-role" \
  --network-configuration '{
    "networkMode": "PUBLIC"
  }' \
  --protocol-configuration '{
    "serverProtocol": "MCP"
  }' \
  --environment-variables '{
    "FALCON_CLIENT_ID": "FALCON_CLIENT_ID_VALUE",
    "FALCON_CLIENT_SECRET": "FALCON_CLIENT_SECRET_VALUE",
    "FALCON_BASE_URL": "https://api.crowdstrike.com"
  }'
```
