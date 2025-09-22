import sqlite3
from revoke_access import ensure_minimal_schema, revoke_access_for_component

conn = sqlite3.connect("access.db")
ensure_minimal_schema(conn)

# Seed example data
with conn:
	conn.executemany("INSERT INTO user_roles(user_id, role_id, enabled) VALUES(?, ?, 1)", [
		("u:alice", "r:billing-admin"), ("u:bob", "r:billing-viewer"), ("u:carol", "r:billing-admin")
	])
	conn.executemany("INSERT INTO role_privileges(role_id, privilege, component_id, enabled) VALUES(?, ?, ?, 1)", [
		("r:billing-admin", "billing:write", "billing-svc"),
		("r:billing-viewer", "billing:read", "billing-svc"),
	])


# Execute (disable role assignments)
print(revoke_access_for_component(conn, "billing-svc", strategy="disable_role_assignments"))

# Or revoke privileges from roles instead
print(revoke_access_for_component(conn, "billing-svc", strategy="revoke_role_privileges"))