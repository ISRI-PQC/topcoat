.PHONY: all
all: latticehelper
	go build .

.PHONY: latticehelper
latticehelper:
	git clone https://gitlab.cyber.ee/pqc/pq-tools/latticehelper