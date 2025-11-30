import {AppConfig, loadConfig} from "../core/appConfig";
import {MapManager} from "./mapManager";
import {UsersListManager} from "./usersListManager";
import {DatesManager} from "./datesManager";
import {WarningsListManager} from "./warningsListManager";
import {UsersManager} from "./usersManager";
import {UsersPositions} from "../model/userPositionsModels";

/**
 * Orquestador y punto de acceso de los manejadores.
 * @class Managers
 */
export class Managers {

    /**
     * Configuración de la aplicación 
     * @private
     */
    private appConfig: AppConfig;

    /**
     * Manejador de personas
     */
    usersManager: UsersManager; 
    /**
     * Manejador de lista de personas
     */
    usersListManager: UsersListManager;
    /**
     * Manejador de mapa
     */
    mapManager: MapManager;
    /**
     * Manejador de fechas
     */
    datesManager: DatesManager;
    /**
     * Manejador de lista de alertas
     */
    warningsListManager: WarningsListManager;

    /**
     * Crea una nueva instancia de Managers.
     * @constructor
     * @param {AppConfig} appConfig - Configuración de la aplicación.
     */
    constructor(appConfig: AppConfig) {
        this.appConfig = appConfig;
        this.mapManager = new MapManager(this.appConfig.map);
        this.datesManager = new DatesManager(this.appConfig.currentDateTimeService,'current-date','last-update-date');
        this.usersManager = new UsersManager(this.appConfig.userPositionService);
        this.usersListManager = new UsersListManager('users-list');
        this.warningsListManager = new WarningsListManager(this.appConfig.userPositionService,'warnings-list');
    }

    /**
     * Inicializa los manejadores.
     */
    start() {
        this.datesManager.start();
        this.usersManager.start();
    }

    /**
     * Detiene los manejadores.
     */
    stop() {
        this.datesManager.stop();
        this.usersManager.stop();
    }

    /**
     * Ejecuta la actualización de personas en todos los manejadores necesarios
     * @param {UsersPositions} usersPositions - Posiciones de las personas
     */
    usersUpdated(usersPositions: UsersPositions) {
        this.mapManager.updateUsersPositions(usersPositions.users);
        this.datesManager.updateLastUpdateDate(new Date(usersPositions.systemTimestamp));
        this.usersListManager.updateUsersList(usersPositions.users);
        this.warningsListManager.updateWarningsList(usersPositions.users);
    }

    /**
     * Ejecuta la selección de personas en todos los manejadores necesarios
     * @param {number} userId - Identificador de la persona seleccionada
     */
    userSelected(userId: number) {
        this.usersListManager.selectUserCard(userId);
        this.warningsListManager.selectWarningCard(userId);
        this.mapManager.selectUser(userId);
    }
}

const config = await loadConfig("/appConfig.json");
export const managers = new Managers(config)
