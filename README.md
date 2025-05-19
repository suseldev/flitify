# Flitify
**EARLY VERSION, ONLY BASICS ARE IMPLEMENTED FOR NOW!**
Flitify **will be** a secure remote computer management tool with a modern web interface.
It is developed with security in mind, encrypting all communication between clients and the server.

## Setup
1. Clone the repository:
    ```bash
    git clone https://github.com/xxSusel/flitify.git
    cd flitify
    ```
2. Create and activate a venv:
    ```bash
    mkdir .venv
    python3 -m venv .venv/
    source .venv/bin/activate
    ```
3. Install required packages:
    ```bash
    python3 -m pip install -r server/requirements.txt
    ```

## Testing
Run automated tests using pytest:
    ```bash
    cd server/
    python3 -m pytest tests/
    ```

(C) xxSusel


