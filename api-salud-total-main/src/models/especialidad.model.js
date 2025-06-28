import { pool } from '../db.js';

export const getEspecialidades = async () => {
    const result = await pool.query('SELECT id_especialidad, nom_espe FROM especialidades');
    return result;
};

export const getEspecialidadById = async (id) => {
    const result = await pool.query('SELECT id_especialidad, nom_espe FROM especialidades WHERE id_especialidad = $1', [id]);
    return result.rows[0];
};