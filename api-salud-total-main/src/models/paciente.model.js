import { pool } from "../db.js";

export const getPacientes = async () => {
    const query = `
    SELECT pc.id_paciente, us.rut, us.nombre, us.ap_paterno, us.ap_materno, us.id_usuario
    FROM usuarios us JOIN pacientes pc ON (us.id_usuario = pc.id_usuario);
    `;
    const result = await pool.query(query);
    if (result.rows.length === 0) {
        throw new Error("No hay pacientes registrados");
    }
    return result.rows;
}