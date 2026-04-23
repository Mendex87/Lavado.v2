import sqlite3


def main() -> None:
    con = sqlite3.connect("plant_app.db")
    cur = con.cursor()
    tables = {r[0] for r in cur.execute("select name from sqlite_master where type='table'").fetchall()}
    required = {
        "quality_records",
        "maintenance_requests",
        "oee_snapshots",
        "energy_readings",
        "measurement_readings",
        "quarry_stock",
        "quarry_stock_movements",
    }
    missing = sorted(required - tables)
    print("missing:", missing)
    print("table_count:", len(tables))
    print("stock_rows:", cur.execute("select quarry_id, current_ton from quarry_stock").fetchall())


if __name__ == "__main__":
    main()
