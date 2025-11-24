from app.core.schemas import PaginationMeta, PaginationLinks, PaginationResponse
from app.core.sla_transform_decorator import track_duration


@track_duration(sla_ms=50, label="get_pagination_meta")
async def get_pagination_meta(
    total: int,
    current_page: int = 1,
    per_page: int = 1,
) -> PaginationMeta:
    return PaginationMeta(
        current_page=current_page,
        per_page=per_page,
        total_items=total,
        total_pages=int(total / per_page),
    )


@track_duration(sla_ms=50, label="get_pagination_links")
async def get_pagination_links(
    self_link: str | None = None,
    first_link: str | None = None,
    prev_link: str | None = None,
    next_link: str | None = None,
    last_link: str | None = None,
) -> PaginationLinks:
    return PaginationLinks(
        self=self_link,
        first=first_link,
        prev=prev_link,
        next=next_link,
        last=last_link,
    )


@track_duration(sla_ms=50, label="get_pagination")
async def get_pagination(
    link: PaginationLinks, meta: PaginationMeta
) -> PaginationResponse:
    return PaginationResponse(
        links=link,
        meta=meta,
    )
