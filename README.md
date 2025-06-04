# 📦 Flitify
*Secure, modular remote computer management tool*

**Flitify** is a secure and modular remote client management system, built around a custom encrypted TCP protocol. It features a modern React-based admin panel, Flask backend, and fully Dockerized deployment for ease of setup and use.

## ✨ Features
- **Custom encrypted protocol**
   - Built from scratch over TCP, using AES encryption, secure key exchange, and per-client authentication.
- **Modern API architecture**
    - Internal Flask API served via Waitress, secured by a secret token and isolated from public access. All requests are routed through a web backend proxy with user login and JWT-based session handling.
    -  Internal control layer is not exposed externally; only the proxy can interact with it.
- **Admin Web Panel (React)**
    - Complete authentication-gated UI offering:
        -   Client status overview      
        -   File browser interface
        -   Pseudo-interactive command shell
 
## ⚡ Quickstart 
### Docker (recommended)
Flitify is packaged as a Docker container using **nginx** as the reverse proxy and static frontend host. The **frontend is automatically built** during the Docker image build process.
```bash
git clone https://github.com/xxSusel/flitify.git
cd flitify
python3 docker/generate_all_config.py # Generate config, set admin username and password
docker-compose up --build
```

#### (Optional) Run a client:
1) Sign in to the web panel
2) Navigate to the "Computers" tab and add a new client
3) Start the client app:
```
cp config_client_example.json config_client.json
vi config_client.json
python3 client_main.py
```
>  **Note:** A standalone Windows executable client is planned for future releases.
>  
### Manual deployment
> **Important:** Ensure you have a working **MongoDB** instance before proceeding.
1) Clone the repository
```bash
git clone https://github.com/xxSusel/flitify.git
cd flitify
```

2) Set up the Python virtual environment and install requirements:
```bash
cd app
mkdir .venv
python3 -m venv .venv/
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```
3) Generate RSA keys and configure the server
```bash
python3 crypto/utils/rsakeyutils.py .
cp config_server_example.json config_server.json
vi config_server.json
```
 > **Security Warning:**  
> Do **NOT** expose the internal API server to the public networks. It is designed to operate in a secure, isolated environment, acting as a bridge between the Flitify server and the web backend.

4) Start the Flitify server:
```bash
python3 server_main.py
```
5) Set up the web backend:
```bash
cd ../ # Go to the repository root directory
cd flitify-web/backend
mkdir .backend-venv
python3 -m venv .backend-venv/
source .backend-venv/bin/activate
python3 -m pip install -r requirements.txt
```
6) Configure the backend:
```bash
cp config_backend_example.json config_backend.json
vi config_backend.json
```
7) Launch the backend (creates admin user on the first run)
```bash
FLITIFY_INIT_USERNAME=yourname FLITIFY_INIT_PASSWORD=yourpass python3 app.py
```
8) Start the frontend:
```bash
cd ../frontend # Go to flitify-web/frontend
npm install
vi vite.config.js # Configure API proxy to match backend
npm run dev # Start the development server
```
9) *(Optional)* Add a client in the web panel and start it:
```bash
cp config_client_example.json config_client.json
vi config_client.json
python3 client_main.py
```
## 📌 Roadmap / TODO
- [ ] Role-based access controls
- [ ] Administrator user management panel
- [ ] Client grouping feature (e.g., assign multiple computers into groups with shared access permissions)
- [ ] Documentation

## ⚠️ Disclaimer
Flitify was originally developed as an internal tool. While it includes client authentication mechanisms, these can be easily disabled.
 > Do not use this tool for malicious purposes.


