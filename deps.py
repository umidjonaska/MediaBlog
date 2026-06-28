from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

#Repositories
from repositories.user import UserRepository
from repositories.comment import CommentRepository
from repositories.post import PostRepository
from repositories.media import MediaRepository

#Servises
from services.user import UserService
from services.comment import CommentService
from services.post import PostService
from services.media import MediaService

#Database
from database.database import get_db

#Users
def user_service_dp(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(repository=UserRepository(session=db))

#Comment
def comment_service_dp(db: AsyncSession = Depends(get_db)) -> CommentService:
    return CommentService(repository=CommentRepository(session=db))

#Post
def post_service_dp(db: AsyncSession = Depends(get_db)) -> PostService:
    return PostService(repository=PostRepository(session=db))

#Media
def media_service_dp(db: AsyncSession = Depends(get_db)) -> MediaService:
    return MediaService(repository=MediaRepository(session=db))