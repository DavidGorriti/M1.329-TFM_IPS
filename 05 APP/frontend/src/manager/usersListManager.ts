import {UserPosition} from "../model/userPositionsModels"
import { managers } from "./managers";

/**
 * Manejador encargado de gestionar la lista de personas en el DOM
 * @class UsersListManager
 */
export class UsersListManager {
    
    /**
     * Prefijo del identificador de la tarjeta de cada persona
     * @private
     */
    private idPrefix = 'ul-';
    /**
     * Lista de personas dentro del edificio
     * @private
     */
    private previousUsers: Number[] = [];

    /**
     * Objeto DOM que contiene la lista de personas
     * @private
     */
    private container: HTMLElement | null;
    /**
     * Objeto DOM que contiene la cabecera de la lista de personas
     * @private
     */
    private containerHeader: HTMLElement | null;
    
    /**
    * Crea una nueva instancia de UsersListManager.
    * @constructor
    * @param {string} containerId - Identificador del objeto DOM que contiene la lista de personas.
    */
    constructor(containerId: string) {
        this.container = document.getElementById(containerId);
        this.containerHeader = document.getElementById(containerId + '-header');
    }

    /**
     * Actualiza el objeto DOM con la lista de personas.
     * @param {UserPosition[]} users: Lista de posiciones de personas
     */
    updateUsersList(users: UserPosition[]) {
        if (!this.container || !this.containerHeader) return;

        // Actualizar título
        this.containerHeader.getElementsByTagName('span')[0].innerHTML = `Personas: ${users.length}`;

        // Actualizar personas
        const currentUsersIds = this.updateUsersInfo(users);
        this.removeUsersInfo(currentUsersIds);
        this.previousUsers = [...currentUsersIds];
        
        // Si no hay personas
        if (users.length === 0) {
            this.container.innerHTML = `
                <p id="${this.idPrefix}-nodata" class="text-muted text-center mt-3">
                    No hay Personas conectadas.
                </p>`;
        } else {
            const child = this.container.querySelector(`#${this.idPrefix}-nodata`);
            if (child)
                this.container.removeChild(child);
        }

    }

    /**
     * Selecciona una tarjeta de la lista de personas.
     * @param {number} userId: Identificador de la persona
     */
    selectUserCard(userId: number) {
        if (this.container) {
            const divId = this.getUserCardId(userId);
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
     * Actualiza el DOM de la lista de personas creando o actualizando la información de las tarjetas
     * y devuelve una lista con el identificador de las personas.
     * @param {UserPosition[]} users: Lista de posiciones de personas
     * @returns {Number[]}
     * @private
     */
    private updateUsersInfo(users: UserPosition[]): Number[] {
        const currentUsersIds: Number[] = [];
        // Crear o actualizar elementos
        users.forEach(user => {
            if (this.container) {
                let addToContainer = false;
                currentUsersIds.push(user.userId);
                const divId = this.getUserCardId(user.userId);
                let item = this.container.querySelector(`#${divId}`);
                if (!item) {
                    item = document.createElement("div");
                    item.id = divId;
                    item.className = "user-card my-1 p-2 border-bottom";
                    item.addEventListener("click", () => {
                        managers.userSelected(user.userId);
                    });
                    addToContainer = true;
                }

                item.innerHTML = `
                    <div class="fw-bold">${user.deviceName}</div>
                    <div class="small">Planta: <strong>${user.floorId ?? "-"}</strong></div>
                    <div class="small text-muted">Última actualización hace ${user.lastUpdateInSeconds.toFixed(3)} s</div>
                `;
                if (addToContainer)
                    this.container.appendChild(item);
            }
        });

        return currentUsersIds;
    }

    /**
     * Borra las tarjetas de las personas que ya no se encuentran en el edificio
     * @param {Number[]} currentUsersIds: Lista de identificadores de personas dentro del edificio
     * @private
     */
    private removeUsersInfo(currentUsersIds: Number[]) {
        // Borra las personas que no están en el edificio
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
     * Devuelve el identificador de la tarjeta de una personas
     * @param {Number} userId: Identificador de la persona
     * @private
     */
    private getUserCardId(userId: number) {
        return this.idPrefix + String(userId);
    }
}
