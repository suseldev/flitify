import os
import tempfile
import pytest
from crypto.utils import rsakeyutils
from Crypto.PublicKey import RSA

def test_generate_and_load_rsa_keypair():
    with tempfile.TemporaryDirectory() as tmpdir:
        priv_path = f"{tmpdir}/priv.pem"
        pub_path = f"{tmpdir}/pub.pem"

        rsakeyutils.generateRsaKeypair(priv_path, pub_path)
        
        assert os.path.exists(priv_path)
        assert os.path.exists(pub_path)

        priv_key = rsakeyutils.loadKeyFromFile(priv_path)
        pub_key = rsakeyutils.loadKeyFromFile(pub_path)

        assert isinstance(priv_key, RSA.RsaKey)
        assert isinstance(pub_key, RSA.RsaKey)
        assert priv_key.has_private()
        assert not pub_key.has_private()
