import os
import sys
import json
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pytube import Search, YouTube
from yt_dlp import YoutubeDL
from colorama import Fore, Style
import subprocess

# Configuración de logging
logging.basicConfig(
    filename="youtube_downloader.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Ruta fija para las descargas
download_path = "D:\\Musica"
offline_data_file = "offline_downloads.json"

# Función para limpiar la consola
def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

# Cargar datos offline
def load_offline_data():
    if os.path.exists(offline_data_file):
        try:
            with open(offline_data_file, 'r') as file:
                return json.load(file)                  
        except json.JSONDecodeError:
            logging.error("El archivo offline_downloads.json está corrupto. Reiniciando.")
            save_offline_data([])
            return []
    return []

# Guardar datos offline
def save_offline_data(data):
    with open(offline_data_file, 'w') as file:
        json.dump(data, file, indent=4)

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
            print(f"{Fore.GREEN}Descarga completada: {title}{Style.RESET_ALL}")

            # Opciones posteriores a la descarga
            post_download_options(title, format_type)

    except Exception as e:
        logging.error(f"Error al descargar {link}: {e}")
        print(f"{Fore.RED}Error al descargar {link}: {e}{Style.RESET_ALL}")

# Opciones posteriores a la descarga
def post_download_options(title, format_type):
    while True:
        try:
            print("\n¿Qué quieres hacer ahora?")
            print("1: Volver al menú")
            print("2: Abrir ruta de la canción/video")
            print("3: Reproducir canción o video")
            print("4: Salir")
            choice = int(input("Ingresa tu opción: "))

            file_path = os.path.join(download_path, f"{title}.{'mp3' if format_type == 'mp3' else 'mp4'}")

            if choice == 1:
                return
            elif choice == 2:
                if os.name == "nt":
                    subprocess.run(["explorer", "/select,", file_path])
                else:
                    subprocess.run(["xdg-open", os.path.dirname(file_path)])
            elif choice == 3:
                if os.name == "nt":
                    os.startfile(file_path)
                else:
                    subprocess.run(["xdg-open", file_path])
            elif choice == 4:
                sys.exit()
            else:
                print("Opción inválida. Intenta de nuevo.")
        except ValueError:
            print("Por favor, ingresa un número válido.")

# Función para descargar desde una lista de enlaces en un archivo de texto
def download_from_list(file_path, format_type):
    try:
        with open(file_path, 'r') as file:
            links = file.readlines()

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(download_video_or_audio, link.strip(), format_type) for link in links if link.strip()]
            for future in futures:
                future.result()

    except FileNotFoundError:
        print(f"{Fore.RED}Archivo no encontrado. Asegúrate de que la ruta sea correcta.{Style.RESET_ALL}")

# Función para buscar videos y listar los resultados
def search_and_download(query, format_type):
    try:
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
    except Exception as e:
        logging.error(f"Error en la búsqueda: {e}")
        print(f"{Fore.RED}Error en la búsqueda: {e}{Style.RESET_ALL}")

# Función para manejar descargas offline
def manage_offline_downloads():
    offline_data = load_offline_data()

    if not offline_data:
        print(f"{Fore.YELLOW}No hay descargas pendientes offline.{Style.RESET_ALL}")
        return

    print("Descargas pendientes:")
    for i, item in enumerate(offline_data, start=1):
        print(f"{i}. {item['title']} ({item['link']})")

    while True:
        try:
            choice = int(input("Ingresa el número del video que deseas descargar o 0 para salir: "))
            if choice == 0:
                return
            elif 1 <= choice <= len(offline_data):
                selected_item = offline_data.pop(choice - 1)
                save_offline_data(offline_data)
                try:
                    download_video_or_audio(selected_item['link'], selected_item['format'])
                    print(f"{Fore.GREEN}Descarga completada: {selected_item['title']}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}Error al intentar descargar {selected_item['title']}: {e}{Style.RESET_ALL}")
                    save_for_offline_download(selected_item['link'], selected_item['title'], selected_item['format'])
                break
            else:
                print("Selección inválida. Intenta de nuevo.")
        except ValueError:
            print("Por favor, ingresa un número válido.")

# Guardar búsqueda para descarga offline
def save_for_offline_download(link, title, format_type):
    offline_data = load_offline_data()
    offline_data.append({"link": link, "title": title, "format": format_type})
    save_offline_data(offline_data)
    print(f"{Fore.YELLOW}Guardado para descargar offline: {title}{Style.RESET_ALL}")

# Menú principal
def main():
    while True:
        clear_console()
        print(f"{Fore.CYAN}=== Descargador de YouTube ==={Style.RESET_ALL}")
        print("1. Descargar por enlace")
        print("2. Descargar desde lista de enlaces (archivo .txt)")
        print("3. Buscar y descargar")
        print("4. Gestionar descargas offline")
        print("5. Salir")

        try:
            choice = input("Elige una opción: ").strip()

            if choice == '1':
                link = input("Ingresa el enlace del video: ").strip()
                format_type = input_format_type()
                try:
                    download_video_or_audio(link, format_type)
                except Exception:
                    save_for_offline_download(link, "Enlace desconocido", format_type)

            elif choice == '2':
                file_path = input("Ingresa la ruta del archivo de texto: ").strip()
                format_type = input_format_type()
                download_from_list(file_path, format_type)

            elif choice == '3':
                query = input("Ingresa el nombre del video o canción: ").strip()
                format_type = input_format_type()
                search_and_download(query, format_type)

            elif choice == '4':
                manage_offline_downloads()

            elif choice == '5':
                print(f"{Fore.CYAN}Saliendo del programa.{Style.RESET_ALL}")
                sys.exit()

            else:
                print(f"{Fore.RED}Opción inválida. Por favor, selecciona una opción válida.{Style.RESET_ALL}")
        except Exception as e:
            logging.error(f"Ha ocurrido un error: {e}")
            print(f"{Fore.RED}Ha ocurrido un error: {e}.{Style.RESET_ALL}")

# Validar formato (mp3/mp4)
def input_format_type():
    while True:
        format_type = input("Formato (mp3/mp4): ").strip().lower()
        if format_type in ['mp3', 'mp4']:
            return format_type
        else:
            print(f"{Fore.RED}Formato inválido. Por favor, ingresa 'mp3' o 'mp4'.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
