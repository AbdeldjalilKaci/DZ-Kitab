-- migration_condition_scores.sql

-- Créer la table book_condition_scores
CREATE TABLE IF NOT EXISTS book_condition_scores (
    id SERIAL PRIMARY KEY,
    announcement_id INTEGER UNIQUE NOT NULL REFERENCES announcements(id) ON DELETE CASCADE,
    
    -- Page Score
    page_no_missing BOOLEAN DEFAULT FALSE,
    page_no_torn BOOLEAN DEFAULT FALSE,
    page_clean BOOLEAN DEFAULT FALSE,
    page_score FLOAT DEFAULT 0.0,
    
    -- Binding Score
    binding_no_loose BOOLEAN DEFAULT FALSE,
    binding_no_falling BOOLEAN DEFAULT FALSE,
    binding_stable BOOLEAN DEFAULT FALSE,
    binding_score FLOAT DEFAULT 0.0,
    
    -- Cover Score
    cover_no_detachment BOOLEAN DEFAULT FALSE,
    cover_clean BOOLEAN DEFAULT FALSE,
    cover_no_scratches BOOLEAN DEFAULT FALSE,
    cover_score FLOAT DEFAULT 0.0,
    
    -- Damage Score
    damage_no_burns BOOLEAN DEFAULT FALSE,
    damage_no_smell BOOLEAN DEFAULT FALSE,
    damage_no_insects BOOLEAN DEFAULT FALSE,
    damage_score FLOAT DEFAULT 0.0,
    
    -- Accessories Score
    accessories_complete BOOLEAN DEFAULT FALSE,
    accessories_content BOOLEAN DEFAULT FALSE,
    accessories_extras BOOLEAN DEFAULT FALSE,
    accessories_score FLOAT DEFAULT 0.0,
    
    -- Overall Score
    overall_score FLOAT DEFAULT 0.0,
    condition_label VARCHAR(50),
    
    -- Price Suggestion
    base_price FLOAT,
    suggested_price FLOAT,
    
    -- AI Analysis
    has_photos BOOLEAN DEFAULT FALSE,
    ai_analysis JSONB,
    photo_urls JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Créer les index
CREATE INDEX IF NOT EXISTS idx_condition_scores_announcement ON book_condition_scores(announcement_id);
CREATE INDEX IF NOT EXISTS idx_condition_scores_overall ON book_condition_scores(overall_score DESC);

-- Vérifier la table
SELECT 'Migration condition scores terminée!' as message;

SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'book_condition_scores'
ORDER BY ordinal_position;