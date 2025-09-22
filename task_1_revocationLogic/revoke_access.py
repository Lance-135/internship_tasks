from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Dict, Literal

Strategy = Literal["disable_role_assignments", "revoke_role_privileges"]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_audit_table(conn):
    sql = """
    CREATE TABLE IF NOT EXISTS audit_access_revocations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL,
        actor TEXT NOT NULL,
        action TEXT NOT NULL,
        component_id TEXT NOT NULL,
        details_json TEXT NOT NULL
    )
    """
    with conn:
        conn.execute(sql)


def insert_audit(conn, actor: str, action: str, component_id: str, details: Dict) -> None:
    sql = """
    INSERT INTO audit_access_revocations (ts, actor, action, component_id, details_json)
    VALUES (?, ?, ?, ?, ?)
    """
    with conn:
        conn.execute(
            sql,
            (now_iso(), actor, action, component_id, json.dumps(details, separators=(",", ":"))),
        )


def revoke_access_for_component(
    conn,
    component_id: str,
    *,
    strategy: Strategy = "disable_role_assignments",
    actor: str = "admin",
) -> Dict[str, int]:
    ensure_audit_table(conn)
    insert_audit(conn, actor, "start_revoke", component_id, {"strategy": strategy})

    sql_for_roles = """
    SELECT DISTINCT rp.role_id
    FROM role_privileges rp
    WHERE rp.component_id = ?
    """
    role_ids = [row[0] for row in conn.execute(sql_for_roles, (component_id,)).fetchall()]

    disabled_assignments = 0
    revoked_privileges = 0

    if strategy == "disable_role_assignments":
        if role_ids:
            sql_update = f"""
            UPDATE user_roles
            SET enabled = 0
            WHERE role_id IN ({",".join("?" for _ in role_ids)}) AND enabled = 1
            """
            with conn:
                cur = conn.execute(sql_update, role_ids)
            disabled_assignments = cur.rowcount or 0

        insert_audit(
            conn,
            actor,
            "disable_role_assignments",
            component_id,
            {"role_ids": role_ids, "disabled_assignments": disabled_assignments},
        )

    elif strategy == "revoke_role_privileges":
        sql_update = "UPDATE role_privileges SET enabled = 0 WHERE component_id = ? AND enabled = 1"
        with conn:
            cur = conn.execute(sql_update, (component_id,))
        revoked_privileges = cur.rowcount or 0

        insert_audit(
            conn,
            actor,
            "revoke_role_privileges",
            component_id,
            {"revoked_privileges": revoked_privileges},
        )

    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    result = {
        "roles_related_to_component": len(role_ids),
        "disabled_role_assignments": disabled_assignments,
        "revoked_role_privileges": revoked_privileges,
    }

    insert_audit(conn, actor, "complete_revoke", component_id, result)
    return result


# a helper function to create necessary tables
def ensure_minimal_schema(conn) -> None:

    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS user_roles(
            user_id TEXT NOT NULL,
            role_id TEXT NOT NULL,
            enabled INTEGER NOT NULL
        )""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS role_privileges(
            role_id TEXT NOT NULL,
            privilege TEXT NOT NULL,
            component_id TEXT NOT NULL,
            enabled INTEGER NOT NULL
        )""")
    ensure_audit_table(conn)
