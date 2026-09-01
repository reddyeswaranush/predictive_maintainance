# FactoryOps AI CRUD Flow

## Purpose

This document explains how CRUD operations work in the FactoryOps AI project and how data flows through the system. It is written as a project walkthrough that can be shared as supporting material for internship or experience documentation.

## Project Overview

The project is split into three main parts:

- `backend/` contains the FastAPI application, API routers, SQLAlchemy database models, schemas, and service-layer logic.
- `frontend/` contains the Streamlit dashboard used to view operational data and submit records.
- `ml/` contains model inference and prediction-related logic used by the prediction endpoints.

At a high level, the request flow is:

`Streamlit UI -> FastAPI router -> service layer -> SQLAlchemy model -> SQLite database`

The response then returns through the same path back to the frontend as JSON.

## Application Entry Point

The backend starts from `backend/api/main.py`.

Its responsibilities are:

- import all database models
- create tables with `Base.metadata.create_all(bind=engine)`
- create the FastAPI app
- register all routers

Registered resource routers:

- `/machines`
- `/sensors`
- `/telemetry`
- `/predictions`
- `/maintenance`
- `/notifications`
- `/inventory`
- `/incidents`

## Database Layer

The active database configuration used by the running backend is in `backend/database/connection.py`.

It defines:

- the SQLite database URL: `sqlite:///factoryops.db`
- the SQLAlchemy engine
- the session factory `SessionLocal`
- the declarative base `Base`
- the `get_db()` dependency used by FastAPI

`get_db()` creates one database session per request and closes it automatically after the request is completed.

## CRUD Architecture Pattern

The project follows a consistent layered CRUD design:

### 1. Model Layer

The model defines the table structure in the database.

Example:

- `backend/models/machine.py`
- `backend/models/telemetry.py`
- `backend/models/prediction.py`

These SQLAlchemy classes define columns such as IDs, names, status fields, telemetry values, and foreign keys like `machine_id`.

### 2. Schema Layer

The schema defines request and response shapes using Pydantic.

Typical schema types:

- `Create` schema for POST requests
- `Update` schema for PUT requests
- `Response` schema for API output

Example:

- `MachineCreate`
- `MachineUpdate`
- `MachineResponse`

This layer validates incoming data and controls the JSON shape returned to the client.

### 3. Router Layer

The router exposes the HTTP endpoints.

Typical endpoints per resource:

- `GET /resource/`
- `GET /resource/{id}`
- `POST /resource/`
- `PUT /resource/{id}`
- `DELETE /resource/{id}`

The router does three main things:

- accepts the request
- validates input through schemas
- injects the database session using `Depends(get_db)`

After that, it calls the corresponding service function.

### 4. Service Layer

The service layer contains the actual database logic.

Typical operations include:

- query all rows
- query a row by ID
- create a new row
- update an existing row
- delete a row

This layer directly talks to the SQLAlchemy model using the database session.

## Standard CRUD Flow

The cleanest example is the `machines` resource.

### Create Flow

Example endpoint:

- `POST /machines/`

Flow:

1. The frontend submits machine data such as `machine_name`, `department`, `location`, and `status`.
2. The router in `backend/api/routers/machine.py` receives the request.
3. FastAPI validates the payload with `MachineCreate`.
4. The router calls `create_machine(db, machine)` in `backend/services/machine_service.py`.
5. The service creates a `Machine(...)` object.
6. It saves the object using:
   - `db.add(...)`
   - `db.commit()`
   - `db.refresh(...)`
7. The saved row is returned as a response.

### Read Flow

Two read patterns exist:

- `GET /machines/` returns all machine records
- `GET /machines/{machine_id}` returns one machine record

Flow:

1. The router receives the GET request.
2. It calls the relevant service function.
3. The service runs a SQLAlchemy query such as:
   - `db.query(Machine).all()`
   - `db.query(Machine).filter(...).first()`
4. The result is returned as JSON.
5. If no record exists for a single-ID request, the router raises `HTTPException(status_code=404)`.

### Update Flow

Example endpoint:

- `PUT /machines/{machine_id}`

Flow:

1. The frontend sends updated values.
2. The router validates them with `MachineUpdate`.
3. The service first fetches the existing row.
4. If the row does not exist, the router returns `404`.
5. If it exists, the service updates the fields.
6. It commits the transaction and refreshes the object.
7. The updated row is returned.

### Delete Flow

Example endpoint:

- `DELETE /machines/{machine_id}`

Flow:

1. The router receives the delete request.
2. The service searches for the row by ID.
3. If not found, the router returns `404`.
4. If found, the service runs `db.delete(...)` and `db.commit()`.
5. The API returns a success message.

## Resources That Follow This CRUD Pattern

The same CRUD structure is used for:

- `machines`
- `sensors`
- `telemetry`
- `maintenance`
- `inventory`
- `incidents`
- `notifications`
- `predictions`

Each of these resources has:

- a router file under `backend/api/routers/`
- a service file under `backend/services/`
- a model file under `backend/models/`
- a schema file under `backend/schemas/`

## Frontend Flow

The Streamlit frontend is mainly defined in `frontend/app.py` and supporting page modules under `frontend/`.

Its role is:

- fetch data from the backend
- display it in dashboard views
- submit new operational records
- trigger limited update actions

### Reading Data in the Frontend

The frontend reads collection data using `get_records(resource)`.

This function:

- builds the API URL
- sends a `GET` request using `requests.get(...)`
- parses the JSON response
- caches the results briefly for dashboard performance

The app loads collections such as:

- machines
- telemetry
- predictions
- maintenance
- incidents
- inventory
- notifications
- sensors

These datasets are converted into pandas DataFrames and then merged for dashboards and visualizations.

### Writing Data in the Frontend

The frontend sends state-changing requests through `send_record(...)`.

This function supports:

- `POST`
- `PUT`
- `DELETE`

It sends requests to the backend using `requests.request(...)` and clears cached data after successful writes so the UI refreshes with current information.

## Data Management Page

The main create forms live in `frontend/data_management.py`.

This page allows users to submit new records directly to the backend for:

- machines
- telemetry
- maintenance
- incidents
- inventory
- notifications
- sensors

Examples:

- adding a machine sends `POST /machines/`
- recording telemetry sends `POST /telemetry/`
- creating a maintenance job sends `POST /maintenance/`
- logging an incident sends `POST /incidents/`

This page is effectively the frontend’s main “Create” interface.

## Where Update Happens in the UI

The only clear update flow exposed in the frontend is in `frontend/fleet_explorer.py`.

That page includes an “Update a machine status” form.

Flow:

1. The user selects a machine from the fleet view.
2. The user changes the status value.
3. The frontend sends `PUT /machines/{machine_id}`.
4. The backend router receives the request.
5. The machine service updates the machine row in the database.
6. The frontend refreshes and displays the new status.

So the backend supports update for many resources, but the current frontend visibly uses update mainly for machine status.

## Where Delete Happens

Delete endpoints exist in the backend for all major resources, but the current Streamlit frontend does not expose obvious delete buttons for normal users.

That means:

- delete is supported at the API level
- delete is not a major visible workflow in the frontend

## Special Prediction Flow

`predictions` is the one resource that is not only plain CRUD.

In addition to standard create, read, update, and delete endpoints, it includes prediction-generation endpoints:

- `POST /predictions/generate/{machine_id}`
- `POST /predictions/generate-metro`

### Prediction Generation by Machine ID

Flow:

1. The request comes to `POST /predictions/generate/{machine_id}`.
2. The router queries the latest telemetry record for that machine.
3. It extracts values such as:
   - temperature
   - pressure
   - vibration
   - voltage
   - current
   - power
   - rpm
   - humidity
   - oil level
4. These values are passed to the ML inference function in `ml/predict.py`.
5. The model returns prediction values such as:
   - `failure_probability`
   - `health_score`
   - `predicted_days`
6. The router builds a `PredictionCreate` object.
7. The standard prediction service saves it to the database.
8. The saved prediction row is returned to the client.

### Prediction Generation for MetroPT Data

Flow:

1. The request comes to `POST /predictions/generate-metro`.
2. The payload is validated by `MetroTelemetryInput`.
3. The values are passed to the Metro-specific prediction function.
4. The returned prediction result is saved through the normal prediction create service.
5. The result becomes a stored prediction record in the database.

This means prediction generation combines:

- telemetry input
- ML inference
- database persistence

So it is not just CRUD. It is CRUD plus model-based business logic.

## How Data Is Used Across the Dashboard

The frontend does more than simply display raw rows.

For example:

- machine records provide asset identity and status
- telemetry records provide the latest sensor readings
- prediction records provide failure risk and health estimates
- incident records show operational issues
- maintenance records show planned or ongoing repair work
- inventory records show parts availability

These datasets are merged in the frontend to build summary dashboards, fleet risk views, and operational decision screens.

An important example is the machine view builder in `frontend/app.py`, which combines:

- machine master data
- latest telemetry per machine
- latest prediction per machine

This is how the dashboard computes derived states such as:

- normal
- warning
- critical

## Important Implementation Notes

### 1. Backend Authentication Is Not Implemented

The login screen in the frontend is only a Streamlit session-based demo gate.

This means:

- the dashboard requires frontend login
- the backend API itself is not protected by real authentication

### 2. SQLite Is the Active Database

The live backend uses SQLite through `factoryops.db`.

This makes the project easy to run locally and appropriate for a demo or internship project.

### 3. Foreign Keys Exist Without Rich ORM Relationships

Several tables use `machine_id` as a foreign key, but the project mostly works with direct queries rather than advanced ORM relationships.

### 4. Machine Update Behavior Is Slightly Different

Most update services use a partial update style with `exclude_unset=True`, which updates only the fields actually sent by the client.

`machine_service.update_machine()` is slightly different because it directly assigns values from the update object to all machine fields. In practice, this works because the frontend sends the full machine payload when updating machine status.

## Summary

The project demonstrates a complete full-stack CRUD architecture for predictive maintenance operations:

- FastAPI provides the API layer
- SQLAlchemy handles database access
- Pydantic validates request and response data
- Streamlit provides the operational UI
- the ML layer extends CRUD with prediction generation

From an engineering perspective, the project includes:

- resource-based API design
- layered backend architecture
- data-entry workflows
- dashboard data aggregation
- predictive inference integrated into operational records

This makes it a solid internship-scale implementation of a predictive maintenance platform with both standard CRUD operations and ML-assisted workflows.
