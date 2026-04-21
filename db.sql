USE musicbot;

-- =====================================================
-- 🔹 TABLA USERS
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id BIGINT NOT NULL,        -- ID de Discord
    username VARCHAR(100) NOT NULL,
    discord_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY idx_discord_id (discord_id)
) ENGINE=InnoDB;

-- =====================================================
-- 🔹 TABLA SONGS
-- =====================================================
CREATE TABLE IF NOT EXISTS songs (
    id INT NOT NULL AUTO_INCREMENT,
    song_id VARCHAR(50) NOT NULL,    -- ID de YouTube
    title VARCHAR(255) NOT NULL,
    duration INT NOT NULL,           -- Duración en segundos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY idx_song_id (song_id),
    INDEX idx_title (title)
) ENGINE=InnoDB;

-- =====================================================
-- 🔹 TABLA FAVORITOS
-- =====================================================
CREATE TABLE IF NOT EXISTS favoritos (
    id INT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    song_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY idx_user_song (user_id, song_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =====================================================
-- 🔹 TABLA PLAYLISTS
-- =====================================================
CREATE TABLE IF NOT EXISTS playlists (
    id INT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY idx_user_playlist (user_id, name),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =====================================================
-- 🔹 TABLA PLAYLIST_SONGS
-- =====================================================
CREATE TABLE IF NOT EXISTS playlist_songs (
    id INT NOT NULL AUTO_INCREMENT,
    playlist_id INT NOT NULL,
    song_id INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY idx_playlist_song (playlist_id, song_id),
    FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
) ENGINE=InnoDB;