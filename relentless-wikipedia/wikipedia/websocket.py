import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from cockroachDB.factory import SavedArticles

socketroute= APIRouter()

# Serve the dashboard HTML page
@socketroute.get("/activity-dashboard", response_class=HTMLResponse)
async def get_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Real-Time User Activity Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; }
            #activity-list { margin-top: 20px; }
            .activity-item { margin-bottom: 10px; }
        </style>
    </head>
    <body>

    <h1>Real-Time User Activity Dashboard</h1>
    <div id="activity-list"></div>

    <script>
        // Connect to the WebSocket server
        const socket = new WebSocket("wss://relentless-wikipedia-assignment.onrender.com/ws/user-activity");

        socket.onmessage = function(event) {
            const activities = JSON.parse(event.data);
            const activityList = document.getElementById('activity-list');
            
            // Clear the previous activity list
            activityList.innerHTML = '';

            // Display the new activity list
            activities.forEach(activity => {
                const activityItem = document.createElement('div');
                activityItem.classList.add('activity-item');
                activityItem.innerHTML = `<strong>Articles saved today ${activity.title}</strong> - ${activity.url} -saved by: ${activity.savedby} <em>${activity.tags}</em>`;
                activityList.appendChild(activityItem);
            });
        };

        socket.onclose = function(event) {
            console.log("WebSocket closed");
        };

        socket.onerror = function(error) {
            console.error("WebSocket error", error);
        };
    </script>

    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

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

