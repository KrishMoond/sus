# Admin Setup Guide

## Step 1: Create Admin/Superuser Account

Run this command in your terminal:

```bash
cd sustainabilityhub
python manage.py createsuperuser
```

You'll be prompted to enter:
- **Username**: (e.g., `admin`)
- **Email**: (optional, e.g., `admin@example.com`)
- **Password**: (enter a strong password twice)

**Example:**
```
Username: admin
Email address: admin@sustainabilityhub.com
Password: ********
Password (again): ********
Superuser created successfully.
```

---

## Step 2: Create Default Categories

After creating your superuser, run these commands to create default categories:

### For Forums:
```bash
python manage.py create_default_categories
```

### For Resources:
```bash
python manage.py create_default_categories --app resources
```

**Or run both at once:**
```bash
python manage.py create_default_categories
python manage.py create_default_categories --app resources
```

---

## Step 3: Access Admin Panel

1. Start your Django server:
   ```bash
   python manage.py runserver
   ```

2. Open your browser and go to:
   ```
   http://127.0.0.1:8000/admin/
   ```

3. Login with your superuser credentials

4. You can now:
   - View all users, projects, events, etc.
   - Create/edit/delete forum categories
   - Create/edit/delete resource categories
   - Manage all content

---

## Alternative: Create Categories via Admin Panel

1. Login to `/admin/`
2. Go to **Forums** → **Categories** → Click **"Add Category"**
3. Create categories manually:
   - General Discussion
   - Projects & Collaborations
   - Resources & Tools

4. Go to **Resources** → **Resource Categories** → Click **"Add Resource Category"**
5. Create categories manually:
   - Articles & Guides
   - Tools & Apps
   - Research & Studies

---

## Quick Setup Script

You can also run the Python script:

```bash
python setup_defaults.py
```

This will create 3 default categories for both forums and resources automatically.

---

## Troubleshooting

**Can't login to admin?**
- Make sure you created a superuser with `python manage.py createsuperuser`
- Check that `is_superuser` is True in the admin panel

**Categories not showing?**
- Run the management commands: `python manage.py create_default_categories`
- Check the admin panel to see if categories exist
- Make sure migrations are applied: `python manage.py migrate`

