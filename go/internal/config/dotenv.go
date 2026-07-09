package config

import "github.com/joho/godotenv"

// LoadDotEnv loads KEY=VALUE pairs from the given .env file into the process
// environment, without overriding variables that are already set. A missing
// file is not an error: CI and container runtimes inject environment variables
// directly. It must run before flag/environment resolution so that .env values
// participate in the defaults < env < flag precedence.
func LoadDotEnv(path string) {
	// godotenv.Load never overrides existing variables, matching the precedence
	// where a real environment variable wins over the .env file. Errors (most
	// commonly a missing file) are intentionally ignored.
	_ = godotenv.Load(path)
}
