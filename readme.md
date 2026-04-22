🎵 Music Bot Discord - Advanced Player

Bot de música para Discord con sistema de favoritos, playlists persistentes en MySQL, reproducción desde YouTube y panel interactivo en tiempo real.

✨ Características
🎶 Reproducción de Música
Búsqueda automática en YouTube
Streaming de audio con FFmpeg
Control de reproducción en tiempo real
Cambio dinámico de canciones

❤️ Sistema de Favoritos
Botón interactivo con ❤️ dentro del reproductor
Guarda canciones en base de datos
Lista de favoritos con !favoritos
Sin duplicados gracias a claves únicas

📁 Sistema de Playlists
Crear playlists personales
Añadir canciones desde la base de datos
Eliminación segura con relaciones (FK)
Reproducción completa de playlists

📊 Sistema Inteligente por Servidor
Historial de canciones (!historial)
Top canciones (!top)
Control de volumen por servidor
Datos aislados por guild

🎨 Interfaz Visual
Embed “Now Playing”
Barra de progreso animada
Miniatura del video
Cambio de color si la canción es favorita

🚀 Instalación
🔧 Requisitos
Python 3.10+
FFmpeg instalado
MySQL o MariaDB

📥 Clonar repositorio
git clone https://github.com/tu-usuario/music-bot.git
cd music-bot

📦 Instalar dependencias
pip install -r requirements.txt

⚙️ Configurar variables de entorno

Copia el archivo de ejemplo y rellena tus credenciales:

cp .env.example .env

Windows:

copy .env.example .env
🗂️ Archivo .env
DISCORD_TOKEN=tu_token
CHANNEL_ID=id_canal_inicio

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=musicbot

📖 Comandos
🎶 Música
Comando	Descripción
!play <canción>	Reproduce música
!stop	Pausa
!resume	Reanuda
!skip	Cambia canción
!join	Conecta al canal
!volumen <0-2>	Ajusta volumen

❤️ Favoritos
Comando	Descripción
!favoritos	Muestra tus canciones favoritas

📁 Playlists
Comando	Descripción
!crear_playlist	Crear playlist
!add_playlist <canción>	Añadir canción
!ver_playlist	Ver playlist
!mis_playlists	Ver todas
!borrar_playlist	Eliminar
!play_playlist	Reproducir

📊 Estadísticas
Comando	Descripción
!historial	Últimas canciones
!top	Más reproducidas

⚙️ Otros
Comando	Descripción
!ping	Test
!menu	Ver comandos

🛠️ Tecnologías
Python
discord.py
yt-dlp
FFmpeg
MySQL
dotenv

📊 Base de Datos

El sistema usa MySQL con relaciones bien estructuradas:

users → usuarios
songs → canciones
favoritos → favoritos
playlists → playlists
playlist_songs → relación playlist-canción

✔ Claves únicas para evitar duplicados
✔ Foreign Keys con borrado en cascada

⚙️ Arquitectura
🔄 Flujo de reproducción
Usuario ejecuta !play
Se busca en YouTube con yt-dlp
Se obtiene stream de audio
Se guarda en base de datos
Se reproduce con FFmpeg
Se muestra embed con botón ❤️
Se actualiza progreso en tiempo real

🔥 Características destacadas
❤️ Botón interactivo
Añade/Quita favoritos sin comandos
Persistente en base de datos
Cambia color del reproductor

📊 Progreso en tiempo real

Barra animada tipo:

▬▬▬🔘▬▬▬▬▬▬▬▬ 1:20 / 3:45

🧠 Sistema inteligente
Historial automático
Contador de reproducciones
Volumen independiente por servidor

🤝 Contribuciones
Fork
Crear rama (feature/...)
Commit
Push
Pull Request

📝 Licencia

MIT

📌 Notas
Requiere FFmpeg en PATH
Compatible con múltiples servidores
Base de datos optimizada para evitar duplicados

⚠️ Seguridad

Nunca compartas tu archivo .env.
El token de Discord da acceso total a tu bot.

Si alguna vez lo subiste por error, revoca el token inmediatamente en el Developer Portal.

Nunca compartas tu archivo `.env`.
El token de Discord da acceso total a tu bot.

Si alguna vez lo subiste por error, revoca el token inmediatamente en el Developer Portal.

🎉 Autor

Desarrollado con ❤️ para la comunidad de Discord 🚀
