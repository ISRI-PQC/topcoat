.PHONY: all
all: devkit
	go build .

.PHONY: devkit
devkit:
	git clone git@gitlab.cyber.ee:pqc/PQ-protocols/pqdevkit.git