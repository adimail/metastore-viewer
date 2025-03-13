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

## Notes

- **TailwindCSS:** The provided command runs Tailwind in watch mode, automatically updating the CSS whenever changes are made to `input.css`.
- **Server Startup:** Adjust the startup command based on your application server. The example uses either `flask run` or `python app.py` depending on your configuration.
