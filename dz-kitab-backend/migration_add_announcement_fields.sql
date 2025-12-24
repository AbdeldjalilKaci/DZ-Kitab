-- migration_add_announcement_fields.sql

-- Créer l'enum pour les catégories
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'bookcategoryenum') THEN
        CREATE TYPE bookcategoryenum AS ENUM (
            'Informatique',
            'Mathématiques',
            'Physique',
            'Chimie',
            'Biologie',
            'Médecine',
            'Économie',
            'Gestion',
            'Droit',
            'Langues',
            'Littérature',
            'Histoire',
            'Géographie',
            'Philosophie',
            'Psychologie',
            'Architecture',
            'Ingénierie',
            'Autre'
        );
    END IF;
END $$;

-- Ajouter les nouvelles colonnes à la table announcements
ALTER TABLE announcements 
ADD COLUMN IF NOT EXISTS category bookcategoryenum,
ADD COLUMN IF NOT EXISTS market_price FLOAT,
ADD COLUMN IF NOT EXISTS final_calculated_price FLOAT,
ADD COLUMN IF NOT EXISTS page_count INTEGER,
ADD COLUMN IF NOT EXISTS publication_date VARCHAR;

-- Créer un index sur la catégorie
CREATE INDEX IF NOT EXISTS idx_announcements_category ON announcements(category);

-- Mettre à jour les announcements existantes avec une catégorie par défaut
UPDATE announcements 
SET category = 'Autre' 
WHERE category IS NULL;

-- Rendre la colonne category obligatoire après avoir mis à jour les valeurs existantes
ALTER TABLE announcements 
ALTER COLUMN category SET NOT NULL;

-- Ajouter une contrainte de vérification pour page_count
ALTER TABLE announcements 
ADD CONSTRAINT check_page_count_positive CHECK (page_count IS NULL OR page_count > 0);

-- Message de confirmation
SELECT '✅ Migration ajout catégorie et champs terminée!' as message;
