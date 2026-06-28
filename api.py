"""Asosiy application"""

from fastapi import FastAPI, APIRouter
from fastapi.responses import ORJSONResponse

from core.config import config

from routes import user, post, comment, media

from auth import login

api = APIRouter()

#Users
api.include_router(user.router, tags=["Users"])
api.include_router(comment.router, tags=["Comments"])
api.include_router(post.router, tags=["Posts"])
api.include_router(media.router, tags=["Media"])
api.include_router(login.auth_route, tags=["Auth"])

# Admin
app = FastAPI(
    title=config.app.app_name,
    description=f"{config.app.app_name} uchun Blog_Post api",
    version='1.0',
    contact={
        'name': 'Umidjon Blog',
        'url': 'https://umidjon_blog.com',
    },
    docs_url='/docs',  # None - dokumentatsiyani o`chirish
    redoc_url='/redoc',  # None - dokumentatsiyani o`chirish
    debug=config.debug,
    default_response_class=ORJSONResponse
)

@app.get('/')
async def main():
    return {
        'status': 200,
        'message': 'Umidjon Askaraliev'
    }


app.include_router(api)