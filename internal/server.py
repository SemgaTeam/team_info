import hmac
import hashlib
from internal.core import Core
from datetime import datetime, timezone

from fastapi import FastAPI, Header, HTTPException, Request, Depends

def get_app(get_core) -> FastAPI:
    app = FastAPI(title="WebHook server")

    @app.post("/postreceive")
    async def postreceive(
        request: Request,
        x_github_event: str | None = Header(default=None),
        x_hub_signature_256: str | None = Header(default=None),
        core: Core = Depends(get_core)
    ) -> dict:
        if not x_github_event:
            raise HTTPException(status_code=400, detail="Missing X-GitHub-Event header")
        if not x_hub_signature_256:
            raise HTTPException(status_code=403, detail="X-Hub-Signature-256 header is missing!")
        
        payload = await request.body()
        verify_signature(payload, core.GITHUB_SECRET_TOKEN, x_hub_signature_256)

        payload = await request.json()
        received_at = utc_now_iso()
        sender_login = (payload.get("sender") or {}).get("login")
        repository_name = (payload.get("repository") or {}).get("full_name")

        await core.handle_webhook_event(x_github_event, sender_login, repository_name, payload, received_at)

        return {"status": "ok"}

    return app
    

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def verify_signature(payload_body, secret_token, signature_header):
    hash_object = hmac.new(secret_token.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=403, detail="Request signatures didn't match!")