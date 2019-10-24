trap 'kill %1; kill %2; kill %3' SIGINT
python3 -m http.server -d examples/server1 3000 & python3 -m http.server -d examples/server2 5000 & python3 reverse_proxy.py & wait
