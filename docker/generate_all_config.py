import json
import secrets
import string
import getpass
from pathlib import Path

def random_str(length=16):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def token_hex(length=32):
    return secrets.token_hex(length // 2)

INIT_USER = input("Username for Flitify admin: ")
INIT_PASSWORD = getpass.getpass(prompt="Password for Flitify admin: ")

MONGO_USER = random_str(8)
MONGO_PASS = random_str(16)
API_SECRET = token_hex(64)
JWT_SECRET = token_hex(64)

# git repo root directory
BASE = Path(__file__).resolve().parent.parent

SERVER_CFG_TEMPLATE = BASE / "app" / "config_server_example.json"
BACKEND_CFG_TEMPLATE = BASE / "flitify-webpanel" / "backend" / "config_backend_example.json"
SERVER_CFG = BASE / "app" / "config_server.json"
BACKEND_CFG = BASE / "flitify-webpanel" / "backend" / "config_backend.json"
PRIV_KEY_PATH = BASE / "app" / "priv_key.pem"
PUB_KEY_PATH = BASE / "app" / "pub_key.pem"
ENV_PATH = BASE / ".env"


with open(SERVER_CFG_TEMPLATE) as f:
    server_cfg = json.load(f)

server_cfg["flitify_server"]["db_user"] = MONGO_USER
server_cfg["flitify_server"]["db_password"] = MONGO_PASS
server_cfg["flitify_server"]["db_address"] = "flitify-mongo:27017" # docker hostname
server_cfg["flitify_server"]["host"] = "0.0.0.0"
server_cfg["flitify_server"]["private_key_path"] = "/keys/priv_key.pem"
server_cfg["api_server"]["host"] = "0.0.0.0"
server_cfg["api_server"]["secret"] = API_SECRET

with open(SERVER_CFG, "w") as f:
    json.dump(server_cfg, f, indent=4)

with open(BACKEND_CFG_TEMPLATE) as f:
    backend_cfg = json.load(f)

backend_cfg["host"] = "0.0.0.0"
backend_cfg["db_user"] = MONGO_USER
backend_cfg["db_password"] = MONGO_PASS
backend_cfg["db_address"] = "flitify-mongo:27017"
backend_cfg["internal_api_host"] = "http://flitify-server:37012"
backend_cfg["internal_api_secret"] = API_SECRET
backend_cfg["jwt_secret"] = JWT_SECRET

with open(BACKEND_CFG, "w") as f:
    json.dump(backend_cfg, f, indent=4)

with open(ENV_PATH, "w") as f:
    f.write(f"MONGO_INITDB_ROOT_USERNAME={MONGO_USER}\n")
    f.write(f"MONGO_INITDB_ROOT_PASSWORD={MONGO_PASS}\n")
    f.write(f"FLITIFY_INIT_USERNAME={INIT_USER}\n")
    f.write(f"FLITIFY_INIT_PASSWORD={INIT_PASSWORD}\n")
    f.write(f"MONGO_INITDB_DATABASE=flitify\n")
    f.write(f"API_SECRET={API_SECRET}\n")
    f.write(f"JWT_SECRET={JWT_SECRET}\n")

print(f"""[+] Config generated and saved to: 
FlitifyServer: {SERVER_CFG}
FlitifyWebPanel Backend: {BACKEND_CFG}
""")

