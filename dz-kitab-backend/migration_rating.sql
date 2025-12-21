-- migration_ratings.sql

-- 1. Créer la table ratings
CREATE TABLE IF NOT EXISTS ratings (
    id SERIAL PRIMARY KEY,
    buyer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    seller_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    announcement_id INTEGER NOT NULL REFERENCES announcements(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    communication_rating INTEGER CHECK (communication_rating IS NULL OR (communication_rating >= 1 AND communication_rating <= 5)),
    condition_accuracy_rating INTEGER CHECK (condition_accuracy_rating IS NULL OR (condition_accuracy_rating >= 1 AND condition_accuracy_rating <= 5)),
    delivery_speed_rating INTEGER CHECK (delivery_speed_rating IS NULL OR (delivery_speed_rating >= 1 AND delivery_speed_rating <= 5)),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT buyer_not_seller CHECK (buyer_id != seller_id),
    CONSTRAINT unique_buyer_announcement UNIQUE (buyer_id, announcement_id)
);

-- 2. Créer la table seller_stats
CREATE TABLE IF NOT EXISTS seller_stats (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_ratings INTEGER DEFAULT 0,
    average_rating FLOAT DEFAULT 0.0,
    avg_communication FLOAT DEFAULT 0.0,
    avg_condition_accuracy FLOAT DEFAULT 0.0,
    avg_delivery_speed FLOAT DEFAULT 0.0,
    rating_5_count INTEGER DEFAULT 0,
    rating_4_count INTEGER DEFAULT 0,
    rating_3_count INTEGER DEFAULT 0,
    rating_2_count INTEGER DEFAULT 0,
    rating_1_count INTEGER DEFAULT 0,
    is_top_seller BOOLEAN DEFAULT FALSE,
    total_sales INTEGER DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Créer les index pour performance
CREATE INDEX IF NOT EXISTS idx_ratings_seller ON ratings(seller_id);
CREATE INDEX IF NOT EXISTS idx_ratings_buyer ON ratings(buyer_id);
CREATE INDEX IF NOT EXISTS idx_ratings_announcement ON ratings(announcement_id);
CREATE INDEX IF NOT EXISTS idx_ratings_created_at ON ratings(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_seller_stats_user ON seller_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_seller_stats_avg_rating ON seller_stats(average_rating DESC);

-- 4. Fonction pour mettre à jour automatiquement updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 5. Créer les triggers
DROP TRIGGER IF EXISTS update_ratings_updated_at ON ratings;
CREATE TRIGGER update_ratings_updated_at
    BEFORE UPDATE ON ratings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_seller_stats_updated_at ON seller_stats;
CREATE TRIGGER update_seller_stats_updated_at
    BEFORE UPDATE ON seller_stats
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 6. Vérifier les tables créées
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('ratings', 'seller_stats');

-- 7. Afficher la structure des tables
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('ratings', 'seller_stats')
ORDER BY table_name, ordinal_position;

-- Message de confirmation
SELECT '✅ Migration ratings terminée avec succès!' as message;
