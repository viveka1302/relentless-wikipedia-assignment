Built in FastAPI using Python3.11 , as a practice project to get my hands dirty with Gemini-1.5 using LangChain, and CockroachDB's PostgreSQL distributed server.

Basic Features of this app:
- Signup and Login APIs for running the rest of the authenticated APIs.
- Search an article by name on wikipedia.
- Bookmark certain articles using the save-article API.
- When you save an article, the API automatically generates 5 tags/categories relevant to the article using Gemini.
- API to Edit tags of any particular saved article.
- Fetch all saved articles for the logged in user.
- An HTML page rendered in realtime, linking to a websocket meant for displaying user activity dashboard.

Improvements needed in the future: 
- Try-except Exception handling needs a lot of refining.
- Search articles API should be able to return multiple relevant articles instead of just one.
