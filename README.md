# WeirdSocket

A simple python socket server supports both raw tcp and ssl, simultaneously.

Real implementation of multiple techniques to resolve the problem.

## Why ?

It came up while I was working on other side project (which is pending now 🤐). Although the problem seems super simple (encapsulate TLS around normal socket? or just resume the handshake phase?), but there is no real article related to this situation. Also other open source projects might already have solved in someway, but you will have to spend days to dig into them.

So I would like to amplify it, and share my little work.

Btw, why are you here? 🙄

## Technical details

> ... a long time ago in a galaxy far, far away 🖖 ... there is an [article](https://blog.trich.im/project/2019/weirdsocket/)

## Dependencies

> This is a message from 2020. Please use ...

[![Python 3](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/downloads/)

`pip -r requirements.txt`

## Usage

### Server

Pick your experiment server 👉 `python <file> --help`

- `MSGPEEK` technique include these experiments
```
server_msgpeek_once.py
server_msgpeek_forever.py
server_msgpeek_twisted.py
```

- Hijack TLS handshake technique
```
server_tlslite_once.py
```

- A demo web service based on 1st technique and twisted framework. Please generate a valid certificate for your wanted hostname (tutorial below), trust its chain - [how?](https://support.portswigger.net/customer/portal/articles/1783075-installing-burp-s-ca-certificate-in-your-browser) - and **DO NOT** forget to change `hosts` file 😁. I already provided a sample hostname `web.weirdsocket.com` as default and a root certificate to trust.
```
server_web_twisted.py
```

### Client

- raw 👉 `nc localhost 9999`

- ssl 👉 `python client.py --help`

## Certificate

```
> Create a self-signed root CA
openssl genrsa -out rootCA.key 4096
openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 1024 -out rootCA.crt

> Generate Key for domain
openssl genrsa -out web.weirdsocket.com.key 4096

> Generate CSR (check out 'san.conf' in cert directory) with SAN extension (Chrome requirement 🤐)
openssl req -new -out web.weirdsocket.com.csr -key web.weirdsocket.com.key -config san.conf

> Sign with our rootCA (check out 'san.conf' in cert directory)
openssl x509 -req -days 3650 -in web.weirdsocket.com.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -out web.weirdsocket.com.crt -extensions v3_req -extfile san.conf

> Debug
openssl req -text -noout -in web.weirdsocket.com.csr
openssl x509 -text -noout -in web.weirdsocket.com.crt

> Note
- Because the chain has only 2 nodes, so no need to create fullchain
- SAN is required by Chrome to trust the certificate, so if you don't want to mess with it just create/sign a certficate with CommonName (CN) == your donmain name. Ref below.
```

Ref
- https://gist.github.com/fntlnz/cf14feb5a46b2eda428e000157447309
- http://apetec.com/support/GenerateSAN-CSR.htm
- https://docs.bmc.com/docs/TSCapacity/110/creating-a-request-for-a-ca-signed-certificate-785277999.html
 

## Disclaimer

all techniques used in this project are implemented at experiment level, do not use in production.

## License

GPLv3