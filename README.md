# TOPCOAT implementation

Run `make` to download latticehelper locally before running any go code.

See `examples/run_locally/main.go`. Right now, only Golang channel is implemented for inter-process communication. For a commandline application usage with socket communication, a new implementation of `utils/comms.Comms` is required.