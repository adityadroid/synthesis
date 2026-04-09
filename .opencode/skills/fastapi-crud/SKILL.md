# FastAPI CRUD Skill

## Purpose
Standard CRUD patterns for FastAPI route handlers.

## Usage
Follow these patterns when implementing create, read, update, delete operations.

## Patterns

### Create (POST)
```python
@router.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    service: ItemService = Depends(get_item_service),
) -> ItemResponse:
    """Create a new item."""
    return await service.create(item)
```

### Read One (GET)
```python
@router.get("/items/{item_id}")
async def get_item(
    item_id: UUID,
    service: ItemService = Depends(get_item_service),
) -> ItemResponse:
    """Get item by ID."""
    return await service.get_by_id(item_id)
```

### Read Many (GET)
```python
@router.get("/items")
async def list_items(
    skip: int = 0,
    limit: int = 100,
    service: ItemService = Depends(get_item_service),
) -> list[ItemResponse]:
    """List all items with pagination."""
    return await service.list(skip=skip, limit=limit)
```

### Update (PATCH)
```python
@router.patch("/items/{item_id}")
async def update_item(
    item_id: UUID,
    updates: ItemUpdate,
    service: ItemService = Depends(get_item_service),
) -> ItemResponse:
    """Update item fields."""
    return await service.update(item_id, updates)
```

### Delete (DELETE)
```python
@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: UUID,
    service: ItemService = Depends(get_item_service),
) -> None:
    """Delete item by ID."""
    await service.delete(item_id)
```

## Best Practices
- Use PATCH for partial updates, PUT for full replacement
- Always validate input with Pydantic
- Use dependency injection for services
- Return appropriate status codes
- Document with docstrings
