import sqlite3


def main() -> None:
    con = sqlite3.connect("plant_app.db")
    cur = con.cursor()
    rows = cur.execute(
        """
        select code, line_id, plc_tag
        from measurement_points
        where code in ('l1_totalizer_general','l2_totalizer_general')
        order by line_id, code
        """
    ).fetchall()
    print(rows)


if __name__ == "__main__":
    main()
