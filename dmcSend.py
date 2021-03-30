class dmcSend:

        """Sends an email to Caroline and Richard with a list of upcoming
        bookings using 'confirmed.txt'"""

        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.utils import formatdate
        from email import encoders
        from email.errors import HeaderParseError
        import datetime

        ty = datetime.date.today()
        date_format = '%A %d %B %Y'

        # me == my email address # you == recipient's email address
        me = "owners@marinersaldeburgh.com"
        you = ["caroline@darton-moore.co.uk", "richard@darton-moore.co.uk"]


        dmct =  '/home/sidestrand/new_mariners/textFiles/confirmed.txt'
        dmct_html =  '/home/sidestrand/new_mariners/textFiles/confirmed.html'

        fp = open(dmct, 'rb')
        fp2 = open(dmct_html, 'rb')        

        # Record the MIME types of both parts - text/plain and text/html.

        html = fp2.read()
        fp2.close()
        
        text = fp.read()
        fp.close()

        # Format headers
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "latest bookings list: " + ty.strftime(date_format)
        msg['From'] = me
        msg['To'] = ", ".join(you)
        msg['Date'] = formatdate(localtime=True)
        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))

        try:
            server = smtplib.SMTP("auth.smtp.1and1.co.uk", 587)
            server.login('owners@marinersaldeburgh.com', "T1nk3r52ma~")
            server.sendmail(me, you, msg.as_string())
            server.quit()
        except HeaderParseError:
            print "Error: unable to send email"
