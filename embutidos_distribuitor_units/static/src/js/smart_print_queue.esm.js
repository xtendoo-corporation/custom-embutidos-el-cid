import {registry} from "@web/core/registry";

/**
 * Lanza una lista de acciones de informe una detrás de otra (cola de impresión).
 * Cada informe pasa por los handlers de impresión (p. ej. QZ Tray) y se espera
 * a que termine antes de lanzar el siguiente.
 */
async function embutidosPrintQueue(env, action) {
    for (const job of action.params.jobs) {
        await env.services.action.doAction(job);
    }
}

registry.category("actions").add("embutidos_print_queue", embutidosPrintQueue);
