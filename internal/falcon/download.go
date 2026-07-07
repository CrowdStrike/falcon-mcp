package falcon

import (
	"bytes"
	"context"
	"io"

	"github.com/crowdstrike/gofalcon/falcon/client/intel"
	"github.com/crowdstrike/gofalcon/falcon/client/report_executions"
	"github.com/go-openapi/runtime"
)

// CaptureBodyOption returns a gofalcon ClientOption that overrides the
// operation's response Reader with one that copies the raw HTTP response body
// into buf on a 2xx. Several gofalcon "download"/"export" operations (e.g.
// ReportExecutionsDownloadGet, GetMitreReport) discard the response body —
// their generated OK struct has no Payload and the op takes no io.Writer — so
// we intercept at the runtime layer, reusing gofalcon's authenticated transport
// rather than issuing a separate raw request. Non-2xx responses fall through to
// the op's normal typed error handling via next.
//
// Exported so binary-download toolsets (report executions, intel MITRE report)
// can share the workaround.
func CaptureBodyOption(buf *bytes.Buffer, next runtime.ClientResponseReader) func(*runtime.ClientOperation) {
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
// ReportExecutionsDownloadGet discards the response body (see CaptureBodyOption).
func (c *FalconClient) DownloadReportExecution(ctx context.Context, id string) ([]byte, error) {
	params := report_executions.NewReportExecutionsDownloadGetParamsWithContext(ctx)
	params.Ids = id

	var buf bytes.Buffer
	reader := &report_executions.ReportExecutionsDownloadGetReader{}
	_, err := c.api.ReportExecutions.ReportExecutionsDownloadGet(params, CaptureBodyOption(&buf, reader))
	if err != nil {
		return nil, err
	}
	return buf.Bytes(), nil
}

// GetMitreReport downloads the MITRE ATT&CK report for an actor, returning the
// raw bytes. gofalcon's GetMitreReport discards the response body (no Payload,
// no io.Writer), so this uses the same CaptureBodyOption workaround.
func (c *FalconClient) GetMitreReport(ctx context.Context, actorID, format string) ([]byte, error) {
	params := intel.NewGetMitreReportParamsWithContext(ctx)
	params.ActorID = actorID
	params.Format = format

	var buf bytes.Buffer
	reader := &intel.GetMitreReportReader{}
	_, err := c.api.Intel.GetMitreReport(params, CaptureBodyOption(&buf, reader))
	if err != nil {
		return nil, err
	}
	return buf.Bytes(), nil
}
