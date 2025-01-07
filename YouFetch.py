import os
from pytube import Search, YouTube
from yt_dlp import YoutubeDL
import subprocess
import sys

os.system("cls")

download_path = "D:\\Musica"  # Ruta fija para las descargas

# Función para descargar un video/audio en formato MP3 o MP4
def download_video_or_audio(link, format_type):
    ydl_opts = {
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'quiet': True,
    }

    if format_type == 'mp3':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        })
    elif format_type == 'mp4':
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
        })

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            title = info_dict.get('title', 'Unknown Title')
            print(f"Descarga completada: LINK: {link} / NOMBRE: {title}")

            # Opciones posteriores a la descarga
            while True:
                try:
                    print("\n¿Qué quieres hacer ahora?")
                    print("1: Volver al menú")
                    print("2: Abrir ruta de la canción/video")
                    print("3: Reproducir canción o video")
                    print("4: Salir")
                    choice = int(input("Ingresa tu opción: "))

                    if choice == 1:
                        return
                    elif choice == 2:
                        subprocess.run(["explorer", "/select,", os.path.join(download_path, f"{title}.mp3" if format_type == 'mp3' else f"{title}.mp4")])
                    elif choice == 3:
                        file_path = os.path.join(download_path, f"{title}.mp3" if format_type == 'mp3' else f"{title}.mp4")
                        os.startfile(file_path)
                    elif choice == 4:
                        sys.exit()
                    else:
                        print("Opción inválida. Intenta de nuevo.")
                except ValueError:
                    print("Por favor, ingresa un número válido.")
    except Exception as e:
        print(f"Error al descargar {link}: {e}")

# Función para descargar desde una lista de enlaces en un archivo de texto
def download_from_list(file_path, format_type):
    try:
        with open(file_path, 'r') as file:
            links = file.readlines()
        for link in links:
            link = link.strip()
            if link:
                download_video_or_audio(link, format_type)
    except FileNotFoundError:
        print("Archivo no encontrado. Asegúrate de que la ruta sea correcta.")

# Función para buscar videos y listar los resultados
def search_and_download(query, format_type):
    search = Search(query)
    results = search.results[:50]  # Mostrar los primeros 50 resultados

    print("Resultados de la búsqueda:")
    for i, result in enumerate(results, start=1):
        print(f"{i}. {result.title} ({result.watch_url})")

    while True:
        try:
            choice = int(input("Ingresa el número del video que deseas descargar: "))
            if 1 <= choice <= len(results):
                selected_video = results[choice - 1]
                download_video_or_audio(selected_video.watch_url, format_type)
                break
            else:
                print("Selección inválida. Intenta de nuevo.")
        except ValueError:
            print("Por favor, ingresa un número válido.")

# Menú principal
def main():
    while True:
        os.system("cls")
        print("=== Descargador de YouTube ===")
        print("1. Descargar por enlace")
        print("2. Descargar desde lista de enlaces (archivo .txt)")
        print("3. Buscar y descargar")
        print("4. Salir")

        try:
            choice = input("Elige una opción: ")

            if choice == '1':
                link = input("Ingresa el enlace del video: ").strip()
                while True:
                    format_type = input("Formato (mp3/mp4): ").strip().lower()
                    if format_type in ['mp3', 'mp4']:
                        download_video_or_audio(link, format_type)
                        break
                    else:
                        print("Formato inválido. Por favor, ingresa 'mp3' o 'mp4'.")

            elif choice == '2':
                file_path = input("Ingresa la ruta del archivo de texto: ").strip()
                while True:
                    format_type = input("Formato (mp3/mp4): ").strip().lower()
                    if format_type in ['mp3', 'mp4']:
                        download_from_list(file_path, format_type)
                        break
                    else:
                        print("Formato inválido. Por favor, ingresa 'mp3' o 'mp4'.")

            elif choice == '3':
                query = input("Ingresa el nombre del video o canción: ").strip()
                author = input("¿Quién es el autor? (Dejar vacío si no aplica): ").strip()
                search_query = f"{query} {author}" if author else query
                while True:
                    format_type = input("Formato (mp3/mp4): ").strip().lower()
                    if format_type in ['mp3', 'mp4']:
                        search_and_download(search_query, format_type)
                        break
                    else:
                        print("Formato inválido. Por favor, ingresa 'mp3' o 'mp4'.")

            elif choice == '4':
                print("Saliendo del programa.")
                sys.exit()

            else:
                print("Opción inválida. Por favor, selecciona una opción válida.")
        except Exception as e:
            print(f"Ha ocurrido un error: {e}. Reiniciando el menú principal.")

if __name__ == "__main__":
    main()
