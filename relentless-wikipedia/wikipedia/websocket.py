import asyncio
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from fastapi.responses import HTMLResponse
from cockroachDB.factory import SavedArticles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pathlib import Path

socketroute= APIRouter()

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Serve the dashboard HTML page
@socketroute.get("/activity-dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return templates.TemplateResponse("activity_dashboard.html", {"request": request})
# WebSocket for real-time user activity updates
async def fetch_user_activity(websocket: WebSocket):
    try:
        while True:
            # Query the latest user activities from the database
            savedarticledata= SavedArticles()
            activities = savedarticledata.user_activity()
            ac_list= activities.fetchall()
            col=activities.keys()
            col=list(col)
            activityDict=[]
            for i in ac_list:
                activityDict.append(dict(zip(col, i)))
            # Send data to WebSocket client
            data = [{"title": activity["title"], "url": activity["url"], "tags": activity["tags"], "savedBy": activity["savedby"] } for activity in activityDict]
            await websocket.send_json(data)
            
            # Wait for a short period before refreshing data (polling every 5 seconds)
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        print("Client disconnected")

@socketroute.websocket("/ws/user-activity")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Start sending user activity updates
    await fetch_user_activity(websocket)

