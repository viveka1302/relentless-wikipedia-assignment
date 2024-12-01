from wikipedia_settings.app import app as fastApp
from wikipedia import views as wiki_view

# CODE BELOW


# Register API Router
fastApp.include_router(wiki_view.router,
                    tags=["wiki"],
                    responses={404: {"error": "wiki router missing"}},
)