-- migration_suspensions.sql

-- 1. Créer la table user_suspensions
CREATE TABLE IF NOT EXISTS user_suspensions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reason VARCHAR NOT NULL,
    description TEXT,
    suspended_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    suspension_end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    zero_rating_count INTEGER DEFAULT 0,
    low_rating_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    reactivated_at TIMESTAMP WITH TIME ZONE,
    created_by_admin BOOLEAN DEFAULT FALSE,
    admin_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 2. Créer la table rating_alerts
CREATE TABLE IF NOT EXISTS rating_alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    alert_type VARCHAR NOT NULL,
    low_rating_count INTEGER DEFAULT 0,
    zero_rating_count INTEGER DEFAULT 0,
    average_rating FLOAT DEFAULT 0.0,
    email_sent BOOLEAN DEFAULT FALSE,
    email_sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Créer les index pour performance
CREATE INDEX IF NOT EXISTS idx_user_suspensions_user ON user_suspensions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_suspensions_active ON user_suspensions(is_active);
CREATE INDEX IF NOT EXISTS idx_user_suspensions_end_date ON user_suspensions(suspension_end_date);
CREATE INDEX IF NOT EXISTS idx_user_suspensions_user_active ON user_suspensions(user_id, is_active);

CREATE INDEX IF NOT EXISTS idx_rating_alerts_user ON rating_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_rating_alerts_created_at ON rating_alerts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_rating_alerts_type ON rating_alerts(alert_type);

-- 4. Fonction pour mettre à jour automatiquement updated_at
CREATE OR REPLACE FUNCTION update_suspensions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 5. Créer le trigger
DROP TRIGGER IF EXISTS update_suspensions_updated_at_trigger ON user_suspensions;
CREATE TRIGGER update_suspensions_updated_at_trigger
    BEFORE UPDATE ON user_suspensions
    FOR EACH ROW
    EXECUTE FUNCTION update_suspensions_updated_at();

-- 6. Ajouter des contraintes de vérification
ALTER TABLE user_suspensions
ADD CONSTRAINT check_suspension_dates CHECK (suspension_end_date > suspended_at);

ALTER TABLE user_suspensions
ADD CONSTRAINT check_rating_counts CHECK (
    zero_rating_count >= 0 AND low_rating_count >= 0
);

-- 7. Vérifier les tables créées
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('user_suspensions', 'rating_alerts');

-- 8. Afficher la structure des tables
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('user_suspensions', 'rating_alerts')
ORDER BY table_name, ordinal_position;

-- Message de confirmation
SELECT '✅ Migration suspensions terminée avec succès!' as message;
