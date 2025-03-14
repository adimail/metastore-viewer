# Metastore Viewer for Lakehouse Tables on Object Stores

_COEP Inspiron hackathon_

## Setup Instructions

1. **Clone the repository and navigate to the project folder:**

   ```sh
   git clone https://github.com/adimail/metastore-viewer.git
   cd metastore-viewer
   ```

2. **Run the setup script:**

   ```sh
   ./setup.sh
   ```

3. **Run the application:**
   ```sh
   ./run.sh
   ```

After running `./run.sh`, open another terminal and run the following command to start TailwindCSS in watch mode:

```sh
npx tailwindcss -i ./app/static/css/input.css -o ./app/static/css/tailwind.css --watch
```

---

## Pre-commit Hook Setup

To maintain code quality and enforce consistent formatting, this project uses **pre-commit hooks**. These hooks automatically format Python, Jinja, JavaScript, and TypeScript files and check for common issues.

### Install and Activate Pre-commit:

1. **Install the pre-commit hooks (Do it only once)**:

   ```sh
   pre-commit install
   ```

2. **Run pre-commit manually on all files (first-time setup)**:
   ```sh
   pre-commit run --all-files
   ```

### What Does Pre-commit Do?

- Formats **Python** files using `black`
- Formats **Jinja & HTML** files using `djhtml`
- Formats **JavaScript & TypeScript** files using `prettier`
- Runs **ESLint** on JS/TS files
- Cleans up **trailing whitespace & newlines**

---

## Notes

- **TailwindCSS:** The provided command runs Tailwind in watch mode, automatically updating the CSS whenever changes are made to `input.css`.
- **Server Startup:** Adjust the startup command based on your application server. The example uses either `flask run` or `python app.py` depending on your configuration.
- **Pre-commit Hooks:** Run `pre-commit run --all-files` whenever new hooks are added or if you encounter formatting issues.
