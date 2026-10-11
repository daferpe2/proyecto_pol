# utils/keyset.py
from sqlmodel import select

def keyset_query(session, model, last_id=None, limit=50, filters=None):
    stmt = select(model)
    # Filtros dinámicos
    if filters:
        for condition in filters:
            stmt = stmt.where(condition)

    # Orden natural por ID
    stmt = stmt.order_by(model.fecha_registro.desc())

    # Keyset
    if last_id:
        stmt = stmt.where(model.id < last_id)

    items = session.exec(stmt.limit(limit)).all()
    next_cursor = items[-1].id if items else None

    return items, next_cursor


def keyset_query_esp(
    session,
    model,
    last_id=None,
    limit=50,
    filters=None,
    reverse=False
):
    stmt = select(model)

    if filters:
        for condition in filters:
            stmt = stmt.where(condition)

    if last_id is not None:
        if reverse:
            stmt = stmt.where(model.id < last_id)
        else:
            stmt = stmt.where(model.id > last_id)

    if reverse:
        stmt = stmt.order_by(model.id.asc())
    else:
        stmt = stmt.order_by(model.id.desc())

    items = session.exec(stmt.limit(limit)).all()

    if reverse:
        items = list(reversed(items))

    next_cursor = items[-1].id if items else None
    prev_cursor = items[0].id if items else None

    return items, next_cursor, prev_cursor
