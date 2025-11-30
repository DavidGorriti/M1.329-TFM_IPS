import {CurrentDateTimeServiceConfig} from "../core/appConfig";

/**
 * Servicio encargado de obtener periódicamente la fecha/hora actual desde el backend
 * y notificarla mediante un callback.
 * @class DateUpdater
 */
export class DateUpdater {
    /**
     * Identificador del intervalo activo.
     * @private
     */
    private intervalId: number | null = null;

    /**
     * URL del servicio que devuelve la fecha/hora actual.
     * @private
     */
    private getCurrentDateUrl: string;

    /**
     * Función de callback que se ejecutará cada vez que se actualiza la fecha/hora.
     * @private
     */
    private callback: (currentDate: Date) => void;
    
    /**
     * Crea una nueva instancia de DateUpdater.
     * @constructor
     * @param {CurrentDateTimeServiceConfig} serviceConfig - Configuración del servicio de fecha/hora.
     * @param {(currentDate: Date) => void} callback - Función de callback que se ejecutará cada vez que se actualiza la fecha/hora.
     */
    constructor(serviceConfig: CurrentDateTimeServiceConfig, callback: (currentDate: Date) => void) {
        this.getCurrentDateUrl = serviceConfig.currentDateTimeUrl;
        this.callback = callback;
    }

     /**
     * Inicia el proceso periódico de obtención de la fecha/hora.
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
    * Detiene el proceso periódico de obtención de la fecha/hora.
    */
    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    /**
     * Realiza una petición al servicio de fecha/hora,
     * parsea la respuesta y llama al callback con la fecha obtenida.
     * @private
     * @async
     * @returns {Promise<void>}
     *
     * @throws {Error} Lanza si la respuesta HTTP no es OK.
     */
    private async fetchAndUpdate() {
        try {
            const response = await fetch(this.getCurrentDateUrl);
            if (!response.ok) throw new Error(`HTTP error ${response.status}`);
            const data = await response.json();
            this.callback(new Date(data));
        } catch (err) {
            console.error("Error fetching user positions:", err);
        }
    }
}