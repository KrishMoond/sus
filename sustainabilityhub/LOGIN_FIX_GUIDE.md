# Login Issue Fix Guide

## 🔧 Problem Diagnosis

If you can't login even with correct credentials, here's how to fix it:

### **Quick Fix: Reset Password**

1. **Reset Password via Script:**
   ```bash
   cd sustainabilityhub
   python reset_user_password.py <username> <new_password>
   ```
   
   Example:
   ```bash
   python reset_user_password.py krish mypassword123
   ```

2. **Or Reset via Django Admin:**
   - Login as superuser: `python manage.py createsuperuser`
   - Go to: `http://127.0.0.1:8000/admin/`
   - Navigate to **Users**
   - Click on the user
   - Scroll to password section
   - Change password

---

## 🐛 Common Issues & Solutions

### Issue 1: "Invalid username or password"

**Causes:**
- Username is case-sensitive (check exact spelling)
- Password was forgotten or not set correctly during registration
- Account is inactive

**Solutions:**
1. **Reset password** using the script above
2. **Register a new account** - new accounts auto-login after registration
3. **Check username spelling** - it's case-sensitive

### Issue 2: Form not submitting

**Check:**
- Browser console for JavaScript errors
- Network tab to see if POST request is sent
- CSRF token is present (check page source)

**Fix:**
- Clear browser cache
- Try in incognito/private mode
- Check that server is running

### Issue 3: Can't type in fields

**This should now be fixed** - input fields have explicit styling with visible text.

---

## ✅ Test Login

1. **Register a new account:**
   - Go to: `/accounts/register/`
   - Create account → You'll be auto-logged in

2. **Login with existing account:**
   - Reset password first: `python reset_user_password.py <username> <new_password>`
   - Then login at: `/accounts/login/`

3. **Check user status:**
   ```bash
   python test_login.py
   ```

---

## 🆘 Still Can't Login?

1. **Create a new account** - Registration now auto-logs you in
2. **Use Django admin** to reset password:
   ```bash
   python manage.py createsuperuser
   # Then go to /admin/ and reset user password
   ```

3. **Check the error message** - The login form now shows specific error messages

---

## 📝 Important Notes

- **Passwords are hashed** - We can't see your actual password
- **Username is case-sensitive** - "Krish" ≠ "krish"
- **New registrations auto-login** - No need to login after creating account
- **All users are active by default** - Unless manually deactivated

