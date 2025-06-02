# Flitify
**EARLY (UNUSABLE) VERSION, ONLY BASICS ARE IMPLEMENTED FOR NOW!**

Flitify **will be** a secure remote computer management tool with a modern web interface.

It is developed with security in mind, encrypting all communication between clients and the server.

## Setup
1. Clone the repository:
    ```
    git clone https://github.com/xxSusel/flitify.git
    cd flitify
    ```

2. Create and activate a venv:
    ```
    mkdir .venv
    python3 -m venv .venv/
    source .venv/bin/activate
    ```

3. Install required packages:
    ```
    python3 -m pip install -r app/requirements.txt
    ```

4. Generate the keys:
   ```
   python3 app/crypto/utils/rsakeygen.py <path to save rsa keys>
   ```

5. Configure server and client apps:
   ```
   cp app/config_server_example.json app/config_server.json
   vi app/config_server.json
   ```
   
6. Start the Flitify server:
   ```
   python3 app/server_main.py
   ```

## Testing
Run automated tests using pytest:

``` bash
cd app/
python3 -m pytest tests/
```

(C) xxSusel


