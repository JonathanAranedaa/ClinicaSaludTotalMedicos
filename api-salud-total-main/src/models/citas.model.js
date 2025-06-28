import { pool } from "../db.js";

export const createCitaModel = async (cita) => {
    const { token, fecha, hora_cita_inicio, hora_cita_termino, id_paciente, id_medico } = cita;
    const query = `
        INSERT INTO citas (fec_en, hora_cita_inicio, hora_cita_termino, motivo_cita, token_cita, id_medico, id_paciente, id_seguro, id_estado)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) RETURNING *;
    `;

    const result = await pool.query(query, [fecha, hora_cita_inicio, hora_cita_termino, " ", token, id_medico, id_paciente, 1, 1])
    if (result.rowCount === 0) {
        throw new Error("Error al crear la cita");
    }
    return result.rows[0];
}

export const getCitasModel = async () => {
    const query = `
        SELECT 
            ci.id_cita,
            ci.fec_en,
            ci.hora_cita_inicio,
            ci.hora_cita_termino,
            ci.token_cita,
            CONCAT(um.nombre, ' ', um.ap_paterno, ' ', um.ap_materno) as nombre_medico,
            esp.nom_espe as especialidad,
            CONCAT(up.nombre, ' ', up.ap_paterno, ' ', up.ap_materno) as nombre_paciente,
            es.estado
        FROM citas ci
        JOIN medicos md ON ci.id_medico = md.id_medico
        JOIN usuarios um ON md.id_usuario = um.id_usuario
        JOIN especialidades esp ON md.id_especialidad = esp.id_especialidad
        JOIN pacientes pc ON ci.id_paciente = pc.id_paciente
        JOIN usuarios up ON pc.id_usuario = up.id_usuario
        JOIN estados es ON ci.id_estado = es.id_estado;
    `;
    const result = await pool.query(query);
    return result.rows;
}

export const updateStateCitaConfirmModel = async (token_cita) => {
    const result = await pool.query("UPDATE citas SET id_estado = $1 WHERE token_cita = $2 RETURNING *;", [2, token_cita]);
    if (result.rowCount === 0) {
        throw new Error("Error al actualizar el estado de la cita");
    }
    return result.rows[0];
}

export const updateStateCitaCancelModel = async (token_cita) => {
    const result = await pool.query("UPDATE citas SET id_estado = $1 WHERE token_cita = $2 RETURNING *;", [3, token_cita]);
    if (result.rowCount === 0) {
        throw new Error("Error al actualizar el estado de la cita");
    }
    return result.rows[0];
}

export const getCitaByIdCitaModel = async (id_cita) => {
    const query = `
        SELECT id_cita, fec_en, hora_cita_inicio, hora_cita_termino, id_medico, token_cita
        FROM citas
        WHERE id_cita = $1;
    `;
    const result = await pool.query(query, [id_cita]);
    if (result.rowCount === 0) {
        throw new Error("No se encontraron citas para el id proporcionado");
    }
    return result.rows[0];
}

export const getCitaByTokenModel = async (token) => {
    const query = `
        SELECT 
            ci.id_cita,
            ci.fec_en,
            ci.hora_cita_inicio,
            ci.hora_cita_termino,
            ci.token_cita,
            CONCAT(um.nombre, ' ', um.ap_paterno, ' ', um.ap_materno) as nombre_medico,
            esp.nom_espe as especialidad,
            CONCAT(up.nombre, ' ', up.ap_paterno, ' ', up.ap_materno) as nombre_paciente,
            es.estado
        FROM citas ci
        JOIN medicos md ON ci.id_medico = md.id_medico
        JOIN usuarios um ON md.id_usuario = um.id_usuario
        JOIN especialidades esp ON md.id_especialidad = esp.id_especialidad
        JOIN pacientes pc ON ci.id_paciente = pc.id_paciente
        JOIN usuarios up ON pc.id_usuario = up.id_usuario
        JOIN estados es ON ci.id_estado = es.id_estado
        WHERE ci.token_cita = $1;
    `;
    const result = await pool.query(query, [token]);
    return result.rows[0];
}

export const updateCitaModel = async (cita) => {
    const { fecha, hora_cita_inicio, hora_cita_termino, id_medico, motivo, id_paciente, id_cita } = cita;
    const query = `
        UPDATE citas SET fec_en = $1, hora_cita_inicio = $2, hora_cita_termino = $3, motivo_cita = $4, id_medico = $5, id_paciente = $6, id_estado = $7
        WHERE id_cita = $8 RETURNING *;
        `;
    const result = await pool.query(query, [fecha, hora_cita_inicio, hora_cita_termino, motivo, id_medico, id_paciente,1, id_cita]); // 1 es el id del estado "Pendiente"
    if (result.rowCount === 0) {
        throw new Error("Error al actualizar la cita");
    }
    return result.rows[0];
}

/// ------------------ Nuevo Módulo ------------------ ///

// Obtener las citas de un paciente según el rut
export const getCitasPacienteByRut = async (rut) => {
    const query = `
    SELECT ci.id_cita, ci.fec_en, ci.hora_cita_inicio, ci.hora_cita_termino, ci.id_medico, ci.token_cita
    FROM citas ci 
    JOIN pacientes pc ON (ci.id_paciente = pc.id_paciente)
    JOIN usuarios us ON (us.id_usuario = pc.id_usuario)
    WHERE us.rut = $1 AND ci.id_estado = $2;
    `;
    const result = await pool.query(query, [rut, 1]);
    return result.rows;
}


export const getInfoForCitaMedico = async (rutMedico) => {
    const query = `
    SELECT md.id_medico, us.nombre, us.ap_paterno, us.ap_materno, esp.nom_espe
    FROM usuarios us 
    JOIN medicos md ON(us.id_usuario = md.id_usuario)
    JOIN especialidades esp ON(md.id_especialidad = esp.id_especialidad)
    WHERE us.rut = $1;
    `
    const result = await pool.query(query, [rutMedico]);
    if (result.rowCount === 0) {
        throw new Error("No se encontraron resultados");
    }
    return result.rows[0];
}

export const getInfoForCitaPaciente = async (rutPaciente) => {
    const query = `
    SELECT pc.id_paciente, us.nombre, us.ap_paterno, us.ap_materno
    FROM usuarios us 
    JOIN pacientes pc ON(us.id_usuario = pc.id_usuario)
    WHERE us.rut = $1;
    `
    const result = await pool.query(query, [rutPaciente]);
    if (result.rowCount === 0) {
        throw new Error("No se encontraron resultados");
    }
    return result.rows[0];
}