# TOPCOAT implementation

This is a Golang implementation of TOPCOAT https://link.springer.com/article/10.1007/s10791-024-09449-2, a two-party lattice-based signature scheme which embodies Crystals-Dilithium (ML-DSA) compression techniques. 


**WARNING**: This implementation is an proof-of-concept prototype, has not received thorough code review, and is not ready for production use.

## Code Overview

See `examples/run_locally/main.go`. Right now, only Golang channel is implemented for inter-process communication. For a commandline application usage with socket communication, a new implementation of `utils/comms.Comms` is required.

## Acknowledgements

This work was funded by the Estonian Research Council under the grant number PRG1780 (Distributed Identity, Distributed Trust). 

## Licence 
TOPCOAT is licensed under the MIT License. See [LICENSE](LICENSE)