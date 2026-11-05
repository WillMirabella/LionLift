# Sends an email
# For now this just prints it in the terminal running flask so we can test without an email account
# Later, swap the print for a real email provider and nothing else has to change
def send_email(to, subject, body):
    print(f"\n----- EMAIL to {to} -----\nSubject: {subject}\n\n{body}\n-------------------------\n")
