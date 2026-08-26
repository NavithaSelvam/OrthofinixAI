from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import Session

from app.models.schemas import PostCreate, PostUpdate, PostResponse, UserInfo
from app.api.dependencies import get_current_user
from app.db.sqlalchemy_db import get_db_session
from app.db.orm_models import Post, User

router = APIRouter(prefix="/posts")


@router.post("/", response_model=PostResponse)
def create_post(
    post_in: PostCreate,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Create a new clinical post, case discussion, or clinical note in the database.
    """
    post_id = str(uuid.uuid4())
    now_dt = datetime.now(timezone.utc)

    new_post = Post(
        id=post_id,
        user_id=current_user.uid,
        title=post_in.title,
        content=post_in.content,
        category=post_in.category,
        image_url=post_in.image_url,
        report_id=post_in.report_id,
        created_at=now_dt,
        updated_at=now_dt
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return PostResponse(
        id=new_post.id,
        user_id=new_post.user_id,
        author_name=current_user.display_name or "Doctor",
        title=new_post.title,
        content=new_post.content,
        category=new_post.category,
        image_url=new_post.image_url,
        report_id=new_post.report_id,
        created_at=new_post.created_at,
        updated_at=new_post.updated_at
    )


@router.get("/", response_model=List[PostResponse])
def get_posts(
    category: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db_session)
):
    """
    List all clinical posts and discussions from the database.
    """
    query = db.query(Post)
    if category:
        query = query.filter(Post.category == category)

    posts = query.order_by(Post.created_at.desc()).limit(limit).all()

    results = []
    for p in posts:
        author_name = "Doctor"
        if p.author and p.author.display_name:
            author_name = p.author.display_name
        results.append(
            PostResponse(
                id=p.id,
                user_id=p.user_id,
                author_name=author_name,
                title=p.title,
                content=p.content,
                category=p.category,
                image_url=p.image_url,
                report_id=p.report_id,
                created_at=p.created_at,
                updated_at=p.updated_at
            )
        )
    return results


@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: str,
    db: Session = Depends(get_db_session)
):
    """
    Retrieve a specific post by ID.
    """
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")

    author_name = "Doctor"
    if p.author and p.author.display_name:
        author_name = p.author.display_name

    return PostResponse(
        id=p.id,
        user_id=p.user_id,
        author_name=author_name,
        title=p.title,
        content=p.content,
        category=p.category,
        image_url=p.image_url,
        report_id=p.report_id,
        created_at=p.created_at,
        updated_at=p.updated_at
    )


@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: str,
    post_update: PostUpdate,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Update an existing post (author only).
    """
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")

    if p.user_id != current_user.uid and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to edit this post")

    if post_update.title is not None:
        p.title = post_update.title
    if post_update.content is not None:
        p.content = post_update.content
    if post_update.category is not None:
        p.category = post_update.category
    if post_update.image_url is not None:
        p.image_url = post_update.image_url

    p.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(p)

    return PostResponse(
        id=p.id,
        user_id=p.user_id,
        author_name=current_user.display_name or "Doctor",
        title=p.title,
        content=p.content,
        category=p.category,
        image_url=p.image_url,
        report_id=p.report_id,
        created_at=p.created_at,
        updated_at=p.updated_at
    )


@router.delete("/{post_id}")
def delete_post(
    post_id: str,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Delete a post (author only).
    """
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")

    if p.user_id != current_user.uid and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")

    db.delete(p)
    db.commit()
    return {"message": "Post deleted successfully", "id": post_id}
