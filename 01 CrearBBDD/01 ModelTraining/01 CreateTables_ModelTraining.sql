-- Crear esquema
CREATE SCHEMA IF NOT EXISTS tfm_ips;

-- Tabla: OriginalFile
CREATE TABLE IF NOT EXISTS tfm_ips.OriginalFile (
    Id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    FileName TEXT NOT NULL
);

-- Tabla: ReferencePointsPosition
CREATE TABLE IF NOT EXISTS tfm_ips.ReferencePointsPosition (
    Id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    OriginalFileId INTEGER NOT NULL,
    AppTimestamp NUMERIC(8,3) NOT NULL,
    Counter INTEGER NOT NULL,
    Latitude DOUBLE PRECISION NOT NULL,
    Longitude DOUBLE PRECISION NOT NULL,
    FloorId INTEGER NOT NULL,
    BuildingId INTEGER NOT NULL,
    CONSTRAINT fk_referencepointsposition_originalfile
        FOREIGN KEY (OriginalFileId)
        REFERENCES tfm_ips.OriginalFile (Id)
        ON DELETE CASCADE
);

-- Tabla: ReferencePointsWifi
CREATE TABLE IF NOT EXISTS tfm_ips.ReferencePointsWifi (
    Id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    OriginalFileId INTEGER NOT NULL,
    AppTimestamp NUMERIC(8,3) NOT NULL,
    SensorTimestamp NUMERIC(8,3) NOT NULL,
    Name_SSID TEXT NOT NULL,
    MAC_BSSID TEXT NOT NULL,
    Frequency INTEGER NOT NULL,
    RSS INTEGER NOT NULL,
    CONSTRAINT fk_referencepointswifi_originalfile
        FOREIGN KEY (OriginalFileId)
        REFERENCES tfm_ips.OriginalFile (Id)
        ON DELETE CASCADE
);

-- Tabla: ReferencePointsPositionWifi
CREATE TABLE IF NOT EXISTS tfm_ips.ReferencePointsPositionWifi (
    Id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    OriginalFileId INTEGER NOT NULL,
    PosiAppTimestamp NUMERIC(8,3) NOT NULL,
    WifiAppTimestamp NUMERIC(8,3) NOT NULL,
    MAC_BSSID TEXT NOT NULL,
    RSS INTEGER NOT NULL,
    Latitude DOUBLE PRECISION NOT NULL,
    Longitude DOUBLE PRECISION NOT NULL,
    ProjectedX DOUBLE PRECISION,
    ProjectedY DOUBLE PRECISION,
    FloorId INTEGER NOT NULL,
    CONSTRAINT fk_referencepointspositionwifi_originalfile
        FOREIGN KEY (OriginalFileId)
        REFERENCES tfm_ips.OriginalFile (Id)
        ON DELETE CASCADE
);

-- Crear índices
CREATE INDEX IF NOT EXISTS idx_rpp_originalfileid
    ON tfm_ips.ReferencePointsPosition (OriginalFileId);

CREATE INDEX IF NOT EXISTS idx_rpw_originalfileid
    ON tfm_ips.ReferencePointsWifi (OriginalFileId);
	
CREATE INDEX IF NOT EXISTS idx_rpp_apptimestamp
    ON tfm_ips.ReferencePointsPosition (AppTimestamp);

CREATE INDEX IF NOT EXISTS idx_rpw_apptimestamp
    ON tfm_ips.ReferencePointsWifi (AppTimestamp);

commit;