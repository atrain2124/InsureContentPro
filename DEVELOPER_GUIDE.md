> # InsureContent Pro - Developer Guide

This guide provides instructions for setting up the development environment, running the application locally, and contributing to the InsureContent Pro project.

## 1. Project Structure

The project is a monorepo containing both the frontend and backend applications:

-   `insurance-content-frontend/`: The React frontend application.
-   `insurance-content-api/`: The Flask backend API.

## 2. Prerequisites

Before you begin, ensure you have the following installed:

-   Python 3.11+
-   Node.js 22.13.0+
-   pip
-   pnpm

## 3. Backend Setup

1.  **Navigate to the Backend Directory**:

    ```bash
    cd insurance-content-api
    ```

2.  **Create and Activate a Virtual Environment**:

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables**:

    Create a `.env` file in the `insurance-content-api/` directory and add the following variables:

    ```
    FLASK_ENV=development
    SECRET_KEY=your_secret_key
    OPENAI_API_KEY=your_openai_api_key
    STRIPE_SECRET_KEY=your_stripe_secret_key
    STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
    DATABASE_URL=sqlite:///src/database/app.db
    ```

5.  **Run the Database Migrations**:

    The database tables are created automatically when the application starts.

6.  **Run the Backend Server**:

    ```bash
    python src/main.py
    ```

    The backend server will be running at `http://localhost:5000`.

## 4. Frontend Setup

1.  **Navigate to the Frontend Directory**:

    ```bash
    cd insurance-content-frontend
    ```

2.  **Install Dependencies**:

    ```bash
    pnpm install
    ```

3.  **Run the Frontend Development Server**:

    ```bash
    pnpm run dev
    ```

    The frontend development server will be running at `http://localhost:5173`.

## 5. Running the Full-Stack Application

With both the backend and frontend servers running, you can access the application at `http://localhost:5173`. The frontend will automatically proxy API requests to the backend server.

## 6. Building for Production

1.  **Build the Frontend**:

    ```bash
    cd insurance-content-frontend
    pnpm run build
    ```

2.  **Copy the Build Files**:

    Copy the contents of the `insurance-content-frontend/dist/` directory to the `insurance-content-api/src/static/` directory.

3.  **Run the Production Server**:

    Set the `FLASK_ENV` environment variable to `production` and run the backend server. The Flask application will serve the built React frontend.

## 7. Contributing

We welcome contributions to the InsureContent Pro project! Please follow these steps to contribute:

1.  **Fork the Repository**: Create a fork of the main repository.
2.  **Create a Branch**: Create a new branch for your feature or bug fix.
3.  **Make Your Changes**: Implement your changes, following the existing code style and conventions.
4.  **Test Your Changes**: Ensure that your changes do not break any existing functionality.
5.  **Submit a Pull Request**: Submit a pull request with a clear description of your changes.

## 8. Code Style and Conventions

-   **Python**: Follow the PEP 8 style guide.
-   **JavaScript/React**: Follow the Airbnb JavaScript Style Guide.
-   **Commit Messages**: Use conventional commit messages.

Thank you for contributing to InsureContent Pro!
