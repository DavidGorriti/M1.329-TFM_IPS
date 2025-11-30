import {DateUpdater} from "../api/dateUpdaterApi"
import {CurrentDateTimeServiceConfig} from "../core/appConfig";

/**
 * Manejador encargado de gestionar la fecha/hora actual y la fecha/hora de última actualización de las posiciones
 * y notificarla mediante un callback.
 * @class DateUpdater
 */
export class DatesManager {

    /**
     * Servicio de actualización de la fecha/hora actual.
     * @private
     */
    private dateUpdater: DateUpdater;
    /**
     * Configuración del servicio de obtención de fecha/hora actual 
     * @private
     */
    private serviceConfig: CurrentDateTimeServiceConfig;

    /**
     * Objeto DOM que contiene la fecha/hora actual
     * @private
     */
    private currentDateContainer: HTMLElement | null;

    /**
     * Objeto DOM que contiene la fecha/hora de última actualización
     * @private
     */
    private lastUpdateDateContainer: HTMLElement | null;

    /**
     * Objeto DOM que contiene la cabecera de fecha/hora de última actualización
     * @private
     */
    private lastUpdateDateContainerHeader: HTMLElement | null;

    /**
     * Fecha/hora de la última actualización de las posiciones
     * @private
     */
    private lastUpdateDate: Date;
    
    /**
     * Crea una nueva instancia de DatesManager.
     * @constructor
     * @param {CurrentDateTimeServiceConfig} serviceConfig - Configuración del servicio de fecha/hora.
     * @param {string} currentDateContainerId - Identificador del objeto DOM que contiene la fecha/hora actual.
     * @param {string} lastUpdateDateContainerId - Identificador del objeto DOM que contiene la fecha/hora de última actualización.
     */
    constructor(serviceConfig: CurrentDateTimeServiceConfig, currentDateContainerId: string, lastUpdateDateContainerId: string) {
        this.currentDateContainer = document.getElementById(currentDateContainerId);
        this.lastUpdateDateContainer = document.getElementById(lastUpdateDateContainerId);
        this.lastUpdateDateContainerHeader = document.getElementById(lastUpdateDateContainerId + '-header');
        
        this.serviceConfig = serviceConfig;
        
         this.dateUpdater = new DateUpdater(this.serviceConfig, (currentdate: Date) => {
            this.updateCurrentDate(currentdate);
            this.checkLastUpdateDate(currentdate);
        });
    }

    /**
     * Actualiza el objeto DOM con la fecha/hora de última actualización.
     * @param {Date} lastUpdateDate - Fecha/hora de última actualización
     */
    updateLastUpdateDate(lastUpdateDate: Date) {
        if (!this.lastUpdateDateContainer) return;

        // Actualiza la fecha
        this.lastUpdateDate = lastUpdateDate;
        this.lastUpdateDateContainer.innerHTML = this.getDateString(lastUpdateDate);

    }

    /**
     * Inicializa DateUpdater
     */
    start() {
        this.dateUpdater.start(this.serviceConfig.updateInterval);
    }

    /**
     * Detiene DateUpdater
     */
    stop() {
        this.dateUpdater.stop();
    }

    /**
     * Actualiza el objeto DOM con la fecha/hora actual.
     * @param {Date} currentdate - Fecha/hora actual.
     * @private
     */
    private updateCurrentDate(currentdate: Date) {
        if (!this.currentDateContainer) return;

        // Actualiza la fecha
        this.currentDateContainer.innerHTML = this.getDateString(currentdate);
    }

    /**
     * Compara la diferencia entre fecha/hora actual y de última actualización y actualiza la alerta.
     * @param {Date} currentdate - Fecha/hora actual.
     * @private
     */
    private checkLastUpdateDate(currentDate: Date) {
        if (!this.lastUpdateDateContainerHeader) return;

        if (this.lastUpdateDate && currentDate && ((currentDate.getTime() - this.lastUpdateDate.getTime())/1000) > this.serviceConfig.maxUpdateElapsedTime) {
            this.lastUpdateDateContainerHeader.classList.add('bg-danger');
            this.lastUpdateDateContainerHeader.style.color = 'white';
        } else {
            this.lastUpdateDateContainerHeader.classList.remove('bg-danger');
            this.lastUpdateDateContainerHeader.style.color = '';
        }
    }

    /**
     * Devuelve la fecha/hora en formato texto.
     * @param {Date} date - Fecha/hora.
     * @private
     */
    private getDateString(date: Date) {
        return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`
    }
}
