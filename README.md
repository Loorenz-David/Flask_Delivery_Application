# Flask_Delivery_Application

Backend-for-the-delivery application currently focuses on authentication and item catalogue management. It is built with Flask and SQLAlchemy, targets PostgreSQL in production, and falls back to an in-memory SQLite database for the automated test-suite.

## Tech Stack
- Python 3.10+
- Flask & Flask SQLAlchemy
- Flask-JWT-Extended for access/refresh tokens
- Marshmallow for payload validation
- Pytest for testing
- python-dotenv for local configuration

## Project Layout
```
Back_end/
├── Delivery_app_BK/
│   ├── __init__.py              # Flask application factory, DB/JWT wiring, blueprint registration
│   ├── config/                  # Environment specific configuration classes
│   ├── models/                  # SQLAlchemy tables, mixins, and managers
│   ├── routers/                 # Flask blueprints (auth + item catalogue)
│   └── services/                # Business logic helpers used by the routers
├── run.py                       # Local entry point (python run.py)
├── tests/                       # Pytest suite (uses an in-memory SQLite database)
└── pytest.ini                   # Pytest discovery settings
```

## Getting Started
1. **Create a Python virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
2. **Install dependencies**  
   Until a `requirements.txt` is generated, install the working set manually:
   ```bash
   pip install Flask Flask-SQLAlchemy Flask-JWT-Extended marshmallow python-dotenv pytest
   ```
3. **Environment variables**  
   Copy `.env.example` to `.env` and adjust as needed:
   ```dotenv
   FLASK_ENV=development
   SECRET_KEY=devkey
   JWT_SECRET_KEY=change-me
   DATABASE_URL=postgresql://postgres:password@localhost:5432/DeliveryApp
   FRONTEND_ORIGIN=http://localhost:5173
   ```
   `FRONTEND_ORIGIN` is used by Flask-CORS so the Vite dev server can hit this API. Set it to the exact origin you'll load the front-end from.

4. **Database**  
   `create_app("development")` will transparently call `db.create_all()` the first time it boots, so an empty PostgreSQL database matching `DATABASE_URL` is enough for local work. Alembic migrations have not been introduced yet.

5. **Run the application**
   ```bash
   pip install -r requirements.txt
   python run.py
   ```
   Flask will start on `http://127.0.0.1:5000`. The development factory registers all blueprints and wires JWT handlers.

## Working with the Front-end

The React client (in `../Front_end/delivery-app-front`) uses `VITE_API_BASE_URL` to talk to this server and expects CORS to allow `http://localhost:5173`. As long as you keep `FRONTEND_ORIGIN` synced with the URL your Vite dev server runs on, browser requests such as `POST http://127.0.0.1:5000/route/query_route` will succeed after signing in.

## Auth Workflow
There is no user-registration route yet. Seed at least one record in the `User` table (manually or via a database client) to exercise the token endpoints.

- `POST /api_v2/auths/login`  
  ```json
  {
    "email": "driver@example.com",
    "password": "secretpass",
    "time_zone": "Europe/Stockholm"
  }
  ```  
  Returns `access_token`, `refresh_token`, and minimal user data when the credentials match an existing row. Tokens include the `time_zone` claim.

- `POST /api_v2/auths/refresh_token`  
  Requires a valid refresh token in the `Authorization: Bearer` header and returns a new access token.

Custom JWT error handlers in `routers/auth_routers/utils/jwt_handler.py` standardise JSON responses for common token failures.

## Item Catalogue Endpoints
All routes live under `/item` and share the same creation pipeline:
1. The route receives JSON payloads.
2. `ObjectCreator.create` validates and normalises the payload.
3. `create_general_object` instantiates SQLAlchemy models and resolves relationships.
4. The response wrapper returns consistent `{"status", "message", "error", "data"}` envelopes.

### Create Category
- `POST /item/create_item_category`
  ```json
  { "name": "Seating" }
  ```

### Create Type
- `POST /item/create_item_type`
  ```json
  {
    "name": "Dining Chair",
    "properties": [1, 2]
  }
  ```
  `properties` is optional and links to `ItemProperty` records by ID.

### Create Property
- `POST /item/create_item_property`
  ```json
  {
    "name": "Set Of",
    "value": "4",
    "field_type": "number-keyboard",
    "options": {"min": 1, "max": 20}
  }
  ```

### Create Item
- `POST /item/create_item`
  ```json
  {
    "article_number": "030303",
    "item_type_id": 1,
    "item_category_id": 1,
    "properties": [1, 2],
    "weight": 12,
    "state": "in-stock",
    "position": "Warehouse A"
  }
  ```
  Relationship IDs are resolved automatically; simple column values pass through `ValueValidator` before assignment.

### Query Items
- `POST /item/query_item`  
  Supply `requested_data` (columns/relationships to serialise) and `query_filters`. Example:
  ```json
  {
    "requested_data": ["id", "article_number", {"properties": ["name", "value"]}],
    "query_filters": {
      "article_number": {"operation": "==", "value": "030303"},
      "state": {"operation": "ilike", "value": "%stock%"}
    }
  }
  ```
  Successful responses compress the payload to base64 GZip when `response.compress_payload()` is triggered.

## Testing
Pytest is configured via `tests/conftest.py` to initialise the app with the `"testing"` configuration and an in-memory SQLite database (`sqlite:///:memory:`). Run the suite with:
```bash
pytest
```
The current tests cover the item creation routes (`tests/test_item_routers/test_routes_create.py`) by asserting happy-path responses.

> **Note:** In this environment `pytest` may not be preinstalled—install it in your virtualenv before running the suite.

## Troubleshooting & Next Steps
- Ensure the PostgreSQL database specified by `DATABASE_URL` exists before starting the server.
- Because user creation is manual right now, invalid login attempts will fail with the generic `"something went wrong"` error. Seed data up-front for local testing.
- Marshmallow schemas (`models/schemas/items_schema.py`) predate the latest relationship changes and will likely be refined as the API evolves.
- Consider adding a `requirements.txt`/`poetry.lock` and database migrations as the project matures.

With this setup you can spin up the API, seed catalogue data via the provided endpoints, query it, and verify behaviour with the pytest suite. 
