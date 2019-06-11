# WeirdSocket

A simple python socket server supports both raw tcp and ssl, simultaneously.

Real implementation of multiple techniques to resolve the problem.

## Why?

It came up while I was working on other side project (which is pending now 🤐). Although the problem seems super simple (encapsulate TLS around normal socket? or just resume the handshake phase?), but there is no real article related to this situation. Also other open source projects might already have solved in someway, but you will have to spend days to dig into them.

So I would like to amplify it, and share my little work.

But, why are you here? 🙄

## Dependencies

> This is a message from 2020. Please use ...

[![Python 3](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/downloads/)

`pip -r requirements.txt`

## Usage

```
...
```

## Certificate

```
> CA
openssl genrsa -out rootCA.key 4096
openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 1024 -out rootCA.crt

> Key
openssl genrsa -out web.weirdsocket.com.key 4096

> CSR
openssl req -new -out web.weirdsocket.com.csr -key web.weirdsocket.com.key -config san.conf

> Sign
openssl x509 -req -days 3650 -in web.weirdsocket.com.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -out web.weirdsocket.com.crt -extensions v3_req -extfile san.conf


> Debug
openssl req -text -noout -in web.weirdsocket.com.csr
openssl x509 -text -noout -in web.weirdsocket.com.crt


> Ref

https://gist.github.com/fntlnz/cf14feb5a46b2eda428e000157447309
http://apetec.com/support/GenerateSAN-CSR.htm
https://docs.bmc.com/docs/TSCapacity/110/creating-a-request-for-a-ca-signed-certificate-785277999.html
```

## Disclaimer

all techniques used in this project are implemented at experiment level, do not use in production.

## License

GPLv3