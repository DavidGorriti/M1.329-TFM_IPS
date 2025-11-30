/**
 * Lista de objetos UserPosition.
 * @typedef {Object} UsersPositions
 * @property {number} systemTimestamp - Fecha/hora de la consulta al servicio.
 * @property {UserPosition[]} users - Lista de personas.
 */
export interface UsersPositions {
    systemTimestamp: number;
    users: UserPosition[];
}

/**
 * Información de una persona.
 * @typedef {Object} UserPosition
 * @property {number} systemTimestamp - Identificador de la persona.
 * @property {string} deviceName - Nombre del dispositivo.
 * @property {number} latitude - Latitud.
 * @property {number} longitude - Longitud.
 * @property {number} floorId - Planta.
 * @property {number} lastUpdateTimestamp - Fecha/hora de la última actualización de ubicación.
 * @property {number} lastUpdateInSeconds - Tiempo transcurrido entre la última actualización y la consulta al servicio.
 */
export interface UserPosition {
    userId: number;
    deviceName: string;
    latitude: number;
    longitude: number;
    floorId: number;
    lastUpdateTimestamp: number;
    lastUpdateInSeconds: number;
}