# api/views.py
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import requests
import google.generativeai as genai
import base64

# GitHub OAuth URLs
GITHUB_AUTH_URL = 'https://github.com/login/oauth/authorize'
GITHUB_TOKEN_URL = 'https://github.com/login/oauth/access_token'
GITHUB_API_URL = 'https://api.github.com'

# Configure the Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_github_api_headers(access_token):
    """Helper function to create headers for GitHub API requests."""
    return {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json',
    }

@api_view(['GET'])
def github_login(request):
    """Step 1: Redirects the user to GitHub for authentication."""
    scopes = 'repo,read:user'
    
    # This redirect_uri must point to your *frontend* where you will handle the callback.
    # Replace with your actual frontend URL.
    redirect_uri = 'http://localhost:3000/' 
    
    auth_url = (f'{GITHUB_AUTH_URL}?client_id={settings.GITHUB_CLIENT_ID}&'
                f'redirect_uri={redirect_uri}&scope={scopes}')
    return redirect(auth_url)

@api_view(['POST'])
def get_access_token(request):
    """
    Step 2: Frontend sends the 'code' here to exchange it for an access token.
    This is a new, dedicated endpoint for the secure token exchange.
    """
    code = request.data.get('code')
    if not code:
        return Response({'error': 'Authorization code not provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    # This redirect_uri must exactly match the one in github_login.
    redirect_uri = 'http://localhost:3000/' 
    
    data = {
        'client_id': settings.GITHUB_CLIENT_ID,
        'client_secret': settings.GITHUB_CLIENT_SECRET,
        'code': code,
        'redirect_uri': redirect_uri,
    }
    
    headers = {'Accept': 'application/json'}
    response = requests.post(GITHUB_TOKEN_URL, data=data, headers=headers)
    
    if response.status_code != 200:
        return Response({'error': 'Failed to get access token'}, status=status.HTTP_400_BAD_REQUEST)
        
    access_token = response.json().get('access_token')
    return Response({'access_token': access_token})

@api_view(['GET'])
def list_repos(request):
    """Lists the authenticated user's GitHub repositories."""
    access_token = request.headers.get('Authorization', '').split('Bearer ')[-1]
    if not access_token:
        return Response({'error': 'Authorization header missing'}, status=status.HTTP_401_UNAUTHORIZED)

    headers = get_github_api_headers(access_token)
    repos_url = f'{GITHUB_API_URL}/user/repos'
    
    try:
        response = requests.get(repos_url, headers=headers)
        response.raise_for_status()
        repos = response.json()
        repo_list = [{'name': repo['name'], 'owner': repo['owner']['login']} for repo in repos]
        return Response(repo_list)
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def list_files(request, owner, repo):
    """Fetches the top-level file tree for a given repository."""
    access_token = request.headers.get('Authorization', '').split('Bearer ')[-1]
    if not access_token:
        return Response({'error': 'Authorization header missing'}, status=status.HTTP_401_UNAUTHORIZED)
    
    headers = get_github_api_headers(access_token)
    contents_url = f'{GITHUB_API_URL}/repos/{owner}/{repo}/contents/'
    
    try:
        response = requests.get(contents_url, headers=headers)
        response.raise_for_status()
        files_and_dirs = response.json()
        file_tree = [{'name': item['name'], 'path': item['path'], 'type': item['type']} for item in files_and_dirs]
        return Response(file_tree)
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_file_content(request, owner, repo, file_path):
    """Fetches the raw content of a single file from a GitHub repository."""
    access_token = request.headers.get('Authorization', '').split('Bearer ')[-1]
    if not access_token:
        return Response({'error': 'Authorization header missing'}, status=status.HTTP_401_UNAUTHORIZED)
    
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3.raw', # Request raw content directly
    }
    
    file_url = f'{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{file_path}'
    
    try:
        response = requests.get(file_url, headers=headers)
        response.raise_for_status()
        return Response({'content': response.text})
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def generate_summaries(request):
    """Generates a list of test case summaries from code content using the Gemini API."""
    code_content = request.data.get('code_content')
    if not code_content:
        return Response({'error': 'No code content provided'}, status=status.HTTP_400_BAD_REQUEST)

    prompt = (
        f"Generate a bullet-point list of test case summaries for the following code. "
        f"Each summary should be a brief, single-sentence description of a test scenario. "
        f"Include functional, edge, and negative cases. Do not generate any extra text, only the list.\n\n"
        f"Code:\n{code_content}"
    )

    try:
        response = model.generate_content(prompt)
        summaries = [line.strip().lstrip('- ') for line in response.text.split('\n') if line.strip()]
        return Response({'summaries': summaries})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def generate_code(request):
    """Generates the full test case code for a selected summary using the Gemini API."""
    code_content = request.data.get('code_content')
    summary = request.data.get('summary')
    framework = request.data.get('framework', 'unittest')
    
    if not code_content or not summary:
        return Response({'error': 'Code content or summary missing'}, status=status.HTTP_400_BAD_REQUEST)
    
    prompt = (
        f"Generate the full, detailed test case code in Python using the '{framework}' framework "
        f"for the following code, based on the scenario: '{summary}'. "
        f"Return only the code block, with proper indentation and docstrings. "
        f"Do not include any extra text or explanations.\n\n"
        f"Code:\n{code_content}\n\n"
        f"Scenario: {summary}"
    )

    try:
        response = model.generate_content(prompt)
        test_code = response.text
        return Response({'test_code': test_code})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)