import requests

from propelauth_py.api import _ApiKeyAuth, _auth_hostname_header, BACKEND_API_BASE_URL
from propelauth_py.errors import BadRequestException, RateLimitedException

ENDPOINT_URL = f"{BACKEND_API_BASE_URL}/api/backend/v1/magic_link"

class CreateMagicLinkResponse:
    def __init__(
        self,
        url: str,
    ):
        self.url = url

    def __repr__(self): 
        return (
            f"CreateMagicLinkResponse(url={self.url}"
        )
    def __eq__(self, other):
        return isinstance(other, CreateMagicLinkResponse)


####################
#       POST       #
####################
def _create_magic_link(
    auth_hostname,
    integration_api_key,
    email,
    redirect_to_url=None,
    expires_in_hours=None,
    create_new_user_if_one_doesnt_exist=None,
    user_signup_query_parameters=None,
) -> CreateMagicLinkResponse:
    url = ENDPOINT_URL
    json = {"email": email}
    if redirect_to_url is not None:
        json["redirect_to_url"] = redirect_to_url
    if expires_in_hours is not None:
        json["expires_in_hours"] = expires_in_hours
    if user_signup_query_parameters is not None:
        json["user_signup_query_parameters"] = user_signup_query_parameters
    if create_new_user_if_one_doesnt_exist is not None:
        json[
            "create_new_user_if_one_doesnt_exist"
        ] = create_new_user_if_one_doesnt_exist

    response = requests.post(
        url,
        json=json,
        auth=_ApiKeyAuth(integration_api_key),
        headers=_auth_hostname_header(auth_hostname),
    )

    if response.status_code == 401:
        raise ValueError("integration_api_key is incorrect")
    elif response.status_code == 429:
        raise RateLimitedException(response.text)
    elif response.status_code == 400:
        raise BadRequestException(response.json())
    elif not response.ok:
        raise RuntimeError("Unknown error when creating magic link")

    json_response = response.json()
    return CreateMagicLinkResponse(
        url=json_response.get('url')
    )
