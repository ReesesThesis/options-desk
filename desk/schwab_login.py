"""Weekly Schwab sign-in. Run on YOUR computer, in the options-desk folder:

    py -m desk.schwab_login

1. It asks for your App Key and Secret (the Secret isn't shown as you type). Don't screenshot them.
2. It prints a link. Open it in your browser, sign in to Schwab, approve.
3. The browser lands on https://127.0.0.1/?code=... and says it can't connect: that's normal.
   Copy THAT address from the browser's address bar and paste it here within 30 seconds.
4. It prints a new refresh token. Put it in the cloud environment settings as
   SCHWAB_REFRESH_TOKEN and set SCHWAB_REFRESH_ISSUED to today's date. Don't paste it in chat.
"""
import getpass, os, urllib.parse
from . import schwab
from .http import post_form

REDIRECT = "https://127.0.0.1"

def main():
    if not os.environ.get("SCHWAB_APP_KEY"):
        os.environ["SCHWAB_APP_KEY"] = input("Schwab App Key: ").strip()
    if not os.environ.get("SCHWAB_APP_SECRET"):
        os.environ["SCHWAB_APP_SECRET"] = getpass.getpass("Schwab Secret (hidden): ").strip()
    key = schwab._env("SCHWAB_APP_KEY")
    print("\nOpen this link in your browser and sign in:\n")
    print(f"{schwab.BASE}/v1/oauth/authorize?client_id={key}&redirect_uri={urllib.parse.quote(REDIRECT)}\n")
    while True:
        url = input("After approving, paste the https://127.0.0.1/?code=... address from the browser: ").strip()
        q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        if "code" in q:
            break
        print("\nThat isn't the 127.0.0.1 address. Open the link above in the browser, approve, and copy the")
        print("address the browser ends up on (it starts with https://127.0.0.1/?code=).\n")
    r = post_form(f"{schwab.BASE}/v1/oauth/token",
                  {"grant_type": "authorization_code", "code": q["code"][0], "redirect_uri": REDIRECT},
                  schwab.basic_auth())
    print("\nSCHWAB_REFRESH_TOKEN =", r["refresh_token"])
    print("Put it in the environment settings, with SCHWAB_REFRESH_ISSUED = today's date.")

if __name__ == "__main__":
    main()
