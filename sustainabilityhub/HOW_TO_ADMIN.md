# How to Login as Admin and Create Categories

## 🎯 Quick Answer

### 1. Create Admin Account
```bash
cd sustainabilityhub
python manage.py createsuperuser
```
Enter your username, email, and password.

### 2. Create Default Categories
```bash
python setup_all_categories.py
```

### 3. Login to Admin Panel
1. Start server: `python manage.py runserver`
2. Go to: http://127.0.0.1:8000/admin/
3. Login with your superuser credentials

---

## 📝 Detailed Steps

### Step 1: Create Superuser Account

Open PowerShell or Command Prompt in your project folder and run:

```bash
cd C:\Users\Krish\Desktop\sustain_hub\sustainabilityhub
python manage.py createsuperuser
```

You'll be asked for:
- **Username**: Choose any (e.g., `admin` or `yourname`)
- **Email**: Your email (optional but recommended)
- **Password**: Create a strong password (enter twice)

**Example:**
```
Username (leave blank to use 'Krish'): admin
Email address: admin@example.com
Password: 
Password (again): 
Superuser created successfully.
```

✅ **You now have admin access!**

---

### Step 2: Create Default Categories

**Easiest Method - Run the setup script:**
```bash
python setup_all_categories.py
```

This will create:
- **3 Forum Categories**: General Discussion, Projects & Collaborations, Resources & Tools
- **3 Resource Categories**: Articles & Guides, Tools & Apps, Research & Studies

**Alternative Methods:**

**Method A: Using Management Commands**
```bash
# For forum categories
python manage.py create_default_categories

# For resource categories (if needed)
# Use admin panel or the setup script above
```

**Method B: Using Admin Panel**
1. Login to `/admin/`
2. Go to **Forums → Categories** → **Add Category**
3. Create categories one by one
4. Go to **Resources → Resource Categories** → **Add Resource Category**
5. Create resource categories

---

### Step 3: Access Admin Panel

1. **Start Django Server:**
   ```bash
   python manage.py runserver
   ```

2. **Open Browser:**
   Go to: http://127.0.0.1:8000/admin/

3. **Login:**
   Use the username and password you created in Step 1

4. **You're in!** You can now:
   - View all users, projects, events, forums, resources
   - Create/edit/delete categories
   - Manage all content
   - Access admin dashboard at `/accounts/admin/dashboard/`

---

## ✅ Verification

After creating categories, verify they exist:

1. **Check Forums:**
   - Go to: http://127.0.0.1:8000/forums/categories/
   - You should see categories listed

2. **Check Resources:**
   - Go to: http://127.0.0.1:8000/resources/
   - When creating a resource, categories should appear in dropdown

3. **Check Admin Panel:**
   - Go to: http://127.0.0.1:8000/admin/
   - Navigate to **Forums → Categories** - should show your categories
   - Navigate to **Resources → Resource Categories** - should show your categories

---

## 🔧 Troubleshooting

**"I can't login to admin"**
- Make sure you created superuser: `python manage.py createsuperuser`
- Check username/password are correct
- Try creating a new superuser with different username

**"Categories still not showing"**
- Run: `python setup_all_categories.py`
- Check admin panel to see if categories exist
- Refresh your browser (Ctrl+F5)
- Make sure server is running

**"Command not found"**
- Make sure you're in the `sustainabilityhub` directory
- Check Python is installed: `python --version`
- Use: `python manage.py` (not `django-admin`)

---

## 📚 Summary

1. ✅ Create superuser: `python manage.py createsuperuser`
2. ✅ Create categories: `python setup_all_categories.py`
3. ✅ Login: http://127.0.0.1:8000/admin/
4. ✅ Verify: Check `/forums/categories/` and `/resources/`

**That's it! You're all set!** 🎉

