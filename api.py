import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Если измените области доступа, удалите файл token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


def authenticate():
    """Аутентифицирует пользователя и возвращает учетные данные."""
    creds = None
    # Файл token.pickle хранит токен доступа пользователя и обновляется автоматически.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # Если нет действительных учетных данных, начнем процесс аутентификации.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Сохраним учетные данные для следующего запуска.
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def list_files_in_folder(folder_id):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    """Возвращает список ссылок на все фото в указанной папке."""
    query = f"'{folder_id}' in parents and mimeType contains 'image/'"
    results = service.files().list(q=query, pageSize=1000, fields="files(id, name)").execute()
    items = results.get('files', [])

    file_links = []
    if not items:
        print('No files found.')
    else:
        for item in items:
            file_id = item['id']
            file_link = f"https://drive.google.com/uc?id={file_id}"
            file_links.append(file_link)

    return file_links


def extract_folder_id(url):
    parts = url.split('/')
    for i in range(len(parts)):
        if parts[i] == 'folders':
            folder_id = parts[i + 1]
            return folder_id.split('?')[0]

    return None


def join_strings(strings_list):
    return ' '.join(strings_list)


def all_in(link):
    return join_strings(list_files_in_folder(extract_folder_id(link)))


def main():
    folder_id = 'https://drive.google.com/drive/folders/1yCLagir9aTqpDL9BWA3omhZzGYyLG1XQ?usp=drive_link'

    file_links = all_in(folder_id)
    print(file_links)


if __name__ == '__main__':
    main()
