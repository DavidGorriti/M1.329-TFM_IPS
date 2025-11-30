import {UserPositionServiceConfig} from "../core/appConfig";
import {UsersPositions} from "../model/userPositionsModels"

/**
 * Servicio encargado de obtener periódicamente desde el backend las últimas 
 * posiciones conocidas de las personas y notificarla mediante un callback.
 * @class PositionUpdater
 */
export class PositionUpdater {
    /**
     * Identificador del intervalo activo.
     * @private
     */
    private intervalId: number | null = null;

    /**
     * URL del servicio que devuelve las posiciones.
     * @private
     */
    private getUsersPositionsUrl: string;

    /**
     * Función de callback que se ejecutará cada vez que se actualiza la fecha/hora.
     * @private
     */
    private callback: (usersPositions: UsersPositions) => void;

    
    /**
     * Crea una nueva instancia de PositionUpdater.
     * @constructor
     * @param {UserPositionServiceConfig} serviceConfig - Configuración del servicio de posiciones.
     * @param {(usersPositions: UsersPositions) => void} callback - Función de callback que se ejecutará cada vez que se actualizan las posiciones.
     */
    constructor(serviceConfig: UserPositionServiceConfig, callback: (usersPositions: UsersPositions) => void) {
        this.getUsersPositionsUrl = serviceConfig.getUsersPositionsUrl;
        this.callback = callback;
    }

    /**
    * Inicia el proceso periódico de obtención de posiciones.
    * @param {number} [intervalMilliseconds=1000] - Intervalo en milisegundos entre peticiones.
    */
    start(intervalMilliseconds: number = 1000) {
        if (this.intervalId) return;

        this.fetchAndUpdate();
        this.intervalId = window.setInterval(() => {
            this.fetchAndUpdate();
        }, intervalMilliseconds);
    }

    /**
    * Detiene el proceso periódico de obtención de posiciones.
    */
    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    /**
     * Realiza una petición al servicio de posiciones,
     * parsea la respuesta y llama al callback con las posiciones obtenida.
     * @private
     * @async
     * @returns {Promise<void>}
     *
     * @throws {Error} Lanza si la respuesta HTTP no es OK.
     */
    private async fetchAndUpdate() {
        try {
            const response = await fetch(this.getUsersPositionsUrl);
            if (!response.ok) throw new Error(`HTTP error ${response.status}`);
            const data: UsersPositions = await response.json() as UsersPositions;
            this.callback(data);
        } catch (err) {
            console.error("Error fetching user positions:", err);
        }
    }
}