"""Weekly Schwab sign-in. Run on YOUR computer (needs Python 3), not in the cloud:

    SCHWAB_APP_KEY=... SCHWAB_APP_SECRET=... python3 -m desk.schwab_login

1. It prints a link. Open it, sign in to Schwab, approve.
2. The browser lands on https://127.0.0.1/?code=... (a "can't connect" page is normal).
   Copy that whole address and paste it back here within 30 seconds.
3. It prints a new refresh token. Put it in the cloud environment settings as
   SCHWAB_REFRESH_TOKEN and set SCHWAB_REFRESH_ISSUED to today's date. Don't paste it in chat.
"""
import urllib.parse
from . import schwab
from .http import post_form

REDIRECT = "https://127.0.0.1"

def main():
    key = schwab._env("SCHWAB_APP_KEY")
    print("Open this link and sign in:\n")
    print(f"{schwab.BASE}/v1/oauth/authorize?client_id={key}&redirect_uri={urllib.parse.quote(REDIRECT)}\n")
    url = input("Paste the full 127.0.0.1 address here: ").strip()
    code = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["code"][0]
    r = post_form(f"{schwab.BASE}/v1/oauth/token",
                  {"grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT},
                  schwab.basic_auth())
    print("\nSCHWAB_REFRESH_TOKEN =", r["refresh_token"])
    print("Put it in the environment settings, with SCHWAB_REFRESH_ISSUED = today's date.")

if __name__ == "__main__":
    main()
