alumni-donation-system/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── database.py           # Database models and functions
├── email_service.py      # Email sending service
├── certificate.py        # Certificate generation
├── render.yaml          # Render deployment config
├── templates/
│   ├── index.html       # Public donation page
│   ├── admin_login.html # Admin login
│   ├── admin_dashboard.html # Admin panel
│   └── email_templates/
│       └── certificate.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js