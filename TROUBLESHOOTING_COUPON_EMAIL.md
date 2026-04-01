## Quick Troubleshooting Guide - Coupon Email Not Sending

### Symptoms
- Client tries to share a coupon via email
- Gets error message (varies)
- Email doesn't arrive

### Step-by-Step Troubleshooting

#### 1. Check Django Console for Error Messages
When a client reports the issue, **immediately check the Django development console** for these patterns:

```
[ERROR] share_coupon: ...
[INFO] share_coupon: ...
```

#### 2. Common Error Scenarios and Solutions

| Error Message | Cause | Solution |
|---|---|---|
| `[ERROR] share_coupon: No username in session` | User not logged in | Ask user to log in again |
| `[ERROR] share_coupon: No coupon code provided` | Empty form submission | Ensure form is properly filled |
| `[ERROR] share_coupon: No recipient email provided` | Missing email address | Require user to enter email |
| `[ERROR] share_coupon: No transaction found for client` | Coupon belongs to different user | Verify user is selecting their own coupon |
| `[DEBUG] Client's available coupons: [...]` | Shows what coupons user actually has | User is trying to share wrong coupon |
| `[ERROR] Error sending coupon share email:` | SMTP/Email configuration issue | See section below |
| `[ERROR] Failed to render email template:` | Missing or broken template | Check `templates/emails/share_coupon.html` exists |

#### 3. Email Configuration Issues

If you see: `[ERROR] Error sending coupon share email: ...`

Check these in order:

**a) Test SMTP Connection**
```bash
python manage.py shell
>>> from django.core.mail import get_connection
>>> conn = get_connection()
>>> conn.open()  # If this works, SMTP is OK
>>> conn.close()
```

**b) Check Settings**
```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.EMAIL_HOST)
>>> print(settings.EMAIL_PORT)
>>> print(settings.EMAIL_USE_TLS)
>>> print(settings.EMAIL_HOST_USER)
```

**c) For Gmail, Verify App Password**
- Go to: https://myaccount.google.com/apppasswords
- If "App passwords" option is grayed out:
  - Enable 2-factor authentication first
  - Then create an App Password
  - Update `EMAIL_HOST_PASSWORD` in settings.py

**d) Send Test Email**
```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> from django.conf import settings
>>> send_mail('Test', 'Test body', settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
>>> # Should print True and you should receive the email
```

#### 4. Run Full Diagnostic
```bash
python manage.py shell < test_coupon_email.py
```
This runs all checks and shows you what's working and what's not.

### If All Tests Pass But Still Having Issues

1. **Check Browser Console** (F12 in browser)
   - Look for JavaScript errors
   - Check Network tab to see the actual response from server

2. **Check Server Response**
   - The view should return JSON with `'success': true/false`
   - Look for the actual error message in the response

3. **Check Email Logs**
   - Some email services block email from development servers
   - Gmail might require "Less secure app access" (old accounts)
   - Check spam folder

4. **Enable Full Logging**
   Add to `Project1/settings.py`:
   ```python
   LOGGING = {
       'version': 1,
       'handlers': {
           'console': {'class': 'logging.StreamHandler'},
       },
       'loggers': {
           'Project1.email_utils': {'handlers': ['console'], 'level': 'DEBUG'},
           'Client.views': {'handlers': ['console'], 'level': 'DEBUG'},
       },
   }
   ```

### Contact Support
If issues persist after these steps, provide:
1. The complete `[ERROR]` or `[INFO]` log lines from console
2. The exact error message shown to user
3. Results of the `test_coupon_email.py` diagnostic
