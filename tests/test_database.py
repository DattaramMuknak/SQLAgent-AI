from src.database import ReadOnlyDatabase


db = ReadOnlyDatabase()


def test_database_tables():
    """Verify that the Chinook database is accessible."""

    tables = db.list_tables()

    assert "Customer" in tables
    assert "Invoice" in tables
    assert "Track" in tables

    print("✓ Database tables test passed")


def test_customer_schema():
    """Verify that Customer schema can be inspected."""

    schema = db.get_schema("Customer")

    column_names = [column["name"] for column in schema]

    assert "CustomerId" in column_names
    assert "FirstName" in column_names
    assert "LastName" in column_names
    assert "Email" in column_names

    print("✓ Customer schema test passed")


def test_read_only_select():
    """Verify that normal SELECT queries work."""

    result = db.execute_read_only(
        """
        SELECT COUNT(*) AS customer_count
        FROM Customer;
        """
    )

    assert result[0]["customer_count"] == 59

    print("✓ Read-only SELECT test passed")


def test_delete_blocked():
    """Verify that DELETE statements are blocked."""

    try:
        db.execute_read_only(
            "DELETE FROM Customer;"
        )
    except PermissionError:
        print("✓ DELETE blocked")
        return

    raise AssertionError("DELETE query was not blocked")


def test_update_blocked():
    """Verify that UPDATE statements are blocked."""

    try:
        db.execute_read_only(
            "UPDATE Customer SET FirstName = 'HACKED';"
        )
    except PermissionError:
        print("✓ UPDATE blocked")
        return

    raise AssertionError("UPDATE query was not blocked")


def test_drop_blocked():
    """Verify that DROP statements are blocked."""

    try:
        db.execute_read_only(
            "DROP TABLE Customer;"
        )
    except PermissionError:
        print("✓ DROP blocked")
        return

    raise AssertionError("DROP query was not blocked")


def test_pragma_blocked():
    """Verify that user-issued PRAGMA statements are blocked."""

    try:
        db.execute_read_only(
            "PRAGMA table_info(Customer);"
        )
    except PermissionError:
        print("✓ PRAGMA blocked")
        return

    raise AssertionError("PRAGMA query was not blocked")


def test_multiple_statements_blocked():
    """Verify that multiple SQL statements are blocked."""

    try:
        db.execute_read_only(
            "SELECT * FROM Customer; DROP TABLE Customer;"
        )
    except PermissionError:
        print("✓ Multiple statements blocked")
        return

    raise AssertionError(
        "Multiple SQL statements were not blocked"
    )


def test_sql_comments_are_safe():
    """Verify that SQL comments cannot execute hidden commands."""

    result = db.execute_read_only(
        """
        SELECT COUNT(*) AS customer_count
        FROM Customer
        /* UPDATE Customer SET FirstName = 'HACKED' */
        """
    )

    assert result[0]["customer_count"] == 59

    print("✓ SQL comment safety test passed")


def test_read_only_connection():
    """Verify that the SQLite connection is truly read-only."""

    try:
        db.execute_read_only(
            "UPDATE Customer SET FirstName = 'HACKED';"
        )
    except PermissionError:
        pass

    result = db.execute_read_only(
        "SELECT COUNT(*) AS customer_count FROM Customer;"
    )

    assert result[0]["customer_count"] == 59

    print("✓ Database remains unchanged")


if __name__ == "__main__":
    print("=" * 60)
    print("SQLAgent AI — DATABASE SECURITY TEST SUITE")
    print("=" * 60)

    tests = [
        test_database_tables,
        test_customer_schema,
        test_read_only_select,
        test_delete_blocked,
        test_update_blocked,
        test_drop_blocked,
        test_pragma_blocked,
        test_multiple_statements_blocked,
        test_sql_comments_are_safe,
        test_read_only_connection,
    ]

    for test in tests:
        test()

    print("\n" + "=" * 60)
    print("✓ ALL DATABASE SECURITY TESTS PASSED")
    print("=" * 60)