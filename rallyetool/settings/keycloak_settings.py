from rallyetool.settings.base_settings import *

MIDDLEWARE.append("mozilla_django_oidc.middleware.SessionRefresh")

ins_index = INSTALLED_APPS.index("django.contrib.staticfiles") + 1
apps_to_install = ["mozilla_django_oidc", "django_compref_keycloak"]
INSTALLED_APPS = INSTALLED_APPS[: ins_index] + apps_to_install + INSTALLED_APPS[ins_index:]

AUTHENTICATION_BACKENDS = ("django_compref_keycloak.backend.CompRefKeycloakAuthenticationBackend",)

# realm is either federated-tum.de or fs.tum.de - provided by CompRef
OIDC_OP_AUTHORIZATION_ENDPOINT = "https://auth.fs.tum.de/auth/realms/federated-tum.de/protocol/openid-connect/auth"
OIDC_OP_TOKEN_ENDPOINT = "https://auth.fs.tum.de/auth/realms/federated-tum.de/protocol/openid-connect/token"
OIDC_OP_USER_ENDPOINT = "https://auth.fs.tum.de/auth/realms/federated-tum.de/protocol/openid-connect/userinfo"
OIDC_OP_JWKS_ENDPOINT = "https://auth.fs.tum.de/auth/realms/federated-tum.de/protocol/openid-connect/certs"

# We have OpenID Connect clients configured for testing.
# It is okay to put their secrets to internal git repositories, but not to public ones!
# These test clients only accept http://localhost:8080 as redirect URL.
OIDC_RP_CLIENT_ID = "..."  # provided by CompRef and overwritten for prod deployment
OIDC_RP_CLIENT_SECRET = "..."  # provided by CompRef and overwritten for prod deployment

OIDC_RP_SIGN_ALGO = "RS256"
OIDC_USERNAME_ALGO = "django_compref_keycloak.backend.generate_username"
# Allowed federated identity providers
# fs.tum.de accounts
COMPREF_KEYCLOAK_FEDERATED_IDP = {
    "fs.tum.de-internal": {
        "enabled": True,
        "active_groups": ["compref", "rallye", "set"],
        # grant superuser privileges for these LDAP groups (empty = is_staff is not touched, also not removed!)
        "staff_groups": ["compref", "rallye", "set"],
        # grant superuser privileges for these LDAP groups (empty = is_superuser is not touched, also not removed!)
        "superuser_groups": ["compref"],
        "sync_groups": True,
    },
    "fs.tum.de": {
        "enabled": True,
        "active_groups": [],
        "staff_groups": [],
        "superuser_groups": [],
        "sync_groups": True,
    },
    "shibboleth.tum.de": {
        "enabled": True,
        "active": {
            "affiliations": [],
            "org_student": [],
            "org_employee": [],
        },
    },
}
