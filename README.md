# Handora (Desihands) - Handmade with Love

> An artisan e-commerce platform and staff administration portal built with Django, Razorpay, ReportLab, and SQLite.

---

## 📖 Table of Contents
1. [Project Description](#-project-description)
2. [Technology Stack](#-technology-stack)
3. [Working Demo Credentials](#-working-demo-credentials)
4. [Website Screenshots Gallery](#-website-screenshots-gallery)
5. [Screen Directory & Page Titles](#-screen-directory--page-titles)
6. [Key Features & System Architecture](#-key-features--system-architecture)
7. [Installation & Setup Guide](#-installation--setup-guide)
8. [Environment Configuration](#-environment-configuration)
9. [Project File Structure](#-project-file-structure)

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

## 📸 Website Screenshots Gallery

### 1. Storefront & Catalog

#### Home Page (`/`)
![Home Page](screenshots/01_home.png)

#### Category Catalog (`/category/wooden-craft/`)
![Category Catalog](screenshots/02_category_catalog.png)

#### Product Details (`/product/deer-shelf/`)
![Product Details](screenshots/03_product_details.png)

#### Smart Search Results (`/search/?q=wooden`)
![Search Results](screenshots/04_search_results.png)

---

### 2. Cart, Checkout & Orders

#### Shopping Cart (`/cart/`)
![Shopping Cart](screenshots/05_shopping_cart.png)

#### Checkout & Address Entry (`/checkout/`)
![Checkout](screenshots/06_checkout.png)

#### Payment Method Selection (`/payment/`)
![Payment Method Selection](screenshots/07_payment_method.png)

#### Order Confirmation & Instant Invoice (`/order_success/<id>/`)
![Order Confirmation](screenshots/08_order_success.png)

#### Customer Wishlist (`/wishlist/`)
![Wishlist](screenshots/09_wishlist.png)

---

### 3. User Authentication & Password Recovery

#### Sign In (`/login/`)
![Sign In](screenshots/10_login.png)

#### User Registration (`/register/`)
![User Registration](screenshots/11_register.png)

#### Password Reset OTP (`/password-reset/`)
![Password Reset](screenshots/12_password_reset.png)

---

### 4. Brand & Informational Pages

#### About Us (`/about/`)
![About Us](screenshots/13_about_us.png)

#### Our Story (`/our-story/`)
![Our Story](screenshots/14_our_story.png)

#### Our Commitment (`/our-commitment/`)
![Our Commitment](screenshots/15_our_commitment.png)

#### Artisan Partners (`/artisan-partners/`)
![Artisan Partners](screenshots/16_artisan_partners.png)

#### Contact Us (`/contact/`)
![Contact Us](screenshots/17_contact.png)

#### Frequently Asked Questions (`/faq/`)
![FAQs](screenshots/18_faq.png)

#### Shipping Policy (`/shipping/`)
![Shipping Policy](screenshots/19_shipping.png)

#### Privacy Policy (`/privacy-policy/`)
![Privacy Policy](screenshots/20_privacy_policy.png)

#### Terms & Conditions (`/terms/`)
![Terms & Conditions](screenshots/21_terms.png)

---

### 5. Staff Administration Portal (`/admin/`)

#### Staff Login (`/admin/login/`)
![Admin Login](screenshots/22_admin_login.png)

#### Admin Analytics Dashboard (`/admin/dashboard/`)
![Admin Dashboard](screenshots/23_admin_dashboard.png)

#### Category Management (`/admin/categories/`)
![Admin Categories](screenshots/24_admin_categories.png)

#### Product Catalog Management (`/admin/products/`)
![Admin Products](screenshots/25_admin_products.png)

#### Order Management (`/admin/orders/`)
![Admin Orders](screenshots/26_admin_orders.png)

#### Order Details & Status Workflow (`/admin/orders/<id>/`)
![Admin Order Details](screenshots/27_admin_order_detail.png)

#### User Accounts & Roles (`/admin/users/`)
![Admin Users](screenshots/28_admin_users.png)

#### Customer Feedback & Email Desk (`/admin/feedback/`)
![Admin Feedback](screenshots/29_admin_feedback.png)

---

## 🖥️ Screen Directory & Page Titles

The application includes the following customer storefront and staff portal screens:

| # | Screen Title | Route URL | Template | Access | Screenshot |
| :- | :--- | :--- | :--- | :- | :--- |
| 1 | **Home - Handora** | `/` | `home.html` | Public | [View](screenshots/01_home.png) |
| 2 | **[Category Name] - Handora** | `/category/<slug>/` | `category.html` | Public | [View](screenshots/02_category_catalog.png) |
| 3 | **[Product Name] - Handora** | `/product/<slug>/` | `product_detail.html` | Public | [View](screenshots/03_product_details.png) |
| 4 | **Search Results - Handora** | `/search/?q=...` | `search_results.html` | Public | [View](screenshots/04_search_results.png) |
| 5 | **Your Cart - Handora** | `/cart/` | `cart.html` | Public | [View](screenshots/05_shopping_cart.png) |
| 6 | **Checkout - Handora** | `/checkout/` | `checkout.html` | Authenticated | [View](screenshots/06_checkout.png) |
| 7 | **Choose Payment Method - Handora** | `/payment/` | `payment_method.html` | Authenticated | [View](screenshots/07_payment_method.png) |
| 8 | **COD Email Verification - Handora** | `/cod_email/` | `cod_email.html` | Authenticated | [View](screenshots/07_payment_method.png) |
| 9 | **COD OTP Verification - Handora** | `/cod_otp/` | `cod_otp.html` | Authenticated | [View](screenshots/12_password_reset.png) |
| 10 | **Order Confirmation - Handora** | `/order_success/<id>/` | `order_success.html` | Authenticated | [View](screenshots/08_order_success.png) |
| 11 | **Handora Invoice / Bill (PDF)** | `/bill/<order_id>/` | ReportLab PDF | Authenticated | [View](screenshots/08_order_success.png) |
| 12 | **Secure Receipt (PDF Token)** | `/receipt/<token>/` | ReportLab PDF | Token-signed | [View](screenshots/08_order_success.png) |
| 13 | **My Wishlist - Handora** | `/wishlist/` | `wishlist.html` | Authenticated | [View](screenshots/09_wishlist.png) |
| 14 | **Sign In - Handora** | `/login/` | `login.html` | Public | [View](screenshots/10_login.png) |
| 15 | **Register - Handora** | `/register/` | `register.html` | Public | [View](screenshots/11_register.png) |
| 16 | **Password Reset - Handora** | `/password-reset/` | `password_reset.html` | Public | [View](screenshots/12_password_reset.png) |
| 17 | **About Us - Handora** | `/about/` | `about.html` | Public | [View](screenshots/13_about_us.png) |
| 18 | **Our Story - Handora** | `/our-story/` | `our_story.html` | Public | [View](screenshots/14_our_story.png) |
| 19 | **Our Commitment - Handora** | `/our-commitment/` | `our_commitment.html` | Public | [View](screenshots/15_our_commitment.png) |
| 20 | **Artisan Partners - Handora** | `/artisan-partners/` | `artisan_partners.html` | Public | [View](screenshots/16_artisan_partners.png) |
| 21 | **Contact Us - Handora** | `/contact/` | `contact.html` | Public | [View](screenshots/17_contact.png) |
| 22 | **FAQ - Handora** | `/faq/` | `faq.html` | Public | [View](screenshots/18_faq.png) |
| 23 | **Shipping Policy - Handora** | `/shipping/` | `shipping.html` | Public | [View](screenshots/19_shipping.png) |
| 24 | **Privacy Policy - Handora** | `/privacy-policy/` | `privacy_policy.html` | Public | [View](screenshots/20_privacy_policy.png) |
| 25 | **Terms & Conditions - Handora** | `/terms/` | `terms.html` | Public | [View](screenshots/21_terms.png) |
| 26 | **Admin Login - Handora** | `/admin/login/` | `admin_panel/login.html` | Public | [View](screenshots/22_admin_login.png) |
| 27 | **Admin Dashboard - Handora** | `/admin/dashboard/` | `admin_panel/dashboard.html`| Staff Only | [View](screenshots/23_admin_dashboard.png) |
| 28 | **Admin Categories - Handora** | `/admin/categories/`| `admin_panel/categories.html`| Staff Only | [View](screenshots/24_admin_categories.png) |
| 29 | **Admin Products - Handora** | `/admin/products/` | `admin_panel/products.html` | Staff Only | [View](screenshots/25_admin_products.png) |
| 30 | **Admin Orders - Handora** | `/admin/orders/` | `admin_panel/orders.html` | Staff Only | [View](screenshots/26_admin_orders.png) |
| 31 | **Admin Order Detail - Handora** | `/admin/orders/<id>/`| `admin_panel/order_detail.html`| Staff Only | [View](screenshots/27_admin_order_detail.png) |
| 32 | **Admin Users - Handora** | `/admin/users/` | `admin_panel/users.html` | Staff Only | [View](screenshots/28_admin_users.png) |
| 33 | **Admin Feedback - Handora** | `/admin/feedback/` | `admin_panel/feedback.html` | Staff Only | [View](screenshots/29_admin_feedback.png) |
| 34 | **Django Core Admin** | `/django-admin/` | Built-in Admin | Superuser | Default backend |

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

Configuration variables are stored in `.env` in the project root (see `.env.example` for the template):

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
├── .env.example                      # Environment variables skeleton
├── .gitignore                        # Git exclusion rules (excludes .env, venv, db.sqlite3)
├── db.sqlite3                        # SQLite database (local only, not in git)
├── manage.py                         # Django execution utility
├── requirements.txt                  # Python dependencies
├── README.md                         # Project documentation and visual screenshots gallery
├── screenshots/                      # High-resolution screenshots of all 29 website pages
│   ├── 01_home.png
│   ├── 02_category_catalog.png
│   ├── 03_product_details.png
│   ├── 04_search_results.png
│   ├── 05_shopping_cart.png
│   ├── 06_checkout.png
│   ├── 07_payment_method.png
│   ├── 08_order_success.png
│   ├── 09_wishlist.png
│   ├── 10_login.png
│   ├── ...
│   └── 29_admin_feedback.png
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
