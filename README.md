# AI Test Case Generator

This project is a web application that uses a backend API to interact with GitHub and Google's Gemini AI to automatically generate test cases for a user's code. It's designed with a clean separation of concerns, allowing for a flexible and scalable architecture.

The backend is built with Django Rest Framework, providing a powerful and secure API. The frontend is a separate application that consumes this API, offering a modern and responsive user interface.

## 🚀 Key Features

  - **GitHub Integration**: Authenticate with your GitHub account to access your repositories.
  - **File Selection**: Browse your repository files and select code snippets for test case generation.
  - **AI-Powered Summaries**: Generate a list of potential test case scenarios (functional, edge, negative) from your code using the Gemini API.
  - **Detailed Code Generation**: Choose a summary to generate a full, detailed test case in a specified testing framework (e.g., `unittest`).
  - **Robust API**: A secure and well-documented API for seamless frontend-backend communication.

## 🛠️ Technology Stack

**Backend**:

  - **Framework**: Django, Django Rest Framework (DRF)
  - **Language**: Python
  - **Authentication**: GitHub OAuth2
  - **AI**: Google Gemini API
  - **Dependencies**: `requests`, `python-decouple`, `django-cors-headers`, `google-generativeai`

**Frontend**:

  - **Framework**: Vanilla HTML, CSS, and JavaScript
  - **UI/UX**: Custom CSS with FontAwesome for a modern, animated interface
  - **Syntax Highlighting**: Prism.js

## ⚙️ Installation and Setup

### Phase 1: Backend Setup

1.  **Clone the Repository**

    ```bash
    git clone https://github.com/your-username/ai_test_case_generator.git
    cd ai_test_case_generator
    ```

2.  **Create and Activate a Virtual Environment**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Configure Environment Variables**
    Create a `.env` file in the `ai_test_case_generator` project root and add your API keys.

      - **GitHub OAuth App**: Go to your GitHub profile settings -\> Developer settings -\> OAuth Apps. Create a new app and get the `Client ID` and `Client Secret`.
      - **Redirect URI**: The "Authorization callback URL" in your GitHub app settings must be set to `http://localhost:3000/`. This is crucial for the OAuth flow.
      - **Gemini API Key**: Get your API key from [Google AI Studio](https://aistudio.google.com/).

    Your `.env` file should look like this:

    ```
    SECRET_KEY='your-django-secret-key'
    DEBUG=True

    GITHUB_CLIENT_ID='your_github_client_id'
    GITHUB_CLIENT_SECRET='your_github_client_secret'
    GEMINI_API_KEY='your_gemini_api_key'
    ```

4.  **Run Migrations and Create a Superuser**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser
    ```

5.  **Run the Backend Server**

    ```bash
    python manage.py runserver
    ```

    Your backend API will now be running on `http://127.0.0.1:8000`.

### Phase 2: Frontend Setup

The frontend is a single `index.html` file with embedded JavaScript. You need to serve this file using a local web server.

1.  **Navigate to the Frontend Directory**

    ```bash
    cd path/to/your/frontend/directory
    ```

    (This assumes the frontend is in a separate directory from the backend).

2.  **Serve the Frontend**
    The simplest way to run a local server is by using `live-server` or a similar tool.

    ```bash
    npm install -g live-server
    live-server . --port=3000
    ```

    This will serve your `index.html` on `http://localhost:3000`.

## 🗺️ API Endpoints

The backend exposes the following REST API endpoints:

| Endpoint                                       | Method | Description                                                                        |
| ---------------------------------------------- | ------ | ---------------------------------------------------------------------------------- |
| `/api/github/login/`                           | `GET`  | Initiates the GitHub OAuth flow by redirecting the user to GitHub.                 |
| `/api/github/token/`                           | `POST` | Exchanges a GitHub authorization code for a valid access token.                      |
| `/api/repos/`                                  | `GET`  | Lists the authenticated user's GitHub repositories.                                |
| `/api/files/{owner}/{repo}/`                   | `GET`  | Fetches the file tree for a specified repository.                                  |
| `/api/files/{owner}/{repo}/{file_path}/`       | `GET`  | Retrieves the raw content of a specific file from a repository.                    |
| `/api/generate/summaries/`                     | `POST` | Sends code to the AI to generate a list of test case summaries.                    |
| `/api/generate/code/`                          | `POST` | Generates a full test case code block based on a provided code snippet and summary. |

## 🚀 Usage Workflow

1.  Open your frontend in a browser (`http://localhost:3000`).
2.  Click **"Connect GitHub Account"**. You will be redirected to GitHub to authorize the application.
3.  After authorization, you will be redirected back to your frontend with a temporary `code`. The frontend's JavaScript will use this code to get a persistent access token from your backend.
4.  The application will display a list of your GitHub repositories. Click on a repository to view its file tree.
5.  Select one or more files by checking the boxes next to them.
6.  Click **"Generate Test Case Summaries"**. The API will send the code to Gemini, and the returned summaries will be displayed.
7.  Click on a summary to generate the full, detailed test case code, which will be displayed in a syntax-highlighted block.

## 🐛 Troubleshooting

  - **"Invalid Redirect URI"**: Ensure the "Authorization callback URL" in your GitHub OAuth app settings is an exact match for the `redirect_uri` in your backend's `api/views.py`.

  - **"localhost refused to connect"**: Make sure your frontend web server is running on the correct port (e.g., `http://localhost:3000`). The backend server is on port 8000.

  - **"File not found"**: This occurs when your frontend server doesn't have a configured route handler for `/`. Change the `redirect_uri` in your backend and your GitHub app settings to `http://localhost:3000/`.

  - **Files not selecting**: The issue is likely in the frontend JavaScript where the DOM is being modified. Ensure you are using DOM manipulation methods like `appendChild` correctly and not overwriting elements with `innerHTML`.

  - **No repositories shown after re-connecting**: When you manually revoke a GitHub token, your frontend's `localStorage` still holds the old, invalid token. Clear your browser's local storage to force a new authentication flow.


## 🙏 Acknowledgments

  - The [Django](https://www.djangoproject.com/) and [Django Rest Framework](https://www.django-rest-framework.org/) teams for building an amazing web framework.
  - [Google Gemini API](https://ai.google.dev/) for providing powerful AI capabilities.
  - [Prism.js](https://prismjs.com/) for elegant syntax highlighting.
  - [FontAwesome](https://fontawesome.com/) for the icons.
