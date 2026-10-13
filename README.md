# Handora (Desihands) - Handmade with Love

> An artisan e-commerce platform and staff administration portal built with Django, Razorpay, ReportLab, and SQLite.

---

## 📖 Table of Contents
1. [Project Description](#-project-description)
2. [Technology Stack](#-technology-stack)
3. [Working Demo Credentials](#-working-demo-credentials)
4. [Screen Directory & Page Titles](#-screen-directory--page-titles)
5. [Key Features & System Architecture](#-key-features--system-architecture)
6. [Installation & Setup Guide](#-installation--setup-guide)
7. [Environment Configuration](#-environment-configuration)
8. [Project File Structure](#-project-file-structure)

---

## 🛍️ Project Description

**Handora** (internal project codebase: `desihands`) is a full-stack e-commerce web platform engineered for handcrafted Indian heritage products, decor, textiles, wooden crafts, and lifestyle accessories.

The application serves two distinct user groups:
1. **Shoppers & Customers**: Provides a catalog experience to browse collections, search and sort items, save to wishlist, manage a shopping cart, and check out using either **Cash on Delivery (with 6-digit email OTP verification)** or **Razorpay (UPI, Credit/Debit Cards, Net Banking, EMI, and Wallets)**. Customers automatically receive PDF invoices via email and order confirmation links.
2. **Shop Administrators & Staff**: Features a custom staff administration portal (`/admin/`) independent of the standard Django admin. The admin portal delivers real-time business metrics (monthly revenue charts, order status distributions), catalog management (categories & products with inline availability and discount toggles), user account roles, order tracking, and a customer inquiry reply desk with outbound email integration.

---

## 🛠️ Technology Stack

| Layer | Technologies & Libraries |
| :--- | :--- |
| **Backend Framework** | Python 3.14, Django 6.0 |
| **Database** | SQLite3 (`db.sqlite3`) |
| **Payment Gateway** | Razorpay Python SDK (`razorpay>=1.4.0`), Razorpay Checkout.js modal |
| **PDF Generation** | ReportLab 4.x (`reportlab>=4.0.0`), xhtml2pdf |
| **QR Code Generation** | `qrcode>=8.0` |
| **Image & Media** | Pillow (`Pillow>=10.0.0`) |
| **Security & Env** | `python-dotenv`, `cryptography`, Django `TimestampSigner` |
| **Frontend** | Django Template Engine, Vanilla JavaScript, CSS3 (`style.css`, `admin.css`) |

---

## 🔐 Working Demo Credentials

Pre-configured, verified demo credentials ready for immediate testing:

### 1. Store Administrator / Staff Account
- **Username**: `demo_admin`
- **Password**: `Admin@12345`
- **Role**: Superuser & Staff (`is_staff=True`, `is_superuser=True`)
- **Login URL**: `http://127.0.0.1:8000/admin/login/` (or `http://127.0.0.1:8000/login/`)
- **Capabilities**: Full access to the custom Admin Dashboard, revenue analytics, products, categories, orders, user roles, and customer feedback.

### 2. Shopper / Customer Account
- **Username**: `demo_user`
- **Password**: `User@12345`
- **Role**: Standard Customer (`is_staff=False`)
- **Login URL**: `http://127.0.0.1:8000/login/`
- **Capabilities**: Browse catalog, add items to cart, wishlist items, checkout via COD or Razorpay, and download order invoices.

---

## 🖥️ Screen Directory & Page Titles

The application includes the following customer storefront and staff portal screens:

| # | Screen Title | Route URL | Template | Access | Key Features |
| :- | :--- | :--- | :--- | :- | :--- |
| 1 | **Home - Handora** | `/` | `home.html` | Public | Hero banner, categories grid, featured items, bestsellers, new arrivals |
| 2 | **[Category Name] - Handora** | `/category/<slug>/` | `category.html` | Public | Product grid, price/discount sorting, pagination, wishlist toggles |
| 3 | **[Product Name] - Handora** | `/product/<slug>/` | `product_detail.html` | Public | High-res imagery, rating stars, MRP/discount badges, quantity counter, add to cart |
| 4 | **Search Results - Handora** | `/search/?q=...` | `search_results.html` | Public | Multi-keyword search parser with `featured` and `bestseller` filter tags |
| 5 | **Your Cart - Handora** | `/cart/` | `cart.html` | Public | Line items, AJAX quantity updates, dynamic subtotal calculation, removal confirmation |
| 6 | **Checkout - Handora** | `/checkout/` | `checkout.html` | Authenticated | Delivery address, contact info, order summary inspection |
| 7 | **Choose Payment Method - Handora** | `/payment/` | `payment_method.html` | Authenticated | COD selection or Razorpay checkout modal (UPI, Cards, Net Banking) |
| 8 | **COD Email Verification - Handora** | `/cod_email/` | `cod_email.html` | Authenticated | Email prompt for OTP dispatch before COD finalization |
| 9 | **COD OTP Verification - Handora** | `/cod_otp/` | `cod_otp.html` | Authenticated | 6-digit OTP entry with 5-minute expiry countdown and resend option |
| 10 | **Order Confirmation - Handora** | `/order_success/<id>/` | `order_success.html` | Authenticated | Order success message, payment reference, and instant invoice PDF download button |
| 11 | **Handora Invoice / Bill (PDF)** | `/bill/<order_id>/` | Generated via ReportLab | Authenticated | Professional A4 PDF receipt with order summary, customer details, and tax totals |
| 12 | **Secure Receipt (PDF Token)** | `/receipt/<token>/` | Generated via ReportLab | Token-signed | Cryptographically signed temporary link included in order confirmation emails |
| 13 | **My Wishlist - Handora** | `/wishlist/` | `wishlist.html` | Authenticated | Saved favorite products with quick "Move to Cart" and "Remove" options |
| 14 | **Sign In - Handora** | `/login/` | `login.html` | Public | Username & password authentication with eye-toggle password reveal |
| 15 | **Register - Handora** | `/register/` | `register.html` | Public | Customer onboarding capturing Name, Email, 10-digit Phone, and Password validation |
| 16 | **Password Reset - Handora** | `/password-reset/` | `password_reset.html` | Public | Email input to request a 6-digit password reset OTP |
| 17 | **Verify Reset OTP - Handora** | `/verify-reset-otp/` | `verify_reset_otp.html` | Public | OTP verification with secure HMAC comparison and expiration handling |
| 18 | **New Password - Handora** | `/reset-password/` | `password_reset_confirm.html`| Public | Set new password with confirmation and Django password validators |
| 19 | **Password Reset Done - Handora**| `/password-reset/done/`| `password_reset_done.html` | Public | Success screen confirming updated credentials |
| 20 | **About Us - Handora** | `/about/` | `about.html` | Public | Brand heritage and artisan craftsmanship story |
| 21 | **Our Story - Handora** | `/our-story/` | `our_story.html` | Public | Detailed brand origin narrative |
| 22 | **Our Commitment - Handora** | `/our-commitment/` | `our_commitment.html` | Public | Ethical sourcing, eco-friendly materials, and fair wages |
| 23 | **Artisan Partners - Handora** | `/artisan-partners/` | `artisan_partners.html` | Public | Profiles and regional backgrounds of partner artisan communities |
| 24 | **Contact Us - Handora** | `/contact/` | `contact.html` | Public | Contact form saving inquiries into `ContactMessage` model |
| 25 | **FAQ - Handora** | `/faq/` | `faq.html` | Public | Common ordering, shipping, and return questions |
| 26 | **Shipping Policy - Handora** | `/shipping/` | `shipping.html` | Public | Shipping timelines, packaging, and delivery terms |
| 27 | **Privacy Policy - Handora** | `/privacy-policy/` | `privacy_policy.html` | Public | User data retention, security, and cookies policy |
| 28 | **Terms & Conditions - Handora** | `/terms/` | `terms.html` | Public | Legal agreement for site usage and purchases |
| 29 | **Admin Login - Handora** | `/admin/login/` | `admin_panel/login.html` | Public | Dedicated staff authentication screen |
| 30 | **Admin Dashboard - Handora** | `/admin/dashboard/` | `admin_panel/dashboard.html`| Staff Only | Revenue cards, monthly revenue bar charts, order status donut charts |
| 31 | **Admin Categories - Handora** | `/admin/categories/`| `admin_panel/categories.html`| Staff Only | Category table with product counts, edit links, and deletion workflows |
| 32 | **Admin Products - Handora** | `/admin/products/` | `admin_panel/products.html` | Staff Only | Product catalog with inline AJAX switches for availability and discount |
| 33 | **Admin Users - Handora** | `/admin/users/` | `admin_panel/users.html` | Staff Only | User administration list with staff badge indicators and phone numbers |
| 34 | **Admin Orders - Handora** | `/admin/orders/` | `admin_panel/orders.html` | Staff Only | Order tracking list with filters by status (Pending, Confirmed, Shipped, Delivered) |
| 35 | **Admin Order Detail - Handora** | `/admin/orders/<id>/`| `admin_panel/order_detail.html`| Staff Only | Full order invoice details, items table, and status transition selector |
| 36 | **Admin Feedback - Handora** | `/admin/feedback/` | `admin_panel/feedback.html` | Staff Only | Customer contact messages, unread badge counter, and mark-read controls |
| 37 | **Admin Feedback Reply - Handora**| `/admin/feedback/<id>/reply/`| `admin_panel/feedback_reply.html`| Staff Only | In-browser email drafting interface to reply directly to customer inquiries |
| 38 | **Django Core Admin** | `/django-admin/` | Standard Django Admin | Superuser | Built-in fallback administration site |

---

## ⚙️ Key Features & System Architecture

### 1. Catalog & Smart Search Parser
- **Category Hierarchy**: Categories auto-slugify and link to paginated product sets.
- **Search Engine**: In `main/views.py`, the search engine splits terms and extracts boolean flags (`featured`, `bestseller`) from keyword terms, combining them into ORM querysets (`Q(...)`).

### 2. Session Cart System (`main/cart.py`)
- Independent session-based cart stored at `request.session['cart']`.
- Quantities capped at 15 items per product.
- Real-time subtotal and grand total recalculations via AJAX and HTML data attributes.

### 3. Payment Processing
- **Cash on Delivery (COD)**: Protected with email-based OTP verification. A cryptographically random 6-digit OTP is issued with a 5-minute time-to-live (`time.time() + 300`).
- **Razorpay Integration**: Creates a remote server-side Razorpay Order (`client.order.create`), initializes `Razorpay(options)` in JavaScript, and verifies payment signatures server-side at `/payment/verify/`.

### 4. Automated PDF Billing (`ReportLab`)
- Orders generate an official A4 invoice (`Handora_Bill_Order_<id>.pdf`) with brand styling, order timestamps, line items, unit pricing, discounts, shipping breakdown, and payment identifiers.
- Generated PDFs are dispatched as email attachments upon order confirmation and made available for customer download.

---

## 🚀 Installation & Setup Guide

### 1. Prerequisites
- Python 3.10+ (Python 3.14 recommended)
- `pip` package manager

### 2. Setup Virtual Environment
```bash
# Navigate to the project root
cd "C:\antigravity project\desihands"

# Create a virtual environment (if not already present)
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows Command Prompt:
.\venv\Scripts\activate.bat
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations & Static Files
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### 5. Launch the Development Server
```bash
python manage.py runserver
```

Open your browser at `http://127.0.0.1:8000/`.

---

## 🔒 Environment Configuration

Configuration variables are stored in `.env` in the project root:

```env
# Email Configuration (SMTP Gmail)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Razorpay Test / Production Keys
RAZORPAY_KEY_ID=rzp_test_YourKeyId
RAZORPAY_KEY_SECRET=YourKeySecret

# Application Settings
DEBUG=True
SECRET_KEY=your-secure-random-django-secret-key
SITE_BASE_URL=http://127.0.0.1:8000
```

---

## 📁 Project File Structure

```
desihands/
├── .env                              # Environment configuration (secrets, SMTP, Razorpay)
├── .gitignore                        # Git exclusion rules
├── db.sqlite3                        # SQLite database
├── manage.py                         # Django execution utility
├── requirements.txt                  # Python dependencies
├── README.md                         # Project documentation and screen guide
├── desihands/                        # Project configuration module
│   ├── settings.py                   # Django settings, apps, templates, auth, payments
│   ├── urls.py                       # Root URL routes (/admin/, /django-admin/, /)
│   ├── wsgi.py                       # WSGI entry point
│   └── asgi.py                       # ASGI entry point
├── main/                             # Core e-commerce application
│   ├── admin.py                      # Django standard admin registrations
│   ├── admin_forms.py                # Admin CRUD forms (Product, Category, User)
│   ├── admin_urls.py                 # Custom staff admin routes (/admin/...)
│   ├── admin_views.py                # Staff dashboard & management view logic
│   ├── cart.py                       # Session cart class
│   ├── context_processors.py         # Global template variables (categories, cart_count, wishlist_count)
│   ├── email_utils.py                # Order confirmation email dispatcher
│   ├── forms.py                      # Customer registration & product forms
│   ├── models.py                     # Category, Product, Profile, Wishlist, Order, OrderItem, ContactMessage
│   ├── urls.py                       # Storefront URL patterns
│   ├── views.py                      # Storefront, cart, checkout, payments, bills
│   └── templates/                    # HTML template views
│       ├── base.html                 # Master layout (navbar, brand logo, footer)
│       ├── home.html                 # Storefront homepage
│       ├── category.html             # Product catalog by category
│       ├── product_detail.html       # Single product details
│       ├── search_results.html       # Search results listing
│       ├── cart.html                 # Shopping cart
│       ├── checkout.html             # Customer address entry
│       ├── payment_method.html       # Payment choice & Razorpay modal
│       ├── cod_email.html / cod_otp.html # COD OTP workflow
│       ├── order_success.html        # Order confirmation & bill download
│       ├── wishlist.html             # Customer wishlist
│       ├── login.html / register.html# Authentication screens
│       ├── password_reset*.html      # OTP password recovery
│       ├── admin_panel/              # Custom staff administration templates
│       │   ├── dashboard.html        # Analytics dashboard
│       │   ├── products.html         # Product management
│       │   ├── categories.html       # Category management
│       │   ├── orders.html           # Order management
│       │   ├── users.html            # User & permission management
│       │   └── feedback.html         # Customer contact messages
│       └── email/                    # HTML email templates
│           └── order_confirmation.html
├── static/                           # Static assets
│   ├── css/
│   │   ├── style.css                 # Storefront styles
│   │   └── admin.css                 # Admin panel styles
│   └── images/
│       ├── handora-logo.png          # Main navbar logo
│       ├── handora.png               # Brand badge
│       ├── appstore.svg
│       └── playstore.svg
└── media/                            # User uploads (product & category photos)
    ├── categories/
    └── products/
```
