from fastapi import Query


def pagination(
    limit: int = Query(default=5, ge=1), offset: int = Query(default=0, ge=0)
):
    return {"limit": limit, "offset": offset}
