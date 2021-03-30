#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Checks for guest directories in 'confirmed bookings' and creates
    them if they don't exist.  Also checkes for archived guests
"""

if __name__ == "__main__":

    import locale
    locale.setlocale(locale.LC_ALL, '')
    import mysql.connector
    import pathlib

    home = pathlib.Path.home()

    proj_root = home / "Dropbox" / "scripts" / "mariner_updates"

    guests_dir = proj_root.parents[1] / "Aldeburgh" / "guests"

    old_dir = guests_dir / "old bookings"

    new_dir = guests_dir / "confirmed bookings"

    arch_dirs = list(old_dir.iterdir())

    # Declare database
    cnx = mysql.connector.connect(host="localhost",
                        db="aldeburgh",
                        read_default_file='/home/richard/.my.cnf')
    cursor = cnx.cursor()

    # Read data from bookings table and set names for subsequent use
    cursor.execute("""SELECT
    bookings_guest.first_name, bookings_guest.last_name
    FROM bookings_guest, bookings_booking WHERE
    bookings_guest.id=bookings_booking.guest_id AND
    bookings_booking.rtm_sent < 5
    GROUP BY bookings_guest.id
    """)

    rows = cursor.fetchall()
    for row in rows:
        first_name = row[0]
        last_name = row[1]
        full_name = (first_name + " " + last_name)
        dir_name = str(full_name).lower()
        confirmed_path =  new_dir / dir_name

    # Check if guest directory exists in confirmed bookings

    confirmed_path = new_dir / dir_name

    x = confirmed_path.is_dir()
    if not x:
        for child in old_dir.rglob(dir_name):
            move_dir = child.parent
            i = child.name
            if i:
                move_dir = move_dir / dir_name
                move_dir.replace(confirmed_path)
                s.call(['notify-send', "Moving directory " + dirName + " to "
                            "confirmed bookings"])
            else:
                new_guest = new_dir / dir_name
                new_guest.mkdir()
                s.call(['notify-send', "Creating directory for " + dirName])
