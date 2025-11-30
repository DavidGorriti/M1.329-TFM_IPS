-- Crear esquema
CREATE SCHEMA IF NOT EXISTS tfm_ips;

-- Tabla: OriginalFile
CREATE TABLE IF NOT EXISTS tfm_ips.User (
    Id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    DeviceName TEXT NOT NULL
);

-- Tabla: UserWifi
CREATE TABLE IF NOT EXISTS tfm_ips.UserWifi (
    Id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    UserId INTEGER NOT NULL,
    SystemTimestamp Timestamptz NOT NULL,
    MAC_BSSID TEXT NOT NULL,
    RSS INTEGER NOT NULL,
    CONSTRAINT fk_UserWifi_User
        FOREIGN KEY (UserId)
        REFERENCES tfm_ips.User (Id)
        ON DELETE CASCADE
);

-- Tabla: UserPosition
CREATE TABLE IF NOT EXISTS tfm_ips.UserPosition (
    Id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    UserId INTEGER NOT NULL,
    SystemTimestamp Timestamptz NOT NULL,
    Latitude DOUBLE PRECISION NOT NULL,
    Longitude DOUBLE PRECISION NOT NULL,
    FloorId INTEGER NOT NULL,
    CONSTRAINT fk_UserPosition_User
        FOREIGN KEY (UserId)
        REFERENCES tfm_ips.User (Id)
        ON DELETE CASCADE
);

-- Crear índices
CREATE INDEX IF NOT EXISTS idx_uw_userid
    ON tfm_ips.UserWifi (UserId);

CREATE INDEX IF NOT EXISTS idx_up_userid
    ON tfm_ips.UserPosition (UserId);
	
CREATE INDEX IF NOT EXISTS idx_rpp_systemptimestamp
    ON tfm_ips.UserPosition (SystemTimestamp);

commit;