# Chatty

Chatty is a small terminal-based client/server chat application written in
Python. It does not require any third-party dependency to launch or test the
project: it uses Python's standard library, including `curses`, `unittest`,
and basic raw TCP sockets.

The goal of the project is to gain a better understanding of low-level socket
handling by implementing the communication flow directly on top of raw
sockets, without relying on a networking framework.

## Running the application

Start the server in one terminal:

```bash
python3 . server # at the root of the project
python3 chatty server # from outside of the project
```

Start one or more clients in other terminals:

```bash
python3 . client # at the root of the project
python3 chatty client # from outside of the project
```

The default server address is `127.0.0.1:1234`.

## Current features and roadmap

- Real-time chat between one server and multiple clients.
- Username-based connection setup.
- Broadcast of messages to all connected clients except the sender.
- Notifications when users join or leave the chat.
- Terminal interface for composing and reading messages.
- Separate client and server entrypoints.
- Communication tests using only Python's standard `unittest` module.

- [ ] Message storage and past history
- [ ] User account with login
- [ ] Message encryption

## Project structure

```text
chatty/
├── communication/
│   ├── requests.py   Request types and request serialization/parsing
│   ├── sockets.py    Socket setup, framed request reads, and byte sending
│   ├── client.py     Client-side network operations
│   └── server.py     Server-side network operations
├── core.py           Network-request to application-event controller
├── tui.py            Terminal interface and user input handling
└── entrypoint/
    ├── client.py     Client startup
    └── server.py     Server startup
```

## Technical choices

### Raw TCP sockets

Communication is implemented directly with Python's `socket` module. The
project explicitly handles connecting, accepting clients, reading from,
writing to, and closing TCP sockets.

### Threaded client handling

The server keeps the accepting loop separate from client listeners by using a
daemon thread for each connected client. The terminal UI also remains
independent from the network listener through the controller event queue.

### Request protocol

Requests use the following frame format:

```text
TYPE|LENGTH\nPAYLOAD
```

`LENGTH` is the payload size in bytes. The currently defined request types are:

- Authentication request
- Message send request
- Message broadcast request

The client sends its username during connection setup. Chat messages are then
sent to the server, which broadcasts them to all other connected clients.

## Testing

Tests use Python's standard `unittest` module and are located under
`tests/communication/`.

Run the test suite with:

```bash
python3 -m unittest discover -s tests -v
```
