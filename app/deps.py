from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

#Repositories
from app.repositories.user import UserRepository
from app.repositories.comment import CommentRepository
from app.repositories.post import PostRepository
from app.repositories.media import MediaRepository
from app.repositories.order import OrderRepository

#Servises
from app.services.user import UserService
from app.services.comment import CommentService
from app.services.post import PostService
from app.services.media import MediaService
from app.services.order import OrderService

#Database
from app.database.database import get_db

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

#Order
def order_service_dp(db: AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(repository=OrderRepository(session=db))