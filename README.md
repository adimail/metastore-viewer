# Metastore Viewer for Lakehouse Tables on Object Stores

_COEP Inspiron hackathon_

[Demo Video](https://github.com/adimail/metastore-viewer/raw/main/docs/app-demo-v1.mp4)

---

## Prerequisites

- **Python 3.8+** (with pip)
- **Node.js and npm**

---

## Setup Instructions

1. **Clone the Repository and Navigate to the Project Folder**

   ```bash
   git clone https://github.com/adimail/metastore-viewer.git
   cd metastore-viewer
   ```

2. **(Optional) Create and Activate a Virtual Environment**

   ```bash
   python -m venv venv
   # Activate on Unix/macOS:
   source venv/bin/activate
   # Activate on Windows:
   venv\Scripts\activate
   ```

3. **Change Directory to the Web Application**

   ```bash
   cd web-app
   ```

4. **Install Python Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Install Node.js Dependencies**

   ```bash
   npm install
   ```

6. **Run TailwindCSS**

   ```bash
   npx tailwindcss -i ./app/static/css/input.css -o ./app/static/css/tailwind.css --watch
   ```

7. **Start the Application**

   ```bash
   python app.py
   ```

---

## Project Structure

```
.
└── web-app
    ├── app
    │   ├── __init__.py
    │   ├── blueprints
    │   │   ├── __init__.py
    │   │   ├── admin.py
    │   │   ├── api.py
    │   │   ├── auth
    │   │   │   └── auth.py
    │   │   ├── core
    │   │   │   ├── explorer.py
    │   │   │   ├── metadata.py
    │   │   │   ├── query_editor.py
    │   │   │   ├── settings.py
    │   │   │   └── workspace.py
    │   │   └── home.py
    │   ├── extensions.py
    │   ├── models.py
    │   ├── static
    │   │   ├── css
    │   │   │   ├── auth.css
    │   │   │   ├── errors.css
    │   │   │   ├── index.css
    │   │   │   ├── input.css
    │   │   │   └── tailwind.css
    │   │   ├── img
    │   │   │   ├── login.jpeg
    │   │   │   └── register.jpeg
    │   │   └── js
    │   │       ├── script.js
    │   │       ├── session.js
    │   │       └── table_metadata_viewer.js
    │   └── templates
    │       ├── admin
    │       │   └── admin.html
    │       ├── auth
    │       │   ├── login.html
    │       │   ├── profile.html
    │       │   └── register.html
    │       ├── base.html
    │       ├── core
    │       │   ├── bucket_explorer.html
    │       │   ├── metadata_comparison.html
    │       │   ├── query_editor.html
    │       │   ├── settings.html
    │       │   └── table_metadata_viewer.html
    │       ├── errors
    │       │   └── error.html
    │       ├── home.html
    │       └── workspace
    │           ├── add_member.html
    │           ├── create_workspace.html
    │           ├── my_workspaces.html
    │           └── view_workspace.html
    ├── app.py
    ├── create_db.py
    ├── instance
    │   └── site.db
    ├── package-lock.json
    ├── package.json
    ├── requirements.txt
    ├── tailwind.config.js
    └── wsgi.py
```

---

## Notes

- **TailwindCSS:** The provided command runs Tailwind in watch mode, automatically updating the CSS whenever changes are made to `input.css`.
- **Server Startup:** Adjust the startup command based on your application server. The example uses either `flask run` or `python app.py` depending on your configuration.
