#!/usr/bin/env python3
# -*- coding: utf-8 -*-

if __name__ == "__main__":

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import inch, landscape, A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table, TableStyle, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.pdfgen import canvas
    import mysql.connector
    import string
    import datetime
    import locale
    locale.setlocale(locale.LC_ALL, '')
    import os
    import csv
    import re
    import emailUpdates

    os.chdir(os.pardir)

    PROJECT_DIR = os.getcwd()
  
    WORKING_DIR =  PROJECT_DIR + '/mariners_site/'

    TEXT_DIR = WORKING_DIR + 'textFiles/'
    
    print (PROJECT_DIR)
    
    print (TEXT_DIR)

    os.chdir(TEXT_DIR)
    
    with open('latestUpdate.txt', 'r') as lu:
            lu = lu.read()
        
    with open('latestPrint.txt', 'r') as lp:
            lp = lp.read()
            
    with open('lastBooking.txt', 'r') as lb:
        lb = lb.read()
        
    with open('lizLatest.txt', 'r') as llz:
        llz = llz.read()   
        
    with open('totalConfirmed.txt', 'r') as tc:
        tc = tc.read()           

    lp = int(lp)
    lu = int(lu)
    lb = int(lb)
    #llz = int(llz)
    tc = int(tc)
    
    # Declare database
    cnx = mysql.connector.connect(host="localhost",
                        db="aldeburgh",
                        read_default_file='/home/richard/.my.cnf')
                        
    cursor = cnx.cursor()

    print ("Latest booking " + str(lb))
    print ("Total bookings " + str(tc))
    print ("Liz total bookings " + str(llz))
        
    # Determine date format and define date periods
    format = "%d %b %Y"
    format_liz = "%A %d %b %Y"
    format_price = "%d %B %Y"

    bth=['Name','Start','End', 'Adults', 'Children', 'Status', 'Date', 'Notes']
    liz_bth = ['Name','Start','End', 'Adults', 'Children', 'Notes']

    bkg_list = []
    liz_list = []
    bkg_status = []
    most_recent_bkg = []
    styleSheet = getSampleStyleSheet()
    bkg_list.append(bth)
    liz_list.append(liz_bth)
    today = datetime.date.today()
    td = today.strftime(format)
    ty = today.toordinal()
    temp_price = []
    price_list = []
    price_heads = ["Start date", "End date", "Weekly cost", "Two nights", "Three+ nights"]
    price_list.append(price_heads)    
    two_night = 90
    three_plus = 80
    two_night = locale.currency((two_night), grouping = True)
    three_plus = locale.currency((three_plus), grouping = True)

    # Read data from bookings table and set names for subsequent use
    cursor.execute("""SELECT bookings_guest.first_name, bookings_guest.last_name,
    bookings_booking.start_date, bookings_booking.end_date, bookings_booking.bkd_adult, bookings_booking.bkd_child, bookings_booking.num_nights,
    bookings_booking.notes, bookings_booking.rtm_sent, bookings_booking.dep_recd, bookings_booking.bal_recd, bookings_booking.keys_sent, bookings_booking.ack_date, bookings_booking.guest_status
     FROM bookings_guest, bookings_booking WHERE bookings_guest.id = bookings_booking.guest_id AND bookings_booking.rtm_sent <5
    ORDER BY start_date""")
    row = cursor.fetchall()
    for row in row:
        start_date = row[2]
        end_date = row[3]
        first_name = row[0]
        last_name = row[1]
        full_name = first_name + ' ' + last_name
        adults = row[4]
        children = row[5]
        num_nights = row[6]
        notes = row[7]
        notes = notes.replace("<p>", "\n")
        notes = notes.replace("</p>", "")
        rtm_sent = row[8]
        dep_paid = row[9]
        bal_paid = row[10]
        keys_sent = row[11]
        ack_date = row[-2]
        guest_status = row[-1]
        sd = start_date.strftime(format)
        sd = sd.strip('0')
        ed = end_date.strftime(format)
        ed = ed.strip('0')
        lsd = start_date.strftime(format_liz)
        led = end_date.strftime(format_liz)
        fbd = start_date.toordinal()
        lbd = end_date.toordinal()
        bkg_period = range(fbd, lbd)

        if end_date >= today:
            most_recent_bkg.append(end_date)
            mrb = min(most_recent_bkg)
            mrb = datetime.date.toordinal(mrb)
            mrb = mrb - 7
        
        if keys_sent:
                df = keys_sent.strftime(format)
                df = df.strip('0')
        elif dep_paid:
                df = dep_paid.strftime(format)
                df = df.strip('0')
        elif bal_paid:
                df = bal_paid.strftime(format)
                df = df.strip('0')
        else:
                df = '-'
                
        if rtm_sent == 0:
                bkg_status = 'Enquiry'
        elif start_date in bkg_period:
                bkg_status = 'In residence'
        elif keys_sent:
                bkg_status = 'Keys sent'
        elif bal_paid:
                bkg_status = 'Balance received'
        elif dep_paid:
                bkg_status = 'Deposit received'
        elif ack_date:
                bkg_status = 'Acknowledged'
        else:
                pass

        bkd_guest = []
        liz_guest = []
        
        if end_date >= datetime.date.today():

            bkd_guest.append(full_name)
            bkd_guest.append(sd)
            bkd_guest.append(ed)
            bkd_guest.append(adults)
            bkd_guest.append(children)
            bkd_guest.append(bkg_status)

            if (dep_paid or guest_status > 0):
                liz_guest.append(full_name)
                liz_guest.append(lsd)
                liz_guest.append(led)
                liz_guest.append(adults)
                liz_guest.append(children) 

            if df: # If keys have been sent (df)
                    bkd_guest.append(df)
            else:
                    bkd_guest.append('-')

            T = Paragraph(notes, styleSheet["BodyText"])
            bkd_guest.append(T)

            bkg_list.append(bkd_guest)

            if liz_guest:
                    liz_list.append(liz_guest)
                        

    if lp != lu:
        print ("Latest print:  " + str(lp) + ",liz latest update: " + str(lu))
        lp = str(lu)
        with open('latestPrint.txt', 'w') as lp2:
            lp2.write(lp)
                     
    else:
        print ("No update required")
        
    emailUpdates.send_dmc()

    styleSheet = getSampleStyleSheet()
    style = styleSheet['Title']
    P = Paragraph("Mariner's Loft latest bookings as at " + td, style)
    c = canvas.Canvas(PROJECT_DIR + "/Aldeburgh","latest bookings.pdf")
            
    doc = SimpleDocTemplate((PROJECT_DIR + "/Aldeburgh" + "/latest bookings.pdf"), pagesize=landscape(A4))
    liz_doc = SimpleDocTemplate((PROJECT_DIR + "/Aldeburgh" + "/latest bookings liz.pdf"), pagesize=(A4))
    elements = []
    liz_elements = []
    
    bt=Table(bkg_list,style=[('GRID',(0,0),(-1,-1),1,colors.green),
                                            ('BOX',(0,0),(-1,-1),2,colors.blue),
                                            ('BACKGROUND', (0, 0), (-1, 0), colors.lavender),
                                            ('ALIGN', (1,1), (-4,-1), 'RIGHT'),
                                            ('ALIGN', (6,1), (-2,-1), 'RIGHT'),
                                            ('VALIGN', (0,0), (-1,-1), 'TOP'),
                                                     ], colWidths=(150,100,100,50,50,100,100,100), repeatRows=1)

    lz = Table(liz_list,style=[('GRID',(0,0),(-1,-1),1,colors.green),
                                            ('BOX',(0,0),(-1,-1),2,colors.blue),
                                            ('BACKGROUND', (0, 0), (-1, 0), colors.lavender),
                                            ('ALIGN', (3,1), (-1,-1), 'RIGHT'),
                                            ('VALIGN', (0,0), (-1,-1), 'TOP'),
                                                     ], colWidths=(125,125,125,50,50,75))
    elements.append(P)
    elements.append(Spacer(1,24))
    elements.append(bt)
    #write the document to disk
    doc.build(elements)
    
    if today.weekday() == 4:
        liz_elements.append(P)
        liz_elements.append(Spacer(1,24))
        liz_elements.append(lz)
        liz_doc.build(liz_elements)
        
        with open("lizLatest.txt", "w") as lzl:
            lzl.write(str(tc))
            
        emailUpdates.liz_send()
            
        print ("Send latest list to Liz")
        
        with open('liz_text.txt', 'w') as ltx:
            ltx.close()

        with open('liz_message.txt', 'w') as lms:
            lms.close()
        
    with open('prices.csv', 'r') as pr:
        creader = csv.reader(pr, delimiter=',', quotechar='"')
        t = next(creader)
        for t in creader:
            temp_price = []
            assert type(t[0]) == str
            fs = t[0]
            fs = re.sub(r"(\d{4})(.)(\d{2})(.)(\d{2})", r'\1 \3 \5', str(t[0]))
            fs = datetime.datetime.strptime(fs, "%Y %m %d")
            fs = fs.strftime(format_price)
            temp_price.append(fs)

            ls = t[1]
            ls = re.sub(r"(\d{4})(.)(\d{2})(.)(\d{2})", r'\1 \3 \5', str(t[1]))
            ls = datetime.datetime.strptime(ls, "%Y %m %d")
            ls1 = ls.toordinal()
            ls = ls.strftime(format_price)
            temp_price.append(ls)

            wp = int(t[2])
            wp1 = locale.currency((wp), grouping = True)
            temp_price.append(wp1)
            temp_price.append(two_night)
            temp_price.append(three_plus)
            
            if ls1 >= ty:
                print (t)
                price_list.append(temp_price)

        min_date = price_list[1][1]
        min_date = datetime.datetime.strptime(min_date, "%d %B %Y")
        min_date = datetime.date.toordinal(min_date)

    if min_date == ty:
                    
        P = Paragraph("Mariner's Loft price list as at " + td, style)
        c = canvas.Canvas(PROJECT_DIR + "/Aldeburgh" + "/price list.pdf")
                
        doc = SimpleDocTemplate((PROJECT_DIR + "/Aldeburgh" + "/price list.pdf"), pagesize=landscape(A4))
        elements = []
        
        bt=Table(price_list,style=[('GRID',(0,0),(-1,-1),1,colors.green),
                                                ('BOX',(0,0),(-1,-1),2,colors.blue),
                                                ('BACKGROUND', (0, 0), (-1, 0), colors.lavender),
                                                ('ALIGN', (0,0), (-1,0), 'CENTER'),
                                                ('ALIGN', (1,-1), (1,-1), 'LEFT'),
                                                ('ALIGN', (-3,1), (-1,-1), 'RIGHT'),
                                                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                                                         ], colWidths=(150,150,100,100,100), repeatRows=1)
                                                         
        elements.append(P)
        elements.append(Spacer(1,24))
        elements.append(bt)
        #write the document to disk
        doc.build(elements)

    else:
        print ("Price list up to date")
