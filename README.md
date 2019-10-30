## PyRoxy
A simple reverse proxy written in Python3 using the low level stdlib HTTP API.

### Getting started.
Modify `manifest.yaml` to your liking (port, server, proxy rules). Once this is done

you should be able to play around with the reverse proxy. Make sure your `/etc/hosts`

file is correctly configured to resolve the addresses you want in front of the reverse

proxy to your proxy address. Once all this is set up you can run with:

`python3 reverse_proxy.py`

### Basic Example.
To see a basic example, first add the following to your `/etc/hosts` file.

```
127.0.0.1 foo.localhost
127.0.0.1 bar.localhost
```
Then run the dockerfile with: `docker build -t pyroxy . && docker run -p8080:8080 -it pyroxy:latest`

Test out the reverse proxy:

`curl foo.localhost:8080`
`curl bar.localhost:8080`


### Known Limitations.
Currently, there are some issues with caching when viewing in a browser.
