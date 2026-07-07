package falcon

import (
	"bytes"
	"context"
	"io"

	"github.com/crowdstrike/gofalcon/falcon/client/report_executions"
	"github.com/go-openapi/runtime"
)

// captureBodyOption returns a gofalcon ClientOption that overrides the
// operation's response Reader with one that copies the raw HTTP response body
// into buf on a 2xx. Several gofalcon download operations (e.g.
// ReportExecutionsDownloadGet) discard the response body — their generated OK
// struct has no Payload and the op takes no io.Writer — so we intercept at the
// runtime layer, reusing gofalcon's authenticated transport rather than issuing
// a separate raw request. Non-2xx responses fall through to the op's normal
// typed error handling via next.
func captureBodyOption(buf *bytes.Buffer, next runtime.ClientResponseReader) func(*runtime.ClientOperation) {
	return func(op *runtime.ClientOperation) {
		op.Reader = runtime.ClientResponseReaderFunc(func(resp runtime.ClientResponse, consumer runtime.Consumer) (interface{}, error) {
			if resp.Code()/100 == 2 {
				if _, err := io.Copy(buf, resp.Body()); err != nil {
					return nil, err
				}
				return nil, nil
			}
			return next.ReadResponse(resp, consumer)
		})
	}
}

// DownloadReportExecution downloads the content of a report execution by ID,
// returning the raw bytes. It works around the fact that gofalcon's
// ReportExecutionsDownloadGet discards the response body (see captureBodyOption).
func (c *FalconClient) DownloadReportExecution(ctx context.Context, id string) ([]byte, error) {
	params := report_executions.NewReportExecutionsDownloadGetParamsWithContext(ctx)
	params.Ids = id

	var buf bytes.Buffer
	reader := &report_executions.ReportExecutionsDownloadGetReader{}
	_, err := c.api.ReportExecutions.ReportExecutionsDownloadGet(params, captureBodyOption(&buf, reader))
	if err != nil {
		return nil, err
	}
	return buf.Bytes(), nil
}
