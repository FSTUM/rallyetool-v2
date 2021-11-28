# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
from rallyetool.settings.base_settings import *  # noqa: F403

USE_KEYCLOAK = True
MIDDLEWARE.append("mozilla_django_oidc.middleware.SessionRefresh")  # noqa: F405

ins_index = INSTALLED_APPS.index("django.contrib.staticfiles") + 1  # noqa: F405
apps_to_install = ["mozilla_django_oidc", "django_compref_keycloak"]  # noqa: F405
INSTALLED_APPS = INSTALLED_APPS[:ins_index] + apps_to_install + INSTALLED_APPS[ins_index:]  # noqa: F405

AUTHENTICATION_BACKENDS = ("django_compref_keycloak.backend.CompRefKeycloakAuthenticationBackend",)

# realm is either federated-tum.de or fs.tum.de - provided by CompRef
OIDC_OP_AUTHORIZATION_ENDPOINT = (
    "https://auth.fs.tum.de/auth/realms/federated-tum.de/protocol/openid-connect/auth"  # nosec: not secret
)
OIDC_OP_TOKEN_ENDPOINT = (
    "https://auth.fs.tum.de/auth/realms/federated-tum.de/protocol/openid-connect/token"  # nosec: not secret
)
OIDC_OP_USER_ENDPOINT = (
    "https://auth.fs.tum.de/auth/realms/federated-tum.de/protocol/openid-connect/userinfo"  # nosec: not secret
)
OIDC_OP_JWKS_ENDPOINT = (
    "https://auth.fs.tum.de/auth/realms/federated-tum.de/protocol/openid-connect/certs"  # nosec: not secret
)

# We have OpenID Connect clients configured for testing.
# It is okay to put their secrets to internal git repositories, but not to public ones!
# These test clients only accept http://localhost:8080 as redirect URL.
OIDC_RP_CLIENT_ID = "..."  # nosec: provided by CompRef and overwritten for prod
OIDC_RP_CLIENT_SECRET = "..."  # nosec: provided by CompRef and overwritten for prod

OIDC_RP_SIGN_ALGO = "RS256"
OIDC_USERNAME_ALGO = "django_compref_keycloak.backend.generate_username"

# Allowed federated identity providers
COMPREF_KEYCLOAK_FEDERATED_IDP = {
    "fs.tum.de-internal": {
        "enabled": True,
        "active_groups": [],
        "staff_groups": [],
        "superuser_groups": [],
        "sync_groups": True,
    },
    "fs.tum.de": {
        "enabled": True,
        "active_groups": ['users'],
        "staff_groups": ["compref", "rallye-admins"],
        "superuser_groups": ["compref", "rallye-admins"],
        "sync_groups": True,
    },
    "shibboleth.tum.de": {
        "enabled": False,
        "active": {
            "affiliations": [],
            "org_student": [],
            "org_employee": [],
        },
    },
}
