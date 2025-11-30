import {PositionUpdater} from "../api/positionUpdaterApi"
import {UserPositionServiceConfig} from "../core/appConfig";
import {UsersPositions, UserPosition} from "../model/userPositionsModels";
import {managers} from "./managers"

/**
 * Manejador encargado de obtener las últimas posiciones conocias de las personas
 * y notificarla mediante un callback.
 * @class DateUpdater
 */
export class UsersManager {

    /**
     * Servicio de actualización de posiciones.
     * @private
     */
    private positionUpdater: PositionUpdater; 
    /**
     * Configuración del servicio de obtención de posiciones
     * @private
     */
    private serviceConfig: UserPositionServiceConfig;

    /**
     * Crea una nueva instancia de UsersManager.
     * @constructor
     * @param {CurrentDateTimeServiceConfig} serviceConfig - Configuración del servicio de fecha/hora.
     * @param {string} currentDateContainerId - Identificador del objeto DOM que contiene la fecha/hora actual.
     * @param {string} lastUpdateDateContainerId - Identificador del objeto DOM que contiene la fecha/hora de última actualización.
     */
    constructor(serviceConfig: UserPositionServiceConfig) {
        this.serviceConfig = serviceConfig;
        
         this.positionUpdater = new PositionUpdater(this.serviceConfig, (usersPositions: UsersPositions) => {
            managers.usersUpdated(usersPositions);
        });
    }

    /**
     * Inicializa PositionUpdater
     */
    start() {
        this.positionUpdater.start(this.serviceConfig.updateInterval);
    }

    /**
     * Detiene PositionUpdater
     */
    stop() {
        this.positionUpdater.stop();
    }
}