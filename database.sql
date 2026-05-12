
CREATE DATABASE IF NOT EXISTS geopermit_db;
USE geopermit_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Permit types table
CREATE TABLE IF NOT EXISTS permit_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    required_docs JSON
);

-- Hazard zones table (for GIS hazard validation)
CREATE TABLE IF NOT EXISTS hazard_zones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    hazard_type ENUM('flood', 'landslide', 'earthquake', 'fire') NOT NULL,
    center_lat DECIMAL(10, 8) NOT NULL,
    center_lng DECIMAL(11, 8) NOT NULL,
    radius_meters FLOAT NOT NULL,
    description TEXT
);

-- Permit applications table
CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    permit_type_id INT NOT NULL,
    project_title VARCHAR(200) NOT NULL,
    project_description TEXT,
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    location_address TEXT,
    is_hazard_zone BOOLEAN DEFAULT FALSE,
    hazard_info TEXT,
    status ENUM('pending', 'under_review', 'approved', 'rejected') DEFAULT 'pending',
    admin_remarks TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (permit_type_id) REFERENCES permit_types(id)
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
);

-- -----------------------------------------------
-- Seed data
-- -----------------------------------------------

-- Default admin account (password: admin123)
INSERT INTO users (full_name, email, password_hash, role) VALUES
('Admin User', 'admin@geopermit.gov', 'pbkdf2:sha256:600000$placeholder$hash', 'admin');

-- Permit types with required documents
INSERT INTO permit_types (name, description, required_docs) VALUES
('Tree Cutting Permit', 'Required for cutting or trimming trees in regulated areas.',
 '["Barangay Clearance", "Land Title or Tax Declaration", "Photo of Tree", "Site Map"]'),
('Building Permit', 'Required for construction of any structure.',
 '["Approved Building Plan", "Land Title", "Tax Clearance", "Environmental Compliance Certificate"]'),
('Excavation Permit', 'Required for any digging or excavation activity.',
 '["Site Plan", "Geological Assessment", "Barangay Clearance", "Contractor License"]'),
('Billboard/Signage Permit', 'Required for erecting billboards or large signage.',
 '["Structural Analysis", "Electrical Plan", "Lessor Consent", "Business Permit"]');

-- Sample hazard zones (Philippines-based coords)
INSERT INTO hazard_zones (name, hazard_type, center_lat, center_lng, radius_meters, description) VALUES
('Lahug River Flood Zone', 'flood', 10.3163, 123.8854, 1200, 'Lahug River area - prone to flooding during heavy rains'),
('Bulacao River Flood Zone', 'flood', 10.2741, 123.8520, 1500, 'Bulacao River valley - flash flood risk'),
('Calinog Valley Flood Zone', 'flood', 10.3847, 123.8945, 1000, 'Low-lying area prone to water buildup'),
('Tabu Protected Area', 'protected', 10.3200, 123.9200, 2000, 'Protected mangrove and marine sanctuary'),
('Sirao Flower Garden Protected', 'protected', 10.3500, 123.9100, 800, 'Protected garden and eco-tourism area'),
('Sambag Coastal Protected Area', 'protected', 10.2900, 123.8400, 1500, 'Coastal protection zone - no construction allowed'),
('Busay Heights Landslide Zone', 'landslide', 10.3600, 123.8700, 1500, 'Steep hillside area - landslide risk during rainy season'),
('Tops Heights Landslide Zone', 'landslide', 10.3450, 123.8650, 1200, 'Elevated area with unstable slopes'),
('Cebu Central Fault Zone', 'earthquake', 10.3167, 123.8833, 3000, 'Near active Cebu Central Fault line'),
('Busay Forest Fire Zone', 'fire', 10.3600, 123.8700, 2000, 'Forest area - high fire risk during dry season');


-- ── Mock Users ─────────────────────────────────────────
-- Password for all users below: User@1234
-- Password for admin: Admin@1234
-- (hashes generated via werkzeug generate_password_hash)

INSERT INTO users (full_name, email, password_hash, role) VALUES
(
  'Juan dela Cruz',
  'juan@email.com',
  'PASTE_HASH_HERE',
  'user'
),
(
  'Maria Santos',
  'maria@email.com',
  'PASTE_HASH_HERE',
  'user'
),
(
  'Pedro Reyes',
  'pedro@email.com',
  'PASTE_HASH_HERE',
  'user'
),
(
  'Admin User',
  'admin@geopermit.gov',
  'PASTE_HASH_HERE',
  'admin'
);