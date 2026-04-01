# Manual Testing Guide - Coupon Email Sharing

## Quick Status Summary
✅ **Email System**: FULLY WORKING
✅ **Form Submission**: FIXED (changed from links to buttons)  
✅ **Error Handling**: ENHANCED with detailed logging
✅ **Ready for Testing**: YES

## How to Test in Browser

### Step 1: Start the Server
The server should already be running at: `http://127.0.0.1:8000/`

If not, run:
```bash
python manage.py runserver
```

### Step 2: Log In
1. Open: http://127.0.0.1:8000/Client/login/
2. Use one of these test accounts:
   - **Username**: `Client 1` (HAS COUPONS - use this one!)
   - **Password**: (check your database or create new)

### Step 3: Navigate to Purchases
1. Click on "Purchases" in the sidebar
2. You should see your purchase history with coupons

### Step 4: Share a Coupon
1. Click the **"Share Coupon"** dropdown button
2. Select **"Email"** from the menu
3. A modal dialog should appear
4. Select a coupon from the dropdown
5. Enter a recipient email address
6. Click **"Send Coupon"**

### Step 5: Monitor the Process

#### Browser Console (F12)
You should see logs like:
```javascript
Sending coupon share request: {
  coupon_code: "105394420260112",
  recipient_email: "test@example.com"
}
Response received: 200
Response data: {
  success: true,
  message: "Coupon shared successfully to test@example.com"
}
```

#### Django Console
You should see:
```
[INFO] share_coupon: Client 'Client 1' found
[INFO] share_coupon: Transaction 15 found, sending to test@example.com
[DEBUG] Email template rendered successfully
[DEBUG] Logo attached to email
[INFO] Coupon email sent successfully to test@example.com
[INFO] share_coupon: Email successfully sent to test@example.com
```

## Expected Outcomes

### Success Scenario
- ✅ Green success popup appears: "Coupon shared successfully to [email]"
- ✅ Modal closes automatically
- ✅ Email is sent to recipient
- ✅ Django logs show `[INFO]` messages

### Failure Scenarios

| Symptom | Cause | Solution |
|---------|-------|----------|
| Modal doesn't open | JavaScript error | Check browser console (F12) for errors |
| "Not logged in" error | Session expired | Log in again |
| "Coupon not found" error | Trying to share someone else's coupon | Select your own coupon from dropdown |
| "Failed to send email" | Email configuration issue | Check Django logs for `[ERROR]` messages |
| Form submits as GET | Old bug (should be fixed now) | Clear browser cache and reload |

## Troubleshooting

### If Email Doesn't Send

Check the Django console for error logs starting with `[ERROR]`:

```
[ERROR] share_coupon: ...
[ERROR] Error sending coupon share email: ...
```

Then refer to the TROUBLESHOOTING_COUPON_EMAIL.md guide for detailed solutions.

### If Form Doesn't Submit

1. **Open Browser Console** (Press F12)
2. **Go to Network Tab**
3. **Try to submit the form**
4. **Look for the POST request** to `/client/share-coupon/`
5. **Check the Response**:
   - Status: should be `200`
   - Body: should be JSON with `success: true/false`

### Enable Advanced Debugging

Add this to the top of your Django console tab to see all requests:

```javascript
// In browser console:
fetch('http://127.0.0.1:8000/client/purchases/', {
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': 'TOKEN'},
  body: 'coupon_code=TEST&recipient_email=test@test.com'
})
.then(r => r.json())
.then(d => console.log('Response:', d))
.catch(e => console.error('Error:', e))
```

## Changes Made in This Session

1. **Fixed HTML Form** (client_purchases.html)
   - Changed email dropdown from `<a>` links to `<button>` elements
   - This prevents accidental navigation and ensures JavaScript event handling works correctly

2. **Enhanced JavaScript** (client_purchases.html)
   - Added input validation
   - Added detailed console logging
   - Better error handling
   - Form reset after successful submission

3. **Improved Backend Logging** (Client/views.py)
   - Added comprehensive error messages
   - Added debug information (available coupons)
   - Full exception traceback
   - Validation at each step

4. **Email Function Improvements** (Project1/email_utils.py)
   - Better template rendering error handling
   - Logo attachment failure handling
   - Detailed logging throughout

## Final Checklist

- [ ] Server running without errors
- [ ] Can log in with "Client 1"
- [ ] Can navigate to Purchases
- [ ] Share Coupon button is visible
- [ ] Email option opens modal
- [ ] Can select coupon and enter email
- [ ] Sending succeeds with green popup
- [ ] Django console shows [INFO] logs
- [ ] Email is received (if testing with real email)

## Test Results
Run this command to verify everything is working:
```bash
python manage.py shell -c "exec(open('test_coupon_sharing_flow.py').read())"
```

Expected output:
- ✓ Email sent successfully
- ✓ Form submission working
- ✓ All tests passing

---

**Status**: Ready for production testing ✅
