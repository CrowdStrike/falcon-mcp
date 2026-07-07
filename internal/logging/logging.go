// Package logging configures the process-wide slog logger. All output goes to
// stderr so that stdout stays reserved for the stdio MCP transport.
package logging

import (
	"log/slog"
	"os"

	"github.com/sirupsen/logrus"
)

// Configure installs a slog logger writing to stderr at the requested level
// and pins gofalcon's logrus logger to Warn (or Debug when debug is set) so it
// does not pollute stdout.
func Configure(debug bool) *slog.Logger {
	level := slog.LevelInfo
	logrusLevel := logrus.WarnLevel
	if debug {
		level = slog.LevelDebug
		logrusLevel = logrus.DebugLevel
	}

	handler := slog.NewTextHandler(os.Stderr, &slog.HandlerOptions{Level: level})
	logger := slog.New(handler)
	slog.SetDefault(logger)

	logrus.SetOutput(os.Stderr)
	logrus.SetLevel(logrusLevel)

	return logger
}
