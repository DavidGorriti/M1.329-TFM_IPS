/**
 * Configuración general de la aplicación.
 * @typedef {Object} AppConfig
 * @property {MapConfig} map - Configuración del mapa.
 * @property {UserPositionServiceConfig} userPositionService - Configuración del servicio de posiciones de personas.
 * @property {CurrentDateTimeServiceConfig} currentDateTimeService - Configuración del servicio de fecha/hora actual.
 */
export interface AppConfig {
    map: MapConfig
    userPositionService: UserPositionServiceConfig
    currentDateTimeService: CurrentDateTimeServiceConfig
}

/**
 * Configuración del mapa.
 * @typedef {Object} MapConfig
 * @property {string} baseMap - URL del servicio de tiles de mapa base.
 * @property {[number, number]} center - Coordenadas iniciales del centro mapa [lat, lng].
 * @property {number} zoom - Zoom inicial.
 * @property {number} maxZoom - Zoom máximo permitido.
 * @property {number} minZoom - Zoom mínimo permitido.
 * @property {number} nativeMaxZoom - Zoom máximo de los tiles.
 * @property {[[number, number],[number, number]]} maxBounds - Límites máximos del mapa.
 * @property {string} attribution - Texto de la atribución del mapa.
 */
export interface MapConfig {
    baseMap: string;
    center: [number, number];
    zoom: number;
    maxZoom: number;
    minZoom: number,
    nativeMaxZoom: number;
    maxBounds: [
        [number, number],
        [number, number]
    ];
    attribution: string;
}

/**
 * Configuración del servicio que obtiene las posiciones de las personas.
 * @typedef {Object} UserPositionServiceConfig
 * @property {string} getUsersPositionsUrl - URL del servicio.
 * @property {number} updateInterval - Intervalo de actualización (ms).
 * @property {number} maxUpdateElapsedTime - Umbral para lanzar la alerta.
 */
export interface UserPositionServiceConfig {
    getUsersPositionsUrl: string;
    updateInterval: number;
    maxUpdateElapsedTime: number;
}

/**
 * Configuración del servicio que obtiene la fecha/hora actual.
 * @typedef {Object} CurrentDateTimeServiceConfig
 * @property {string} currentDateTimeUrl - URL del servicio.
 * @property {number} updateInterval - Intervalo de actualización (ms).
 * @property {number} maxUpdateElapsedTime - Umbral para lanzar la alerta.
 */
export interface CurrentDateTimeServiceConfig {
    currentDateTimeUrl: string;
    updateInterval: number;
    maxUpdateElapsedTime: number;
}

/**
 * Carga el archivo JSON de configuración y lo transforma en un objeto `AppConfig`.
 * @async
 * @function loadConfig
 * @param {string} file_path - Ruta al archivo JSON de configuración.
 * @returns {Promise<AppConfig>} Objeto de configuración parseado.
 * @throws {Error} Cuando el archivfo da error al cargarse.
 */
export async function loadConfig(file_path:string): Promise<AppConfig> {
    const response = await fetch(file_path);
    if (!response.ok) {
        throw new Error(`No se pudo cargar ${file_path}`);
    }
    return await response.json() as AppConfig;
}
