import {managers} from "./managers";
import {UserPositionServiceConfig} from "../core/appConfig";
import {UserPosition} from "../model/userPositionsModels";

/**
 * Alerta asociada a una persona.
 * @typedef {Object} Warning
 * @property {number} userId - Identificador del usuario.
 * @property {string} message - Mensaje de alerta.
 */
export interface Warning {
    userId: number;
    message: string;
}

/**
 * Manejador encargado de gestionar la lista de alertas en el DOM
 * @class UsersListManager
 */
export class WarningsListManager {

    /**
     * Prefijo del identificador de la tarjeta de cada alerta
     * @private
     */
    private idPrefix = 'uw-';
    /**
     * Lista de personas dentro del edificio
     * @private
     */
    private previousUsers: Number[] = [];
    /**
     * Configuración del servicio de obtención de posiciones
     * @private
     */
    private serviceConfig: UserPositionServiceConfig;

    /**
     * Objeto DOM que contiene la lista de alertas
     * @private
     */
    private container: HTMLElement | null;
    /**
     * Objeto DOM que contiene la cabecera de la lista de alertas
     * @private
     */
    private containerHeader: HTMLElement | null;
    
    /**
    * Crea una nueva instancia de WarningsListManager.
    * @constructor
    * @param {UserPositionServiceConfig} serviceConfig - Configuración del servicio de obtención de posiciones.
    * @param {string} containerId - Identificador del objeto DOM que contiene la lista de alertas.
    */
    constructor(serviceConfig: UserPositionServiceConfig, containerId: string) {
        this.serviceConfig = serviceConfig;
        this.container = document.getElementById(containerId);
        this.containerHeader = document.getElementById(containerId + '-header');
    }

    /**
     * Actualiza el objeto DOM con la lista de alertas.
     * @param {UserPosition[]} users: Lista de posiciones de personas
     */
    updateWarningsList(users: UserPosition[]) {
        if (!this.container || !this.containerHeader) return;

        const warnings = this.getWarnings(users);

        // Actualizar título
        this.containerHeader.getElementsByTagName('span')[0].innerHTML = `Alertas: ${warnings.length}`;

        // Actualizar avisos
        const currentUsersIds = this.updateWarnignsInfo(warnings);
        this.removeWarningsInfo(currentUsersIds);
        this.previousUsers = [...currentUsersIds];

        // Si no hay warnings
        if (warnings.length === 0) {
            this.container.innerHTML = `
                <p id="${this.idPrefix}nodata" class="text-muted text-center mt-3">
                    No hay alertas.
                </p>`;
            this.containerHeader.classList.add('bg-danger-subtle');
            this.containerHeader.classList.remove('bg-danger');
            this.containerHeader.style.color = '';
        } else {
            this.containerHeader.classList.remove('bg-danger-subtle');
            this.containerHeader.classList.add('bg-danger');
            this.containerHeader.style.color = 'white';
            const child = this.container.querySelector(`#${this.idPrefix}nodata`);
            if (child)
                this.container.removeChild(child);
        }
    }

    /**
     * Selecciona una tarjeta de la lista de alertas.
     * @param {number} userId: Identificador de la persona
     */
    selectWarningCard(userId: number) {
        if (this.container) {
            const divId = this.getWarningCardId(userId);
            for (const child of this.container.children) {
                if (child.id == divId) {
                    child.classList.add('selected');
                    child.scrollIntoView({
                        behavior: "smooth",
                        block: "start" 
                    });
                } else {
                    child.classList.remove('selected');
                }
            }
        }
    }

    /**
     * Devuelve todas las alertas
     * @param {UserPosition[]} users: Lista de personas
     * @returns {Warning[]}
     * @private
     */
    private getWarnings(users: UserPosition[]): Warning[] {
        let warnings: Warning[] = [];

        users.forEach(user => {
            if (user.lastUpdateInSeconds > this.serviceConfig.maxUpdateElapsedTime) {
                let warning: Warning = {
                    userId: user.userId,
                    message: `<div><span class="fw-bold">${user.deviceName}: </span>
                    <span class="small text-muted">Última actualización hace: ${user.lastUpdateInSeconds.toFixed(3)} s</span></div>`
                };
                warnings.push(warning);
            }
        });

        return warnings;
    }

    /**
     * Actualiza el DOM de la lista de alertas creando o actualizando la información de las tarjetas
     * y devuelve una lista con el identificador de las personas.
     * @param {Warning[]} warnings: Lista de alertas
     * @returns {Number[]}
     * @private
     */
    private updateWarnignsInfo(warnings: Warning[]): Number[] {
        const currentUsersIds: Number[] = [];
        // Crear o actualizar elementos
        warnings.forEach(warning => {
            if (this.container) {
                let addToContainer = false;
                currentUsersIds.push(warning.userId);
                const divId = this.getWarningCardId(warning.userId);
                let item = this.container.querySelector(`#${divId}`);
                if (!item) {
                    item = document.createElement("div");
                    item.id = divId;
                    item.className = "warning-card my-1 p-2 border-bottom";
                    item.addEventListener("click", () => {
                        managers.userSelected(warning.userId);
                    });
                    addToContainer = true;
                }

                item.innerHTML = warning.message;
                if (addToContainer)
                    this.container.appendChild(item);
            }
        });

        return currentUsersIds;
    }

    /**
     * Borra las tarjetas de las alertas que ya no son necesarias
     * @param {Number[]} currentUsersIds: Lista de identificadores de personas dentro del edificio
     * @private
     */
    private removeWarningsInfo(currentUsersIds: Number[]) {
        // Borra los warnigns de las personas que no están en el edificio
        const usersToDelete = this.previousUsers.filter(n => !currentUsersIds.includes(n));
        usersToDelete.forEach(userId => {
            if (this.container) {
                const child = this.container.querySelector(`#${this.idPrefix + String(userId)}`)
                if (child)
                    this.container.removeChild(child)
            }
        });
    }

    /**
     * Devuelve el identificador de la tarjeta de una alerta
     * @param {Number} userId: Identificador de la persona
     * @private
     */
    private getWarningCardId(userId: number) {
        return this.idPrefix + String(userId);
    }

}
