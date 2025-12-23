"""
Admin API endpoints for managing application configuration.
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.config import AppConfig, DEFAULT_CONFIG
from app.models.user import User
from app.api.auth import get_current_admin_user


router = APIRouter()


# Pydantic Schemas
class ConfigItemResponse(BaseModel):
    id: str
    key: str
    value: Optional[str]
    description: Optional[str]
    value_type: str
    category: str
    is_secret: bool
    is_editable: bool
    updated_at: datetime

    class Config:
        from_attributes = True


class ConfigItemUpdate(BaseModel):
    value: Optional[str]


class ConfigBulkUpdate(BaseModel):
    configs: dict[str, str]  # key -> value mapping


class ConfigCategoryResponse(BaseModel):
    category: str
    items: List[ConfigItemResponse]


# Routes
@router.get("", response_model=List[ConfigItemResponse])
async def list_all_config(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all configuration items, optionally filtered by category."""
    query = select(AppConfig)
    if category:
        query = query.where(AppConfig.category == category)
    query = query.order_by(AppConfig.category, AppConfig.key)

    result = await db.execute(query)
    configs = result.scalars().all()

    return [
        ConfigItemResponse(
            id=str(config.id),
            key=config.key,
            value="********" if config.is_secret and config.value else config.value,
            description=config.description,
            value_type=config.value_type,
            category=config.category,
            is_secret=config.is_secret,
            is_editable=config.is_editable,
            updated_at=config.updated_at
        )
        for config in configs
    ]


@router.get("/categories", response_model=List[str])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get list of all configuration categories."""
    result = await db.execute(
        select(AppConfig.category).distinct().order_by(AppConfig.category)
    )
    return [row[0] for row in result.all()]


@router.get("/by-category", response_model=List[ConfigCategoryResponse])
async def get_config_by_category(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all configuration items grouped by category."""
    result = await db.execute(
        select(AppConfig).order_by(AppConfig.category, AppConfig.key)
    )
    configs = result.scalars().all()

    # Group by category
    categories_dict = {}
    for config in configs:
        if config.category not in categories_dict:
            categories_dict[config.category] = []
        categories_dict[config.category].append(
            ConfigItemResponse(
                id=str(config.id),
                key=config.key,
                value="********" if config.is_secret and config.value else config.value,
                description=config.description,
                value_type=config.value_type,
                category=config.category,
                is_secret=config.is_secret,
                is_editable=config.is_editable,
                updated_at=config.updated_at
            )
        )

    return [
        ConfigCategoryResponse(category=cat, items=items)
        for cat, items in categories_dict.items()
    ]


@router.get("/{key}", response_model=ConfigItemResponse)
async def get_config_item(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get a specific configuration item by key."""
    result = await db.execute(select(AppConfig).where(AppConfig.key == key))
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration key '{key}' not found"
        )

    return ConfigItemResponse(
        id=str(config.id),
        key=config.key,
        value="********" if config.is_secret and config.value else config.value,
        description=config.description,
        value_type=config.value_type,
        category=config.category,
        is_secret=config.is_secret,
        is_editable=config.is_editable,
        updated_at=config.updated_at
    )


@router.put("/{key}", response_model=ConfigItemResponse)
async def update_config_item(
    key: str,
    update: ConfigItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update a specific configuration item."""
    result = await db.execute(select(AppConfig).where(AppConfig.key == key))
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration key '{key}' not found"
        )

    if not config.is_editable:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Configuration key '{key}' is not editable"
        )

    config.value = update.value
    config.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(config)

    return ConfigItemResponse(
        id=str(config.id),
        key=config.key,
        value="********" if config.is_secret and config.value else config.value,
        description=config.description,
        value_type=config.value_type,
        category=config.category,
        is_secret=config.is_secret,
        is_editable=config.is_editable,
        updated_at=config.updated_at
    )


@router.put("", response_model=List[ConfigItemResponse])
async def bulk_update_config(
    update: ConfigBulkUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Bulk update multiple configuration items."""
    updated_configs = []

    for key, value in update.configs.items():
        result = await db.execute(select(AppConfig).where(AppConfig.key == key))
        config = result.scalar_one_or_none()

        if not config:
            continue  # Skip non-existent keys

        if not config.is_editable:
            continue  # Skip non-editable keys

        config.value = value
        config.updated_at = datetime.utcnow()
        updated_configs.append(config)

    await db.commit()

    return [
        ConfigItemResponse(
            id=str(config.id),
            key=config.key,
            value="********" if config.is_secret and config.value else config.value,
            description=config.description,
            value_type=config.value_type,
            category=config.category,
            is_secret=config.is_secret,
            is_editable=config.is_editable,
            updated_at=config.updated_at
        )
        for config in updated_configs
    ]


@router.post("/clear-cache", response_model=dict)
async def clear_cache_and_seed(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Clear Redis cache and seed default configuration values."""
    import redis
    from app.config import settings

    # Clear Redis cache
    cache_cleared = False
    try:
        r = redis.from_url(settings.redis_url)
        r.flushdb()
        cache_cleared = True
    except Exception as e:
        # Log but don't fail if Redis is unavailable
        pass

    # Seed missing config values
    added = 0
    skipped = 0

    for config_data in DEFAULT_CONFIG:
        result = await db.execute(
            select(AppConfig).where(AppConfig.key == config_data["key"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            skipped += 1
            continue

        config = AppConfig(**config_data)
        db.add(config)
        added += 1

    await db.commit()

    return {
        "cache_cleared": cache_cleared,
        "added": added,
        "skipped": skipped,
        "message": f"Cache cleared. Seeded {added} new config items."
    }
