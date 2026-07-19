check_conn = set()
check_conn.add(frozenset(("A", "B")))
connection = frozenset(("B", "A"))

if connection in check_conn:
    print("Duplicate connection")
else:
    check_conn.add(connection)