from collections import namedtuple

import pytest
import requests_mock
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key

from propelauth_py import init_base_auth
from propelauth_py.api import _auth_hostname_header, BACKEND_API_BASE_URL
from propelauth_py.validation import _validate_and_extract_auth_hostname

TestRsaKeys = namedtuple("TestRsaKeys", ["public_pem", "private_pem"])

TEST_BASE_AUTH_URL = "https://test.propelauth.com"
WRONG_TEST_BASE_AUTH_URL = "https://wrong.propelauth.com"


@pytest.fixture(scope='function')
def rsa_keys():
    return generate_rsa_keys()


def generate_rsa_keys():
    private_key = generate_private_key(public_exponent=65537, key_size=2048)
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ).decode("utf-8")

    public_key_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")
    return TestRsaKeys(public_pem=public_key_pem, private_pem=private_key_pem)


@pytest.fixture(scope='function')
def auth(rsa_keys):
    return mock_api_and_init_auth(TEST_BASE_AUTH_URL, 200, {
        "verifier_key_pem": rsa_keys.public_pem
    })


def mock_api_and_init_auth(auth_url, status_code, json):
    with requests_mock.Mocker() as m:
        api_key = "api_key"
        m.get(BACKEND_API_BASE_URL + "/api/v1/token_verification_metadata",
              request_headers={'Authorization': 'Bearer ' + api_key},
              json=json,
              status_code=status_code,
              headers=_auth_hostname_header(_validate_and_extract_auth_hostname(auth_url)))
        return init_base_auth(auth_url, api_key)
