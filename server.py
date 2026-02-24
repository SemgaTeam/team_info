from core import Core
from datetime import datetime, timezone

from fastapi import FastAPI, Header, HTTPException, Request, Depends

def get_app(get_core) -> FastAPI:
    app = FastAPI(title="WebHook server")

    @app.post("/postreceive")
    async def postreceive(
        request: Request,
        x_github_event: str | None = Header(default=None),
        core: Core = Depends(get_core)
    ) -> dict:
        if not x_github_event:
            raise HTTPException(status_code=400, detail="Missing X-GitHub-Event header")

        payload = await request.json()
        received_at = utc_now_iso()
        sender_login = (payload.get("sender") or {}).get("login")
        repository_name = (payload.get("repository") or {}).get("full_name")

        await core.handle_webhook_event(x_github_event, sender_login, repository_name, payload, received_at)

        return {"status": "ok"}

    return app
    

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
