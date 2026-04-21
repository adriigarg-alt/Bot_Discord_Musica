# =========================================================
# CONECTAR CON MYSQL
# =========================================================
import os  # Permite acceder a variables del sistema (como archivos o variables de entorno)

from dotenv import load_dotenv  # Sirve para cargar variables desde un archivo .env (más seguro que poner datos en el código)

load_dotenv()  # Carga las variables del archivo .env al entorno del programa

import mysql.connector  # Importa la librería que permite a Python conectarse a MySQL

def get_db():
    # Crea y devuelve una conexión a la base de datos MySQL
    return mysql.connector.connect(
    host=os.getenv("DB_HOST"),       # Dirección del servidor (localhost = tu propio ordenador)
    user=os.getenv("DB_USER"),            # Usuario de MySQL (root suele ser el administrador)
    password=os.getenv("DB_PASSWORD"),  # Contraseña del usuario
    database=os.getenv("DB_NAME")     # Nombre de la base de datos a la que te conectas
)


# =========================================================
# IMPORTACIONES NECESARIAS
# =========================================================

import discord  # Librería principal para interactuar con la API de Discord (crear bots, enviar mensajes, etc.)

from discord.ext import commands  # Módulo que facilita crear comandos para el bot (ej: !play, !stop, etc.)

import yt_dlp  # Librería para descargar o extraer audio/video de YouTube (muy usada para bots de música)

import asyncio  # Permite trabajar con tareas asíncronas (muy importante en bots para no bloquear el programa)

import time  # Permite trabajar con tiempo (esperas, timestamps, etc.)

TOKEN = os.getenv("DISCORD_TOKEN")  
# Obtiene el token del bot desde las variables de entorno
# Busca una variable llamada DISCORD_TOKEN en el archivo .env


# =========================================================
# CONFIGURACIÓN DEL BOT
# =========================================================

intents = discord.Intents.default()  
# Crea un objeto con los "intents" (permisos del bot en Discord)

intents.message_content = True  
# Activa el permiso para que el bot pueda leer el contenido de los mensajes

# 🔧 FIX PARA PYTHON 3.14
asyncio.set_event_loop(asyncio.new_event_loop())  
# Soluciona problemas de compatibilidad con el bucle de eventos en Python 3.14

bot = commands.Bot(command_prefix="!", intents=intents)  
# Crea el bot:
# - command_prefix="!" → los comandos empezarán con "!" (ej: !play)
# - intents=intents → le pasa los permisos configurados arriba


# =========================================================
# BOTÓN INTERACTIVO DE FAVORITO
# =========================================================

class HeartButton(discord.ui.View):  
# Crea una clase que representa una vista interactiva (botones en Discord)

    def __init__(self, song_db_id: int):  
        super().__init__(timeout=None)  
        # Inicializa la clase base (View)
        # timeout=None → el botón no expira nunca

        self.liked = False  
        # Variable para saber si la canción está marcada como favorita o no

        self.song_db_id = song_db_id  
        # Guarda el ID de la canción en la base de datos (clave primaria)


    @discord.ui.button(label="", emoji="🤍", style=discord.ButtonStyle.gray, custom_id="heart_button")
    async def heart(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Define un botón dentro de la vista:
        # - sin texto (label="")
        # - emoji inicial 🤍
        # - color gris
        # - identificador único "heart_button"

        # Función que se ejecuta cuando alguien pulsa el botón

        user_id = interaction.user.id  
        # ID único del usuario en Discord

        username = interaction.user.name  
        # Nombre del usuario

        discord_id = interaction.user.id  
        # ID de Discord (igual que user_id en este caso)


       # ✅ Crear usuario si no existe
        # 🔹 Abrir conexión a la base de datos
        with get_db() as db:
            # 🔹 Crear cursor para ejecutar consultas SQL
            with db.cursor() as cursor:

                # 🔹 Comprobar si el usuario ya existe en la tabla users
                cursor.execute("SELECT id FROM users WHERE id=%s", (user_id,))
                result = cursor.fetchone()  # Devuelve el usuario o None si no existe

        # 🔹 Si el usuario NO existe en la base de datos
        if result is None:

            # 🔹 Abrir nueva conexión para insertar usuario
            with get_db() as db:
                with db.cursor() as cursor:

                    # 🔹 Insertar nuevo usuario en la tabla users
                    cursor.execute(
                        "INSERT INTO users (id, username, discord_id) VALUES (%s, %s, %s)",
                        (user_id, username, discord_id)
                    )

                    # 🔹 Guardar cambios en la base de datos
                    db.commit()

        # 🔹 Si el usuario YA existe
        else:

            # 🔹 Abrir conexión para actualizar datos del usuario
            with get_db() as db:
                with db.cursor() as cursor:

                    # 🔹 Actualizar username por si ha cambiado
                    cursor.execute(
                        "UPDATE users SET username=%s WHERE id=%s",
                        (username, user_id)
                    )

                # 🔹 Guardar cambios
                db.commit()


        # 🔹 Comprobar si la canción ya está en favoritos
        with get_db() as db:
            with db.cursor() as cursor:

                # 🔹 Buscar relación usuario-canción en favoritos
                cursor.execute(
                    "SELECT * FROM favoritos WHERE user_id=%s AND song_id=%s",
                    (user_id, self.song_db_id)
                )

                # 🔹 Guardar resultado (None si no existe)
                exists = cursor.fetchone()


        # 🔹 Si YA está en favoritos → eliminar
        if exists:

            # 🔹 Abrir conexión para eliminar favorito
            with get_db() as db:
                with db.cursor() as cursor:

                    # 🔹 Borrar registro de favoritos
                    cursor.execute(
                        "DELETE FROM favoritos WHERE user_id=%s AND song_id=%s",
                        (user_id, self.song_db_id)
                    )

                # 🔹 Guardar cambios
                db.commit()

            # 🔹 Cambiar emoji del botón a corazón vacío
            button.emoji = "🤍"

            # 🔹 Marcar estado interno como NO favorito
            self.liked = False


        # 🔹 Si NO está en favoritos → añadirlo
        else:

            # 🔹 Abrir conexión para insertar favorito
            with get_db() as db:
                with db.cursor() as cursor:

                    # 🔹 Insertar relación usuario-canción en favoritos
                    cursor.execute(
                        "INSERT INTO favoritos (user_id, song_id) VALUES (%s, %s)",
                        (user_id, self.song_db_id)
                    )

                # 🔹 Guardar cambios
                db.commit()

            # 🔹 Cambiar emoji del botón a corazón lleno
            button.emoji = "❤️"

            # 🔹 Marcar estado interno como favorito
            self.liked = True


        # 🔹 Actualizar el mensaje de Discord con el nuevo estado del botón
        await interaction.response.edit_message(view=self)

# =========================================================
# VER FAVORITOS 
# =========================================================

@bot.command()  
# Define un comando del bot → se usará como !favoritos

async def favoritos(ctx):  
# Función que se ejecuta cuando alguien escribe !favoritos
# ctx = contexto (quién lo ejecuta, en qué canal, etc.)

    user_id = ctx.author.id  
    # Obtiene el ID del usuario que ejecutó el comando


    # 🔹 Creamos un cursor local para asegurar lectura actualizada
    # 🔹 Crea conexión aislada para evitar problemas de concurrencia
    with get_db() as db:
        with db.cursor() as cursor:

            cursor.execute(
                """
                SELECT s.title
                FROM favoritos f
                JOIN songs s ON f.song_id = s.id
                WHERE f.user_id = %s
                """,
                (user_id,)
            )
            # Consulta SQL:
            # - Busca los títulos de canciones favoritas del usuario
            # - Hace JOIN entre:
            #   favoritos (f) → tabla de favoritos
            #   songs (s) → tabla de canciones
            # - Filtra por el usuario actual

            results = cursor.fetchall()
            # Obtiene TODOS los resultados (lista de canciones)


    # 🔹 Depuración: imprimir lo que se obtuvo de la DB
    print("DEBUG FAVORITOS:", results)  
    # Imprime en consola los resultados (útil para debug)


    if not results:  
    # Si la lista está vacía (no tiene favoritos)

        await ctx.send("No tienes canciones favoritas.")  
        # Envía mensaje al canal

        return  
        # Termina la función aquí


    text = ""  
    # Variable donde construiremos el texto del mensaje

    for song in results:  
    # Recorre cada canción obtenida de la BD

        text += f"❤️ {song[0]}\n"  
        # Añade cada título al texto
        # song[0] → porque cada fila es una tupla (solo tiene el título)


    embed = discord.Embed(
        title="❤️ Tus favoritos",
        description=text,
        color=discord.Color.red()
    )
    # Crea un embed (mensaje bonito en Discord):
    # - título
    # - lista de canciones
    # - color rojo


    await ctx.send(embed=embed)  
    # Envía el embed al canal

# =========================================================
# CREAR PLAYLIST (RESPETANDO DUPLICADOS CASE-INSENSITIVE DE LA DB)
# =========================================================

@bot.command()  
# Define el comando → se usa como !crear_playlist nombre

async def crear_playlist(ctx, nombre):  
# Función del comando
# ctx → información del mensaje
# nombre → nombre de la playlist que escribe el usuario

    user_id = ctx.author.id  
    # Obtiene el ID del usuario que ejecuta el comando


    try:
        # 🔹 Conexión aislada para evitar errores de concurrencia en Discord
        with get_db() as db:
            with db.cursor() as cursor:

                cursor.execute(
                    "INSERT INTO playlists (user_id, name) VALUES (%s, %s)",
                    (user_id, nombre)
                )
                # Intenta insertar una nueva playlist en la base de datos

            db.commit()
            # Guarda los cambios en la base de datos

        await ctx.send(f"📁 Playlist **{nombre}** creada correctamente.")
        # Mensaje de éxito

    except mysql.connector.errors.IntegrityError as e:
        # Si ocurre un error de integridad (por ejemplo, duplicado)

        # ⚠️ Detectamos error por clave única (nombre duplicado)
        await ctx.send(
            f"⚠️ No se puede crear la playlist **{nombre}**, ya existe con ese nombre (aunque sea mayúsculas/minúsculas diferentes)."
        )
        # Mensaje de error al usuario

# =========================================================
# BORRAR PLAYLIST
# =========================================================

@bot.command()  
# Define el comando → se usa como !borrar_playlist nombre

async def borrar_playlist(ctx, *, nombre):  
# Función del comando
# *nombre → permite que el nombre tenga espacios (ej: "Rock Español")

    user_id = ctx.author.id  
    # ID del usuario que ejecuta el comando


    # 🔹 Obtener playlist respetando mayúsculas/minúsculas
    with get_db() as db:
        with db.cursor() as cursor:

            cursor.execute(
                "SELECT id FROM playlists WHERE user_id=%s AND BINARY name=%s",
                (user_id, nombre)
            )
            # Busca la playlist del usuario
            # BINARY → hace la comparación sensible a mayúsculas/minúsculas

            result = cursor.fetchone()
            # Obtiene un solo resultado (la playlist)

    if not result:
        # Si no encontró la playlist

        await ctx.send("Playlist no encontrada.")
        # Envía mensaje de error

        return
        # Termina la función

    playlist_id = result[0]
    # Extrae el ID de la playlist (viene como tupla → (id,))


    # 🔹 Borrar canciones asociadas primero (FK)
    with get_db() as db:
        with db.cursor() as cursor:

            cursor.execute(
                "DELETE FROM playlist_songs WHERE playlist_id=%s",
                (playlist_id,)
            )
            # Borra todas las canciones relacionadas con esa playlist
            # (tabla intermedia)

        db.commit()
        # Guarda cambios de eliminación de canciones


    # 🔹 Borrar la playlist
    with get_db() as db:
        with db.cursor() as cursor:

            cursor.execute(
                "DELETE FROM playlists WHERE id=%s",
                (playlist_id,)
            )
            # Borra la playlist en sí

        db.commit()
        # Guarda los cambios de eliminación de la playlist


    await ctx.send(f"✅ Playlist **{nombre}** borrada correctamente.")
    # Mensaje de confirmación

# =========================================================
# AÑADIR CANCIÓN A PLAYLIST 
# =========================================================

@bot.command()
# Comando → !add_playlist nombre cancion

async def add_playlist(ctx, nombre, *, song_title):
    # nombre → nombre de la playlist
    # *song_title → título de la canción (permite espacios)

    user_id = ctx.author.id
    # ID del usuario


    # 🔹 Buscar la playlist
    with get_db() as db:
        with db.cursor() as cursor:

            cursor.execute(
                "SELECT id FROM playlists WHERE user_id=%s AND name=%s",
                (user_id, nombre)
            )
            # Busca la playlist del usuario

            result = cursor.fetchone()
            # Obtiene un resultado

    if not result:
        # Si no existe la playlist

        await ctx.send("Playlist no encontrada.")
        return

    playlist_id = result[0]
    # ID de la playlist


    # 🔍 Buscar varias coincidencias (hasta 5)
    with get_db() as db:
        with db.cursor() as cursor:

            cursor.execute(
                """
                SELECT id, title 
                FROM songs 
                WHERE LOWER(title) LIKE LOWER(%s)
                LIMIT 5
                """,
                ('%' + song_title + '%',)
            )
            # Busca canciones que contengan el texto (case-insensitive)
            # LIMIT 5 → máximo 5 resultados

            results = cursor.fetchall()
            # Lista de resultados

    if not results:
        # Si no encuentra canciones

        await ctx.send("No se encontró ninguna canción.")
        return


    # ✅ Si solo hay una coincidencia → añadir directamente
    if len(results) == 1:

        song_id = results[0][0]
        # ID de la canción

        title = results[0][1]
        # Título de la canción

    else:
        # 🎯 Mostrar opciones
        text = "🔎 He encontrado varias canciones:\n\n"

        for i, song in enumerate(results):
            # Recorre resultados con índice

            text += f"**{i+1}.** {song[1]}\n"
            # Muestra lista numerada

        text += "\nEscribe el número de la canción que quieres añadir."

        await ctx.send(text)
        # Envía opciones al usuario


        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        # Valida usuario correcto

        try:
            msg = await bot.wait_for("message", timeout=20.0, check=check)
            # Espera respuesta del usuario

            choice = int(msg.content) - 1
            # Convierte a índice

            if choice < 0 or choice >= len(results):
                await ctx.send("Número inválido.")
                return

            song_id = results[choice][0]
            # ID elegida

            title = results[choice][1]
            # título elegido

        except Exception:
            await ctx.send("Tiempo agotado o entrada inválida.")
            return


    # ✅ Insertar en playlist
    with get_db() as db:
        with db.cursor() as cursor:

            cursor.execute(
                "INSERT IGNORE INTO playlist_songs (playlist_id, song_id) VALUES (%s, %s)",
                (playlist_id, song_id)
            )
            # Inserta la canción en la playlist
            # IGNORE → evita duplicados

        db.commit()
        # Guarda cambios


    await ctx.send(f"🎵 Añadido **{title}** a la playlist **{nombre}**")
    # Mensaje final

# =========================================================
# VER PLAYLIST (CASE-SENSITIVE)
# =========================================================

@bot.command()  
# Define un comando → !ver_playlist nombre

async def ver_playlist(ctx, nombre):  
# nombre → nombre de la playlist (puede tener espacios si lo escribes correctamente)

    user_id = ctx.author.id  
    # ID del usuario que ejecuta el comando


    # 🔹 Obtener playlist con comparación case-sensitive usando BINARY
    with get_db() as db:
        with db.cursor() as cursor:

            cursor.execute(
                "SELECT id FROM playlists WHERE user_id=%s AND BINARY name=%s",
                (user_id, nombre)
            )
            # Busca la playlist exacta (respetando mayúsculas/minúsculas) del usuario

            result = cursor.fetchone()
            # Obtiene un solo resultado (id de la playlist)

    if not result:
        # Si no existe la playlist

        await ctx.send("Playlist no encontrada.")
        return

    playlist_id = result[0]
    # ID de la playlist encontrada


    # 🔹 Obtener canciones usando JOIN para traer títulos
    with get_db() as db:
        with db.cursor() as cursor:

            cursor.execute(
                """
                SELECT s.title
                FROM playlist_songs ps
                JOIN songs s ON ps.song_id = s.id
                WHERE ps.playlist_id = %s
                """,
                (playlist_id,)
            )
            # Obtiene todas las canciones de esa playlist usando JOIN con la tabla songs

            songs = cursor.fetchall()
            # Lista de canciones

    if not songs:
        # Si no hay canciones

        await ctx.send("Playlist vacía.")
        return  


    text = ""  
    # Preparar texto para mostrar

    for song in songs:  
        text += f"🎵 {song[0]}\n"  
        # Añade cada título de canción


    embed = discord.Embed(
        title=f"📁 Playlist: {nombre}",
        description=text,
        color=discord.Color.blue()
    )
    # Crea un embed bonito:
    # - título con el nombre de la playlist
    # - lista de canciones
    # - color azul


    await ctx.send(embed=embed)  
    # Envía embed al canal

# =========================================================
# VER MIS PLAYLISTS
# =========================================================

@bot.command()  
# Define un comando → !mis_playlists

async def mis_playlists(ctx):  
# Función del comando

    user_id = ctx.author.id  
    # ID del usuario que ejecuta el comando

    # 🔹 Consulta playlists del usuario con conteo de canciones
    with get_db() as db:
        with db.cursor() as cursor:

            cursor.execute("""  
            SELECT p.name, COUNT(ps.song_id)
            FROM playlists p
            LEFT JOIN playlist_songs ps ON p.id = ps.playlist_id
            WHERE p.user_id = %s
            GROUP BY p.id, p.name
            """, (user_id,))
            # Consulta SQL:
            # - Trae todas las playlists del usuario
            # - LEFT JOIN con playlist_songs para contar canciones
            # - COUNT(ps.song_id) → número de canciones por playlist
            # - GROUP BY p.id, p.name → agrupa por playlist

            playlists = cursor.fetchall()
            # Obtiene la lista de playlists

    if not playlists:
        # Si no hay playlists

        await ctx.send("No tienes playlists creadas.")
        return


    text = ""  
    # Preparar texto para el embed

    for name, total in playlists:  
        text += f"📁 {name} ({total} canciones)\n"  
        # Añade cada playlist con número de canciones


    embed = discord.Embed(
        title="📁 Tus Playlists",
        description=text,
        color=discord.Color.purple()
    )
    # Crea embed bonito:
    # - título
    # - descripción con la lista
    # - color morado


    await ctx.send(embed=embed)  
    # Envía embed al canal

# =========================================================
# VOLUMEN Y ESTADÍSTICAS
# =========================================================

# Diccionario por guild para evitar conflictos entre servidores
guild_data = {}
# Ejemplo de estructura:
# guild_data[guild_id] = {
#     "volume": 1.0,
#     "history": [],
#     "counter": {}
# }

# =========================================================
# REPRODUCIR PLAYLIST
# =========================================================

@bot.command()  
# Comando → !play_playlist nombre

async def play_playlist(ctx, *, nombre):  
# nombre → nombre de la playlist (permite espacios)

    user_id = ctx.author.id  
    # ID del usuario


    # 🔹 Obtener playlist respetando mayúsculas/minúsculas
    with get_db() as db:
        with db.cursor() as cursor:

            cursor.execute(
                "SELECT id FROM playlists WHERE user_id=%s AND BINARY name=%s",
                (user_id, nombre)
            )
            result = cursor.fetchone()
            # Busca la playlist exacta (case-sensitive)

    if not result:
        await ctx.send("Playlist no encontrada.")
        return

    playlist_id = result[0]
    # ID de la playlist encontrada


    # 🔹 Obtener canciones de la playlist en orden de inserción
    with get_db() as db:
        with db.cursor() as cursor:

            cursor.execute(
                """
                SELECT s.song_id, s.title, s.duration
                FROM playlist_songs ps
                JOIN songs s ON ps.song_id = s.id  -- <--- Aquí usamos s.id, no s.song_id
                WHERE ps.playlist_id = %s
                ORDER BY ps.id ASC
                """,
                (playlist_id,)
            )
            songs = cursor.fetchall()
            # Lista de canciones en la playlist (ordenadas por inserción)

    if not songs:
        await ctx.send("La playlist está vacía.")
        return  


    # 🔹 Conectar al canal de voz si no está conectado
    if not ctx.author.voice:  
        # Si el usuario no está en un canal de voz
        await ctx.send("Debes estar en un canal de voz para reproducir la playlist 🎧")
        return  

    if not ctx.voice_client:  
        # Si el bot no está conectado a ningún canal
        await ctx.author.voice.channel.connect(self_deaf=True)
    elif ctx.voice_client.channel != ctx.author.voice.channel:  
        # Si el bot está en otro canal
        await ctx.voice_client.move_to(ctx.author.voice.channel)


    await ctx.send(f"▶️ Reproduciendo playlist **{nombre}** con {len(songs)} canciones...")


    # 🔹 Función interna para reproducir canciones en secuencia
    async def play_next(index=0):  
        # index → posición de la canción actual

        if index >= len(songs):  
            # Si llegamos al final de la playlist
            await ctx.send(f"✅ Playlist **{nombre}** finalizada.")
            return  

        yt_id, title, duration = songs[index]  
        # Obtenemos datos de la canción


        # 🔹 Obtener URL de YouTube
        ydl_options = {
            'format': 'bestaudio/best',
            'quiet': True,
            'default_search': 'ytsearch',
            'noplaylist': True,
            'extract_flat': False
        }
        # Opciones de yt_dlp

        with yt_dlp.YoutubeDL(ydl_options) as ydl:
            info = ydl.extract_info(title, download=False)
            if 'entries' in info:  
                info = info['entries'][0]  
            # Toma la primera coincidencia si devuelve lista

        url = next((f['url'] for f in info['formats'] if f.get('acodec') != 'none'), None)
        # URL del audio compatible

        if url is None:  
            # Si no se pudo obtener audio
            await ctx.send(f"⚠️ No se pudo reproducir **{title}**, saltando...")
            await play_next(index + 1)
            return  


        # 🔹 Configurar volumen
        volume_level = guild_data.get(ctx.guild.id, {}).get("volume", 1.0)
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(
                url,
                executable="ffmpeg",
                before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                options="-vn -loglevel quiet"
            ),
            volume=volume_level
        )


        # 🔹 Función que se llama al terminar de reproducir
        def after_playing(error):
            fut = asyncio.run_coroutine_threadsafe(play_next(index + 1), bot.loop)
            try:
                fut.result()
            except Exception:
                pass  
            # Asegura que la siguiente canción se reproduzca


        ctx.voice_client.play(source, after=after_playing)
        await ctx.send(f"🎶 Ahora reproduciendo: **{title}**")


    # 🔹 Iniciar reproducción
    await play_next(0)  
    # Comienza desde la primera canción


# =========================================================
# VARIABLES GLOBALES
# =========================================================

start_time = 0  
# Momento en que empezó la reproducción (timestamp)

paused_time = 0  
# Momento en que se pausó la canción

is_paused = False  
# Indica si la canción está pausada o no

# 🔥 CONTADOR DE TIEMPO PARA EL PANEL
current_time_counter = 0  
# Contador de tiempo actual (para mostrar progreso en el panel)


# =========================================================
# FORMATEAR TIEMPO
# =========================================================
def format_time(seconds):  
    # Convierte segundos a formato MM:SS

    minutes = int(seconds // 60)  
    # Calcula minutos completos

    seconds = int(seconds % 60)  
    # Calcula segundos restantes

    return f"{minutes}:{seconds:02}"  
    # Devuelve string tipo "3:07", con dos dígitos para segundos


# =========================================================
# BARRA DE PROGRESO
# =========================================================
def progress_bar(current, total, length=15):  
    """
    Crea una barra de progreso tipo "▬🔘▬" para mostrar avance.
    - current: tiempo actual (segundos)
    - total: duración total (segundos)
    - length: longitud de la barra (por defecto 15)
    """

    if total == 0:  
        # Evita división por cero
        return "🔘" + "▬" * (length - 1)  
        # Solo el marcador al inicio

    progress = int((current / total) * length)  
    # Calcula cuántos "▬" antes del marcador según porcentaje

    progress = min(progress, length - 1)  
    # Asegura que no se pase del tamaño máximo

    bar = "▬" * progress + "🔘" + "▬" * (length - progress - 1)  
    # Construye la barra:
    # ▬▬🔘▬▬ (por ejemplo)

    return bar  
    # Devuelve la barra como string


# =========================================================
# BOT LISTO
# =========================================================

@bot.event  
# Evento especial de Discord que se activa cuando el bot está listo

async def on_ready():  
    # Función que corre al iniciar el bot

    print(f"Bot conectado como {bot.user}")  
    # Mensaje en consola para confirmar que el bot se conectó correctamente

    CHANNEL_ID = int(os.getenv("CHANNEL_ID")) # CAMBIA ESTO  
    # ID del canal donde se enviará el mensaje de inicio

    channel = bot.get_channel(CHANNEL_ID)  
    # Obtiene el objeto canal de Discord a partir del ID

    if channel:  
        # Si el canal existe

        embed = discord.Embed(
            title="🎧 MUSIC BOT ONLINE",
            description="El bot se ha iniciado correctamente.\n\nUsa **!menu** para ver todos los comandos.",
            color=discord.Color.green()
        )
        # Crea un embed bonito con título, descripción y color verde

        embed.add_field(
            name="📜 Comandos Disponibles",
            value="Escribe `!menu` para ver la lista completa.",
            inline=False
        )
        # Añade campo con información extra sobre comandos

        embed.set_footer(text="Listo para reproducir música 🎵")  
        # Footer del embed

        await channel.send(embed=embed)  
        # Envía el embed al canal seleccionado
        
    # =========================================================
    # MENÚ AUTOMÁTICO
    # =========================================================

    if channel:
         # Solo si el canal existe

        embed_menu = discord.Embed(
            title="📜 PANEL DE COMANDOS",
            description="Estos son todos los comandos disponibles del bot:",
            color=discord.Color.blurple()
        )
        # Crea embed para el menú de comandos con color blurple

        # 🔹 Lista de comandos con descripción
        embed_menu.add_field(
            name="🏓 !ping",
            value="Comprueba si el bot está activo.",
            inline=False
        )

        embed_menu.add_field(
            name="🔌 !join",
            value="Conecta el bot a tu canal de voz.",
            inline=False
        )

        embed_menu.add_field(
            name="🎶 !play <canción>",
            value="Reproduce música desde YouTube.",
            inline=False
        )

        embed_menu.add_field(
            name="⏸️ !stop",
            value="Pausa la música actual.",
            inline=False
        )

        embed_menu.add_field(
            name="▶️ !resume",
            value="Reanuda la canción pausada.",
            inline=False
        )

        embed_menu.add_field(
            name="⏭️ !skip",
            value="Cambia la canción actual.",
            inline=False
        )
        embed_menu.add_field(
            name="🔊 !volumen <0-2>",
            value="Ajusta el volumen de la música.",
            inline=False
        )

        embed_menu.add_field(
            name="📜 !historial",
            value="Muestra las últimas canciones reproducidas.",
            inline=False
        )

        embed_menu.add_field(
            name="🔥 !top",
            value="Muestra las canciones más escuchadas.",
            inline=False
        )
        embed_menu.add_field(
            name="❤️ !favoritos",
            value="Muestra tus canciones favoritas.",
            inline=False
        )

        embed_menu.add_field(
            name="📁 !crear_playlist <nombre>",
            value="Crea una nueva playlist.",
            inline=False
        )

        embed_menu.add_field(
            name="➕ !add_playlist <nombre> <canción>",
            value="Añade una canción a una playlist.",
            inline=False
        )

        embed_menu.add_field(
            name="📂 !ver_playlist <nombre>",
            value="Muestra las canciones de una playlist.",
            inline=False
        )
        embed_menu.add_field(
            name="📁 !mis_playlists",
            value="Muestra todas tus playlists.",
            inline=False
        )
        embed_menu.add_field(
            name="❌ !borrar_playlist <nombre>",
            value="Elimina una playlist existente.",
            inline=False
        )
        embed_menu.add_field(
            name="▶️ !play_playlist <nombre>",
            value="Reproduce todas las canciones de una playlist.",
            inline=False
        )

        embed_menu.set_footer(text="🎧 Music Bot listo")
        # Footer del embed

        await channel.send(embed=embed_menu)
        # Envía el menú al canal


# =========================================================
# PING
# =========================================================

@bot.command()  
# Define un comando → !ping

async def ping(ctx):  
    # Función que se ejecuta cuando se escribe !ping

    await ctx.send("Pong!")  
    # Envía "Pong!" al canal, confirmando que el bot responde


# =========================================================
# MENÚ
# =========================================================

@bot.command()  
# Define un comando → !menu

async def menu(ctx):  
    # Función que se ejecuta al escribir !menu

    embed = discord.Embed(
        title="🎧 MENÚ DE COMANDOS - MUSIC BOT",
        description="Aquí tienes todos los comandos disponibles:",
        color=discord.Color.blurple()
    )
    # Crea un embed visual con título, descripción y color blurple

    # 🔹 Agregamos cada comando como campo del embed
    embed.add_field(name="🏓 !ping", value="Verifica si el bot está activo.", inline=False)
    embed.add_field(name="🔌 !join", value="Conecta el bot al canal de voz donde estás.", inline=False)
    embed.add_field(name="🎶 !play <nombre>", value="Reproduce una canción desde YouTube.", inline=False)
    embed.add_field(name="⏸️ !stop", value="Pausa la canción actual.", inline=False)
    embed.add_field(name="▶️ !resume", value="Reanuda la canción pausada.", inline=False)
    embed.add_field(name="⏭️ !skip", value="Cambia la canción actual.", inline=False)
    embed.add_field(name="🔊 !volumen <0-2>", value="Ajusta el volumen de la musica.", inline=False)
    embed.add_field(name="📜 !historial", value="Muestra las últimas canciones reproducidas.", inline=False)
    embed.add_field(name="🔥 !top", value="Muestra las canciones más escuchadas.", inline=False)
    embed.add_field(name="❤️ !favoritos", value="Muestra tus canciones favoritas.", inline=False)
    embed.add_field(name="📁 !crear_playlist <nombre>", value="Crea una nueva playlist.", inline=False)
    embed.add_field(name="➕ !add_playlist <nombre> <canción>", value="Añade una canción a una playlist.", inline=False)
    embed.add_field(name="📂 !ver_playlist <nombre>", value="Muestra las canciones de una playlist.", inline=False)
    embed.add_field(name="📂 !mis_playlist <nombre>", value="Muestra todas tus playlists.", inline=False)
    embed.add_field(name="❌ !borrar_playlist <nombre>", value="Elimina una playlist existente.", inline=False)
    embed.add_field(name="▶️ !play_playlist <nombre>", value="Reproduce todas las canciones de una playlist.", inline=False)

    embed.set_footer(text="Desarrollado con ❤️")  
    # Footer opcional con un mensaje bonito

    await ctx.send(embed=embed)  
    # Envía el embed al canal donde se escribió el comando


# =========================================================
# JOIN
# =========================================================

@bot.command()  
# Define un comando → !join

async def join(ctx):  
    # Función que se ejecuta al escribir !join

    if not ctx.author.voice:  
        # Verifica si el usuario está en un canal de voz
        await ctx.send("Debes estar en un canal de voz.")
        return  # Sale de la función si no está en canal

    channel = ctx.author.voice.channel  
    # Obtiene el canal de voz donde está el usuario

    if ctx.voice_client:  
        # Si el bot ya está conectado a un canal de voz
        await ctx.voice_client.move_to(channel)  
        # Mueve al bot al canal del usuario
    else:  
        # Si el bot no está conectado
        await channel.connect(self_deaf=True)  
        # Se conecta al canal y se silencia a sí mismo

    await ctx.send("Conectado al canal 🎧")  
    # Mensaje confirmando que se conectó

# =========================================================
# VOLUMEN
# =========================================================

@bot.command()  
# Define un comando → !volumen

async def volumen(ctx, level: float):  
    # level: número flotante que indica el volumen deseado

    if level < 0 or level > 2:  
        # Verifica que el volumen esté dentro del rango permitido
        await ctx.send("El volumen debe estar entre **0 y 2**.")
        return  # Sale de la función si está fuera de rango

    guild_id = ctx.guild.id  
    # ID del servidor (guild) donde se ejecuta el comando

    if guild_id not in guild_data:  
        # Si no existe info del servidor, inicializa datos
        guild_data[guild_id] = {"volume": 1.0, "history": [], "counter": {}}

    guild_data[guild_id]["volume"] = level  
    # Guarda el volumen en la estructura de datos global

    if ctx.voice_client and ctx.voice_client.source:  
        # Si el bot está reproduciendo música actualmente
        ctx.voice_client.source.volume = level  
        # Ajusta el volumen de la canción en reproducción

    if level == 0:  
        await ctx.send("🔇 Música silenciada.")  
        # Mensaje especial si silenciamos
    else:  
        await ctx.send(f"🔊 Volumen ajustado a **{level}**")  
        # Mensaje confirmando el nivel de volumen


# =========================================================
# STOP
# =========================================================

@bot.command()  
# Define un comando → !stop

async def stop(ctx):  
    # Función que se ejecuta al escribir !stop

    global paused_time, is_paused  
    # Accede a las variables globales para guardar el estado de pausa

    if ctx.voice_client and ctx.voice_client.is_playing():  
        # Verifica si el bot está conectado y está reproduciendo música

        ctx.voice_client.pause()  
        # Pausa la canción actual

        paused_time = time.time()  
        # Guarda el momento exacto de la pausa (timestamp)

        is_paused = True  
        # Marca que la música está pausada

        await ctx.send("⏸️ Música pausada. Usa **!resume** para continuar.")  
        # Mensaje al usuario confirmando la pausa
    else:  
        await ctx.send("No hay ninguna canción reproduciéndose.")  
        # Mensaje si no hay música que pausar

# =========================================================
# RESUME
# =========================================================

@bot.command()  
# Define un comando → !resume

async def resume(ctx):  
    # Función que se ejecuta al escribir !resume

    global start_time, paused_time, is_paused  
    # Accede a las variables globales de tiempo y estado de pausa

    if ctx.voice_client and ctx.voice_client.is_paused():  
        # Verifica si el bot está conectado y la música está pausada

        ctx.voice_client.resume()  
        # Reanuda la canción pausada

        start_time += (time.time() - paused_time)  
        # Ajusta el tiempo de inicio para mantener el progreso correcto
        # Se suma el tiempo que estuvo pausada

        is_paused = False  
        # Marca que la música ya no está pausada

        await ctx.send("▶️ Música reanudada.")  
        # Mensaje confirmando que la canción se reanudó
    else:  
        await ctx.send("No hay ninguna canción pausada.")  
        # Mensaje si no había música pausada

# =========================================================
# SKIP
# =========================================================

@bot.command()  
# Define un comando → !skip

async def skip(ctx):  
    # Función que se ejecuta al escribir !skip

    if not ctx.voice_client:  
        # Verifica si el bot está conectado a un canal de voz
        await ctx.send("No estoy conectado a un canal de voz.")
        return  # Sale si no hay conexión

    if ctx.voice_client.is_playing():  
        ctx.voice_client.stop()  
        # Detiene la canción actual inmediatamente

    # 🔹 Mensaje interactivo pidiendo nueva canción
    embed = discord.Embed(
        title="⏭️ Cambiar canción",
        description="🎵 **Dime el nombre de la nueva canción...**",
        color=discord.Color.blurple()
    )
    embed.set_footer(text="Escribe el nombre en el chat ✍️")
    await ctx.send(embed=embed)

    # 🔹 Función para filtrar mensajes del mismo usuario y canal
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        # Espera mensaje del usuario con el nombre de la nueva canción
        msg = await bot.wait_for("message", timeout=30.0, check=check)

        await play(ctx, search=msg.content)  
        # Llama al comando play con el nombre proporcionado
    except asyncio.TimeoutError:
        await ctx.send("⌛ Tiempo agotado. Intenta nuevamente con !skip")  
        # Mensaje si el usuario no responde a tiempo

# =========================================================
# 🎶 PLAY
# =========================================================

@bot.command()  
# Decorador que indica que la función siguiente será un comando de Discord
# Esto permite que se invoque con !play <nombre_canción>

async def play(ctx, *, search):  
    # Función asincrónica que se ejecuta cuando se llama !play
    # 'ctx' es el contexto del comando (quién lo llamó, canal, servidor, etc.)
    # 'search' es el término de búsqueda ingresado por el usuario
    # '*' indica que todo lo que sigue se captura como un solo argumento string

    global start_time, is_paused, current_time_counter  
    # Permite modificar estas variables globales desde dentro de la función
    # start_time: tiempo en que comenzó la canción
    # is_paused: indica si la canción está en pausa
    # current_time_counter: contador de segundos transcurridos

    if not ctx.author.voice:  
        # Verifica si el autor del comando está conectado a un canal de voz
        await ctx.send("Debes estar en un canal de voz 🎧")
        # Si no está en un canal de voz, envía mensaje de error
        return
        # Sale de la función para no ejecutar el resto

    guild_id = ctx.guild.id  
    # Obtiene el ID único del servidor (guild) donde se ejecuta el comando

    if guild_id not in guild_data:
        # Si no existen datos guardados para este servidor, los inicializa
        guild_data[guild_id] = {"volume": 1.0, "history": [], "counter": {}}
        # volume: nivel de volumen
        # history: lista de canciones reproducidas
        # counter: contador de cuántas veces se ha reproducido cada canción

    volume_level = guild_data[guild_id]["volume"]  
    # Obtiene el nivel de volumen actual del servidor

    if not ctx.voice_client:
        # Verifica si el bot está conectado a un canal de voz
        await ctx.author.voice.channel.connect(self_deaf=True)  
        # Conecta el bot al canal de voz del autor
        # self_deaf=True hace que el bot no escuche el audio del canal

    if ctx.voice_client.is_playing():
        # Si ya hay una canción reproduciéndose
        ctx.voice_client.stop()  
        # Detiene la reproducción actual antes de iniciar la nueva

    # =======================
    # Configuración de yt_dlp
    # =======================
    ydl_options = {
        'format': 'bestaudio/best',  # Extrae la mejor calidad de audio disponible
        'quiet': True,                # No muestra mensajes por consola
        'default_search': 'ytsearch',# Permite buscar por nombre en YouTube
        'noplaylist': True,           # Evita descargar listas de reproducción
        'extract_flat': False         # Descarga información completa del video
    }

    # =======================
    # Extraer info de YouTube
    # =======================
    with yt_dlp.YoutubeDL(ydl_options) as ydl:
        info = ydl.extract_info(search, download=False)
        # Obtiene información del video sin descargarlo
        if 'entries' in info:
            info = info['entries'][0]  # Si es una lista, toma solo el primer resultado

    # =======================
    # Obtener URL de audio
    # =======================
    url = None
    for f in info['formats']:
        if f.get('acodec') != 'none':
            url = f['url']  # Guarda la URL del stream de audio
            break

    if url is None:
        # Si no se encontró URL de audio válido
        await ctx.send("No se pudo encontrar un stream de audio válido.")
        return

    # =======================
    # Datos de la canción
    # =======================
    title = info['title']  
    # Nombre de la canción
    yt_id = info.get("id", title)  
    # ID único de YouTube, si no existe usa el título
    duration = info.get("duration", 0)  
    # Duración en segundos
    thumbnail = info.get("thumbnail")  
    # URL de la miniatura
    current_time_counter = 0  
    # Reinicia el contador de tiempo transcurrido

    print("DEBUG yt_id:", yt_id, "title:", title)
    # Muestra información en consola para debug

    # =======================
    # Guardar canción y obtener PK
    # =======================

    with get_db() as db:
        with db.cursor() as cursor:

            cursor.execute(
                "INSERT IGNORE INTO songs (song_id, title, duration) VALUES (%s, %s, %s)",
                (yt_id, title, duration)
            )
            db.commit()
            # Guarda la canción en la base de datos

    with get_db() as db:
        with db.cursor() as cursor:

            cursor.execute("SELECT id FROM songs WHERE song_id=%s", (yt_id,))
            result = cursor.fetchone()
            # Obtiene la PK (id) real de la canción

    if result is None:
        await ctx.send("Error al guardar la canción en la base de datos.")
        return

    song_db_id = result[0]
    # Guarda la PK real para usarla como FK en otras tablas o botones

    # =======================
    # Guardar historial y contador por servidor
    # =======================
    guild_data[guild_id]["history"].append(title)
    # Añade el título de la canción al historial del servidor
    if title in guild_data[guild_id]["counter"]:
        guild_data[guild_id]["counter"][title] += 1
        # Incrementa contador si ya se reprodujo antes
    else:
        guild_data[guild_id]["counter"][title] = 1
        # Inicializa el contador si es la primera vez

    # =======================
    # Configurar FFmpeg y reproducir
    # =======================
    ffmpeg_options = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        # Reconecta automáticamente si falla el stream
        "options": "-vn -loglevel quiet"  
        # -vn: no procesa video, solo audio
        # -loglevel quiet: evita mostrar logs de FFmpeg
    }

    source = discord.PCMVolumeTransformer(
        discord.FFmpegPCMAudio(url, executable="ffmpeg", **ffmpeg_options),
        volume=volume_level
    )
    # Crea un objeto de audio con volumen ajustable y stream de FFmpeg

    ctx.voice_client.play(source)
    # Reproduce la canción en el canal de voz

    # =======================
    # Embed Now Playing + HeartButton
    # =======================
    embed = discord.Embed(
        title="🎶 Now Playing",
        description=f"**{title}**",
        color=discord.Color.green()
    )
    # Crea un embed de Discord mostrando la canción en reproducción

    bar = progress_bar(0, duration)
    # Barra de progreso inicial (0 segundos)
    embed.add_field(
        name="⏱️ Progreso",
        value=f"{bar}\n`{format_time(0)} / {format_time(duration)}`",
        inline=False
    )
    # Muestra progreso de la canción
    embed.add_field(name="Controles", value="▶️ ⏸️ ⏭️ 🔁", inline=False)
    # Muestra controles en el embed

    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
        # Añade la miniatura de la canción

    # Botón de favorito usando la PK real
    view = HeartButton(song_db_id=song_db_id)
    # Crea un botón interactivo que puede marcar la canción como favorita
    message = await ctx.send(embed=embed, view=view)
    # Envía el embed al canal

    # =======================
    # Loop de actualización del progreso
    # =======================
    while True:
        await asyncio.sleep(5)  # Actualiza cada 5 segundos

        if not ctx.voice_client:
            break  # Si el bot sale del canal, termina el loop
        if is_paused:
            continue  # No avanza el tiempo si la canción está pausada

        current_time_counter += 5
        # Incrementa el contador de tiempo transcurrido
        current_time = min(current_time_counter, duration)
        # No deja que el tiempo supere la duración total

        bar = progress_bar(current_time, duration)
        embed.set_field_at(
            0,
            name="⏱️ Progreso",
            value=f"{bar}\n`{format_time(current_time)} / {format_time(duration)}`",
            inline=False
        )
        # Actualiza la barra de progreso en el embed
        embed.color = discord.Color.red() if view.liked else discord.Color.green()
        # Cambia color si la canción está marcada como favorita
        await message.edit(embed=embed, view=view)
        # Edita el mensaje original para reflejar los cambios

        if current_time >= duration:
            break  # Si la canción terminó, sale del loop

    embed.color = discord.Color.red()
    embed.set_footer(text="Canción finalizada 🎵")
    await message.edit(embed=embed, view=view)
    # Marca visualmente que la canción terminó

# =========================================================
# HISTORIAL DE CANCIONES
# =========================================================

@bot.command()  
# Define un comando → !historial

async def historial(ctx):  
    # Función que se ejecuta al escribir !historial

    guild_id = ctx.guild.id  
    # ID del servidor donde se ejecuta el comando

    if guild_id not in guild_data or not guild_data[guild_id]["history"]:  
        # Verifica si hay historial de canciones para este servidor
        await ctx.send("No se han reproducido canciones todavía.")
        return  # Sale si no hay historial

    last_songs = guild_data[guild_id]["history"][-10:]  
    # Toma las últimas 10 canciones reproducidas

    text = ""
    for song in reversed(last_songs):  
        # Invierte el orden para mostrar la más reciente primero
        text += f"🎵 {song}\n"

    embed = discord.Embed(
        title="📜 Últimas canciones escuchadas",
        description=text,
        color=discord.Color.blue()
    )
    # Crea un embed con título y listado de canciones

    await ctx.send(embed=embed)  
    # Envía el embed al canal


# =========================================================
# CANCIONES MÁS ESCUCHADAS
# =========================================================

@bot.command()  
# Define un comando → !top

async def top(ctx):  
    # Función que se ejecuta al escribir !top

    guild_id = ctx.guild.id  
    # ID del servidor donde se ejecuta el comando

    if guild_id not in guild_data or not guild_data[guild_id]["counter"]:  
        # Verifica si hay estadísticas de reproducciones para este servidor
        await ctx.send("Todavía no hay estadísticas.")
        return  # Sale si no hay datos

    # 🔹 Ordena las canciones por número de reproducciones (de mayor a menor)
    sorted_songs = sorted(
        guild_data[guild_id]["counter"].items(), 
        key=lambda x: x[1], 
        reverse=True
    )

    text = ""
    for song, count in sorted_songs[:10]:  
        # Toma las 10 canciones más escuchadas
        text += f"🎵 **{song}** — {count} reproducciones\n"

    embed = discord.Embed(
        title="🔥 Canciones más escuchadas",
        description=text,
        color=discord.Color.gold()
    )
    # Crea un embed con título y listado de canciones más escuchadas

    await ctx.send(embed=embed)  
    # Envía el embed al canal de texto


# =========================================================
# EJECUCIÓN
# =========================================================

bot.run(TOKEN)


