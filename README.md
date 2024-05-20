# topcoat

## TODOs
- [ ] Add tests
- [ ] Use two-dimensional parallelism, not just one-dimensional (currently not working, no idea why not - I think it's the math, Nikita thinks it's the code - see `each-with-each` branch)

## Points of Interest

- src/run_locally.py - demo using two processes on the same machines
- src/run_cli.py - command line interface
- src/topcoat/* - source files for everything

## How to run?

(See <https://gitlab.cyber.ee/petr/topcoat-network-demo> for a demo using two Docker containters.)

Both machines must install the `topcoat` python package.

1. Clone this repository
2. `git submodule update --init --remote --recursive`
3. `pip install hatch`
4. `cd topcoat & hatch build & pip install dist/topcoat-0.0.1-py3-none-any.whl`
5. Ensure that `topcoat` command is available in your shell

### Keygen

Instructions for server party:

1. Define `host` and `port` in `config_server.yaml`
2. Tell client party what `host` and `port` are.
3. Run:

```
topcoat keygen \
   --config ./config_server.yaml \
   --output ./server_keys.pkl
```

Instrucitons for client party:

1. Define `host` and `port` in `config_client.yaml`
2. Run:

```
topcoat keygen \
   --config ./config_client.yaml \
   --output ./client_keys.pkl
```

### Sign

Instructions for server party:

1. Define `host` and `port` in `config_server.yaml`
2. Tell client party what `host` and `port` are.
3. Run:

```
topcoat sign \
   --config ./config_server.yaml \
   --keys ./server_keys.pkl \
   --message "message-to-sign" \
   --output ./signature_from_server.pkl
```

Instrucitons for client party:

1. Define `host` and `port` in `config_client.yaml`
2. Run:

```
topcoat sign \
   --config ./config_client.yaml \
   --keys ./client_keys.pkl \
   --message "message-to-sign" \
   --output ./signature_from_client.pkl
```

### Verification

You can use whatever combination of keys and signatures.

```
topcoat verify \
   --message "message-to-sign" \
   --signature ./signature_from_client.pkl \
   --keys ./server_keys.pkl
```
