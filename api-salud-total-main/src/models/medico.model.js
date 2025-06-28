import { pool } from '../db.js';

export const getMedico = async () => {
    const query = `
    SELECT md.id_medico, us.rut, us.correo, us.nombre, us.ap_paterno, us.ap_materno, md.id_especialidad
    FROM usuarios us
    JOIN medicos md ON (md.id_usuario = us.id_usuario)
    `;
    const result = await pool.query(query);
    return result;
};

export const getMedicoByRut = async (rut) => {
    const query = `
    SELECT md.id_medico, us.rut, us.correo, us.nombre, us.ap_paterno, us.ap_materno, md.id_especialidad
    FROM usuarios us
    JOIN medicos md ON (md.id_usuario = us.id_usuario)
    WHERE us.rut = $1;
    `;
    const result = await pool.query(query, [rut]);
    if (result.rowCount === 0) {
        throw new Error("Medico no encontrado");
    }
    return result.rows[0];
}

export const getMedicoByIdEspecialidad = async (idEspecialidad) => {
    const query = `
    SELECT md.id_medico, us.rut, us.correo, us.nombre, us.ap_paterno, us.ap_materno, md.id_especialidad
    FROM usuarios us 
    JOIN medicos md ON (md.id_usuario = us.id_usuario)
    WHERE md.id_especialidad = $1;
    `;
    const result = await pool.query(query, [idEspecialidad]);
    if (result.rowCount === 0) {
        throw new Error("Medico no encontrado");
    }
    return result.rows;
}

export const horarioMedico = async (id) => {
    const query = `
    SELECT hr.id_medico, dia_semana, hora_inicio, hora_salida
    FROM horarios hr 
    JOIN medicos md ON (hr.id_medico = md.id_medico)
    WHERE hr.id_medico = $1;
    `;
    const result = await pool.query(query, [id]);
    if (result.rowCount === 0) {
        throw new Error("Horario no encontrado");
    }
    return result.rows;
}