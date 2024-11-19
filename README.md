# TOPCOAT implementation

See `examples/run_locally/main.go`. Right now, only Golang channel is implemented for inter-process communication. For a commandline application usage with socket communication, a new implementation of `utils/comms.Comms` is required.