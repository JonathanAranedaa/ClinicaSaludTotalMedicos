import { getMedico, getMedicoByRut, horarioMedico, getMedicoByIdEspecialidad } from "../models/medico.model.js";

export const getMedicoController = async (req, res, next) => {
    try {
        const result = await getMedico();
        res.json(result.rows);
    } catch (error) {
        res.status(404).json({
            message: 'No se encontraron médicos',
            error: error.message
        });
        next(error);
    }
}

export const getMedicoByRutController = async (req, res, next) => {
    const { rut } = req.params;
    try {
        const result = await getMedicoByRut(rut);
        res.json(result);
    } catch (error) {
        res.status(404).json({
            message: 'No se encontró el médico con el rut proporcionado',
            error: error.message
        });
        next(error);
    }
}

export const horarioMedicoController = async (req, res, next) => {
    const { id } = req.params;
    try {
        const result = await horarioMedico(id);
        res.json(result);
    } catch (error) {
        res.status(404).json({
            message: 'No se encontró el horario del médico con el id proporcionado',
            error: error.message
        });
        next(error);
    }
}

export const getMedicoByIdEspecialidadController = async (req, res, next) => {
    const { idEspecialidad } = req.params;
    try {
        const result = await getMedicoByIdEspecialidad(idEspecialidad);
        if (result.rowCount === 0) {
            return res.status(404).json({
                message: 'No se encontró el médico con la especialidad proporcionada'
            });
        }
        res.json(result);
    } catch (error) {
        res.status(404).json({
            message: 'No se encontró el médico con la especialidad proporcionada',
            error: error.message
        });
        next(error);
    }
}