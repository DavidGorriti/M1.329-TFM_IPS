import * as L from "leaflet";
import "leaflet.vectorgrid";

import {MapConfig} from "../core/appConfig";
import {UserPosition} from "../model/userPositionsModels"
import {managers} from "./managers";

/**
 * Manejados encargado de gestionar el mapa.
 * @class MapManager
 */
export class MapManager {
    /**
     * Configuración del mapa
     * @private
     */
    private mapConfig: MapConfig;
    /**
     * Mapa Leaflet
     * @private
     */
    private allUsersMap: L.Map;
    /**
     * Capa Leaflet de ubicaciones de personas
     * @private
     */
    private usersLayer: L.GeoJSON;
    /**
     * Objeto Map de Markers de Leaflet con las ubicaciones
     * @private
     */
    private usersFeatures: Map<number, L.CircleMarker> = new Map();
    
    /**
     * Crea una nueva instancia de MapManager.
     * @constructor
     * @param {MapConfig} mapConfig - Configuración del mapa
     */
    constructor(mapConfig: MapConfig) {
        this.mapConfig = mapConfig;
        
        /// Inicializa mapa 
        this.allUsersMap = L.map("map-general", {
            center: this.mapConfig.center,
            zoom: this.mapConfig.zoom,
            maxZoom: this.mapConfig.maxZoom,
            minZoom: this.mapConfig.minZoom,
            maxBounds: this.mapConfig.maxBounds
        });
        this.getBaseLayer().addTo(this.allUsersMap);
        this.usersLayer = this.getUsersLayer();
        this.usersLayer.addTo(this.allUsersMap);
        this.getLegend().addTo(this.allUsersMap);
    }

    /**
     * Actualiza la ubicación y planta de las personas en el mapa.
     * @param {UserPosition[]} users - Lista de las ubicaciones de las personas.
     */
    updateUsersPositions(users: UserPosition[]) {
        const receivedIds = new Set<number>();

        for (const user of users) {
            receivedIds.add(user.userId);

            if (!this.usersFeatures.has(user.userId)) {
                // Crear GeoJSON Feature
                const feature = {
                    type: "Feature",
                    geometry: {
                        type: "Point",
                        coordinates: [user.longitude, user.latitude]
                    },
                    properties: {...user}
                } as const;

                this.usersLayer.addData(feature);

                // Obtener el último layer añadido
                const lastLayer = Object.values(this.usersLayer.getLayers()).pop() as L.CircleMarker;

                // Etiquetar con nombre de dispositivo
                lastLayer.bindTooltip(`${user.deviceName}`, {
                    permanent: false, 
                    direction: "top",
                    className: "user-id-label"
                });

                lastLayer.bindPopup(
                    `<div class="popup-user">
                        ${user.deviceName}
                    </div>`
                );

                this.usersFeatures.set(user.userId, lastLayer);

            } else {
                // Actualizar posición
                const marker = this.usersFeatures.get(user.userId)!;
                marker.setLatLng([user.latitude, user.longitude]);
                const color = this.getColorForFloor(user.floorId);
                marker.setStyle({
                    color: color.border,
                    fillColor: color.fill
                });
            }
        }

        // Eliminar personas que han salido del edificio
        for (const id of [...this.usersFeatures.keys()]) {
            if (!receivedIds.has(id)) {
                const marker = this.usersFeatures.get(id)!;
                this.usersLayer.removeLayer(marker);
                this.usersFeatures.delete(id);
            }
        }

    }
    
    /**
     * Selecciona el marcador del mapa
     * @param {number} userId - Identificador de la persona.
     */
    selectUser(userId: number) {
        this.resetSelection();
        const marker = this.usersFeatures.get(userId);
        if (marker) {
            this.allUsersMap.panTo(marker.getLatLng(), {
                animate: true,
                duration: 0.2
            });
            const size = this.getSelectedSize();
            marker.setStyle({
                radius: size.radius,
                weight: size.weight
            });
            // Abrir popup tras desplazar el mapa
            setTimeout(() => {
                marker.openPopup();
            }, 200); 
        }
    }

    /**
     * Crea el mapa base
     * @returns {L.TileLayer}
     */
    private getBaseLayer(): L.TileLayer {
        return L.tileLayer(this.mapConfig.baseMap, {
            attribution: this.mapConfig.attribution,
            maxZoom: this.mapConfig.maxZoom,
            maxNativeZoom: this.mapConfig.nativeMaxZoom
        });
    }

    /**
     * Crea la capa de posiciones de personas
     * @returns {L.GeoJSON}
     */
    private getUsersLayer(): L.GeoJSON {
        return L.geoJSON([], {
            pointToLayer: (feature, latlng) => {
                const floorId = feature.properties.floorId;
                const color = this.getColorForFloor(floorId);
                const size = this.getUnselectedSize();

                const marker = L.circleMarker(latlng, {
                    radius: size.radius,
                    color: color.border,
                    weight: size.weight,
                    fillColor: color.fill,
                    fillOpacity: 0.8
                });

                marker.on("click", () => {
                    managers.userSelected(feature.properties.userId);
                });

                return marker;
            }
        });
    }

    /**
     * Crea la leyenda del mapa
     * @returns {L.Control}
     */
    private getLegend(): L.Control {
        const legend = new L.Control();

        legend.onAdd = () => {
            const div = L.DomUtil.create("div", "map-legend");
    
            div.innerHTML = `
                <div class="legend-title mb-2">Plantas</div>
                <div class="pb-1"><i style="background:${this.getColorForFloor(0).fill}"></i> Planta 0</div>
                <div class="pb-1"><i style="background:${this.getColorForFloor(-1).fill}"></i> Planta -1</div>
                <div class="pb-1"><i style="background:${this.getColorForFloor(-2).fill}"></i> Planta -2</div>
            `;
    
            return div;
        };

        return legend;
    }

    /**
     * Deselecciona los marcadores del mapa
     */
    private resetSelection() {
        const size = this.getUnselectedSize();
        this.usersFeatures.forEach(marker => {
            marker.closePopup();
            marker.setStyle({
                radius: size.radius,
                weight: size.weight
            });
        });
    }

    /**
     * Devuelve el color del marcador en función de la planta
     * @param {number} floorId - Identificador de la planta.
     * @returns {border: string; fill: string}
     */
    private getColorForFloor(floorId: number): {border: string; fill: string} {
        switch (floorId) {
            case 0:
                return { border: "#0D47A1", fill: "#1976D2" };
            case -1:
                return { border: "#1B5E20", fill: "#4CAF50" };
            case -2:
                return { border: "#B71C1C", fill: "#E53935" };
            default:
                return { border: "#000000", fill: "#000000" };
        }
    }

    /**
     * Devuelve el tamaño del marcador seleccionado
     * @returns {radius: number; weight: number} 
     */
    private getSelectedSize(): {radius: number; weight: number} {
        return {
            radius: 10,
            weight: 3
        }
    }

    /**
     * Devuelve el tamaño del marcador no seleccionado
     * @returns {radius: number; weight: number} 
     */
    private getUnselectedSize(): {radius: number; weight: number} {
        return {
            radius: 6,
            weight: 1
        }
    }

}