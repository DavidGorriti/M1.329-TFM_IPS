import {managers} from "./manager/managers"

managers.start();

// TODO Borrar, solo para desarrollar
(window as any).managers = managers;
