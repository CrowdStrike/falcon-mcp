package falcon

import (
	"context"
	"encoding/json"
	"fmt"
	"io"

	"github.com/crowdstrike/gofalcon/falcon/client"
	fidp "github.com/crowdstrike/gofalcon/falcon/client/identity_protection"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
)

// graphqlEndpoint identifies the operation for error messages; it mirrors the
// swagger path+verb of the Identity Protection GraphQL endpoint.
const graphqlEndpoint = "[POST /identity-protection/combined/graphql/v1] api.preempt.proxy.post.graphql"

// GraphQL executes an Identity Protection GraphQL query and returns the decoded
// JSON response body, or a normalized *Error.
//
// It bypasses gofalcon's generated APIPreemptProxyPostGraphql method on purpose:
// that method's APIPreemptProxyPostGraphqlOK response type carries no Payload —
// its generated reader discards the response body entirely — and the method
// panics on any result type other than the typed OK. So this submits the raw
// runtime operation directly through the shared transport with a custom reader
// that captures the body on 2xx and funnels non-2xx through the standard
// APIError path (runtime.APIError carries the status code). scopes are attached
// to a 403 for permission enrichment, matching every other tool.
func GraphQL(ctx context.Context, c *client.CrowdStrikeAPISpecification, query string, scopes ...Scope) (map[string]any, *Error) {
	params := fidp.NewAPIPreemptProxyPostGraphqlParamsWithContext(ctx).
		WithBody(&models.SwaggerGraphQLQuery{Query: &query})

	var body map[string]any
	reader := runtime.ClientResponseReaderFunc(func(resp runtime.ClientResponse, _ runtime.Consumer) (any, error) {
		if resp.Code()/100 != 2 {
			return nil, runtime.NewAPIError(graphqlEndpoint, resp, resp.Code())
		}
		raw, err := io.ReadAll(resp.Body())
		if err != nil {
			return nil, fmt.Errorf("read graphql response: %w", err)
		}
		if len(raw) > 0 {
			if err := json.Unmarshal(raw, &body); err != nil {
				return nil, fmt.Errorf("decode graphql response: %w", err)
			}
		}
		return body, nil
	})

	op := &runtime.ClientOperation{
		ID:                 "api.preempt.proxy.post.graphql",
		Method:             "POST",
		PathPattern:        "/identity-protection/combined/graphql/v1",
		ProducesMediaTypes: []string{"application/json"},
		ConsumesMediaTypes: []string{"application/json"},
		Schemes:            []string{"https"},
		Params:             params,
		Reader:             reader,
		Context:            ctx,
	}

	if _, err := c.Transport.Submit(op); err != nil {
		if e := APIError(err, nil, scopes...); e != nil {
			return nil, e
		}
		return nil, &Error{Message: err.Error()}
	}
	return body, nil
}
