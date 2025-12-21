-- migration_books.sql

-- 1. Créer l'enum pour les conditions de livre
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'bookconditionenum') THEN
        CREATE TYPE bookconditionenum AS ENUM ('Neuf', 'Comme neuf', 'Bon état', 'État acceptable', 'Usagé');
    END IF;
END $$;

-- 2. Créer l'enum pour le statut des annonces
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'announcementstatusenum') THEN
        CREATE TYPE announcementstatusenum AS ENUM ('Active', 'Vendu', 'Réservé', 'Désactivé');
    END IF;
END $$;

-- 3. Créer la table books
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR UNIQUE NOT NULL,
    title VARCHAR NOT NULL,
    subtitle VARCHAR,
    authors VARCHAR,
    publisher VARCHAR,
    published_date VARCHAR,
    description TEXT,
    page_count INTEGER,
    categories VARCHAR,
    language VARCHAR DEFAULT 'fr',
    cover_image_url VARCHAR,
    preview_link VARCHAR,
    info_link VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Créer la table announcements
CREATE TABLE IF NOT EXISTS announcements (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    price FLOAT NOT NULL,
    condition bookconditionenum NOT NULL,
    status announcementstatusenum DEFAULT 'Active',
    description TEXT,
    custom_images VARCHAR,
    location VARCHAR,
    views_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 5. Créer les index
CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);
CREATE INDEX IF NOT EXISTS idx_announcements_book_id ON announcements(book_id);
CREATE INDEX IF NOT EXISTS idx_announcements_user_id ON announcements(user_id);
CREATE INDEX IF NOT EXISTS idx_announcements_status ON announcements(status);
CREATE INDEX IF NOT EXISTS idx_announcements_created_at ON announcements(created_at DESC);

-- 6. Vérifier les tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('books', 'announcements');

ECHO '✅ Migration books terminée!';