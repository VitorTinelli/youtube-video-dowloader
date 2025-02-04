import json
import yt_dlp
from menu import get_folder_path

def baixarVideo(url, progress_callback):
    with open('configurations/configurations.json', 'r') as config_file:
        config = json.load(config_file)
        folder_path = get_folder_path()
        output_template = config['output'].replace("{folder_path}", folder_path)
        print(f"Baixando vídeo de {url} para {folder_path} com qualidade {config['quality']} e output {output_template}")

    ydl_opts = {
        "format": config['quality'],
        "outtmpl": output_template,
        "progress_hooks": [progress_callback],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])