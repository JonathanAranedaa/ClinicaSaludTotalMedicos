import { sendEmailCita, sendEmailUpdateCita } from "../libs/resend.js";
import {
    createCitaModel,
    getCitaByIdCitaModel,
    getCitaByTokenModel,
    getCitasModel,
    updateCitaModel,
    updateStateCitaCancelModel,
    updateStateCitaConfirmModel,
    getCitasPacienteByRut,
    getInfoForCitaMedico,
    getInfoForCitaPaciente,
} from "../models/citas.model.js";
import { v4 } from "uuid"; // Para generar el token de la cita...
import { pool } from '../db.js';
// import { parse } from 'date-fns';

export const createCita = async (req, res) => {
    const { fecha, horaInicio, horaTermino, correo, rutMedico, rutPaciente } = req.body;
    // Crear token para la verificación de la cita
    const token = v4();
    // Obtener los datos necesarios para crear la cita
    const medico = await getInfoForCitaMedico(rutMedico);
    const paciente = await getInfoForCitaPaciente(rutPaciente);

    // const fechaHoraInicioStr = `${fecha} ${horaInicio}`;
    // const fechaHoraTerminoStr = `${fecha} ${horaTermino}`;

    // // PARSEAR las fechas y horas a objetos Date
    // const horaCitaInicio = parse(fechaHoraInicioStr, 'dd/MM/yyyy HH:mm', new Date());
    // const horaCitaTermino = parse(fechaHoraTerminoStr, 'dd/MM/yyyy HH:mm', new Date());
    // const fechaSQL = horaCitaInicio.toISOString().split('T')[0];

    // Guardar en la base de datos
    const saveCita = await createCitaModel({
        token,
        fecha: fecha,
        horaInicio: horaInicio,
        horaTermino: horaTermino,
        id_paciente: paciente.id_paciente,
        id_medico: medico.id_medico
    });
    // Objeto con el contenido del correo
    const dataCorreo = {
        fecha: fecha,
        hora: horaInicio,
        nombre_medico: medico.nombre + " " + medico.ap_paterno + " " + medico.ap_materno,
        especialidad: medico.nom_espe,
        nombre_paciente: paciente.nombre + " " + paciente.ap_paterno + " " + paciente.ap_materno,
        correo: correo,
        token: token,
    }
    // Enviar correo al usuario con la información de la cita
    await sendEmailCita(dataCorreo);
    // Enviar respuesta al cliente
    res.status(200).json({
        message: "Cita creada y correo enviado correctamente",
        data: saveCita,
    });
}

export const confirmCita = async (req, res) => {
    const { token } = req.query;
    // Buscar el token de la cita en la base de datos
    const cita = await updateStateCitaConfirmModel(token);
    // Enviar respuesta al cliente con el estado de la cita
    res.status(200).json({
        message: "Cita confirmada correctamente",
        data: cita,
    });
}

export const cancelCita = async (req, res) => {
    const { token } = req.query;
    // Buscar el token de la cita en la base de datos
    const cita = await updateStateCitaCancelModel(token);
    // Enviar respuesta al cliente con el estado de la cita
    res.status(200).json({
        message: "Cita cancelada correctamente",
        data: cita,
    });
}

export const getCitas = async (req, res) => {
    // Obtener todas las citas de la base de datos
    const citas = await getCitasModel();
    // Enviar respuesta al cliente con la lista de citas
    if (citas.length === 0) {
        return res.status(404).json({
            message: "No se encontraron citas",
        });
    }
    res.status(200).json(citas);
}

export const getCitasByRut = async (req, res) => {
    const { rut } = req.params;
    // Obtener el paciente por rut
    const citas = await getCitasPacienteByRut(rut);
    if (citas.length === 0) {
        return res.status(404).json({
            message: "No se encontraron citas para el rut proporcionado",
        });
    }
    res.status(200).json(citas);
}

export const getCitaById = async (req, res) => {
    const { id_cita } = req.params;
    // Obtener la cita por id
    const cita = await getCitaByIdCitaModel(id_cita);
    // Enviar respuesta al cliente con la cita
    res.status(200).json(cita);
}

export const getCitaByToken = async (req, res) => {
    try {
        const { token } = req.params;
        const cita = await getCitaByTokenModel(token);
        if (!cita) {
            return res.status(404).json({
                message: "Cita no encontrada"
            });
        }
        res.status(200).json(cita);
    } catch (error) {
        console.error('Error al obtener cita:', error);
        res.status(500).json({
            message: 'Error interno del servidor'
        });
    }
};

export const updateCita = async (req, res) => {
    const { id_cita } = req.params;
    const { fecha, horaInicio, horaTermino, correo, rutMedico, rutPaciente, motivo } = req.body;
    // Obtener los datos necesarios para crear la cita
    const medico = await getInfoForCitaMedico(rutMedico);
    const paciente = await getInfoForCitaPaciente(rutPaciente);
    const cita = await getCitaByIdCitaModel(id_cita);

    // const fechaHoraInicioStr = `${fecha} ${horaInicio}`;
    // const fechaHoraTerminoStr = `${fecha} ${horaTermino}`;

    // // PARSEAR las fechas y horas a objetos Date
    // const horaCitaInicio = parse(fechaHoraInicioStr, 'dd/MM/yyyy HH:mm', new Date());
    // const horaCitaTermino = parse(fechaHoraTerminoStr, 'dd/MM/yyyy HH:mm', new Date());
    // const fechaSQL = horaCitaInicio.toISOString().split('T')[0];

    const updateCita = await updateCitaModel({
        fecha: fecha,
        horaInicio: horaInicio,
        horaTermino: horaTermino,
        id_medico: medico.id_medico, 
        motivo, 
        id_paciente: paciente.id_paciente, 
        id_cita
    });

    // Obtener la cita actualizada
    const dataCorreo = {
        fecha: fecha,
        hora: horaInicio,
        nombre_medico: medico.nombre + " " + medico.ap_paterno + " " + medico.ap_materno,
        especialidad: medico.nom_espe,
        nombre_paciente: paciente.nombre + " " + paciente.ap_paterno + " " + paciente.ap_materno,
        correo: correo,
        token: cita.token_cita,
    }
    // Enviar correo al paciente con la información de la cita actualizada
    await sendEmailUpdateCita(dataCorreo);
    // Enviar respuesta al cliente con la cita actualizada
    res.status(200).json({
        message: "Cita actualizada correctamente",
        data: updateCita,
    });
}

export const getCitasByMedico = async (req, res) => {
    try {
        const { id_medico } = req.params;
        const { fecha } = req.query;
        
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
                es.estado as estado_cita,
                ci.motivo_cita
            FROM citas ci
            JOIN medicos md ON ci.id_medico = md.id_medico
            JOIN usuarios um ON md.id_usuario = um.id_usuario
            JOIN especialidades esp ON md.id_especialidad = esp.id_especialidad
            JOIN pacientes pc ON ci.id_paciente = pc.id_paciente
            JOIN usuarios up ON pc.id_usuario = up.id_usuario
            JOIN estados es ON ci.id_estado = es.id_estado
            WHERE ci.id_medico = $1
            ${fecha ? 'AND ci.fec_en = $2' : ''}
            ORDER BY ci.hora_cita_inicio;
        `;
        
        const params = [id_medico];
        if (fecha) params.push(fecha);
        
        const result = await pool.query(query, params);
        
        // Formatear las fechas antes de enviar
        const citasFormateadas = result.rows.map(cita => ({
            ...cita,
            fec_en: cita.fec_en ? cita.fec_en.toISOString() : 'Sin fecha',
            hora_cita_inicio: cita.hora_cita_inicio ? cita.hora_cita_inicio.toISOString() : 'Sin hora',
            estado: cita.estado_cita
        }));

        res.status(200).json(citasFormateadas);
    } catch (error) {
        console.error('Error al obtener citas por médico:', error);
        res.status(500).json({
            message: 'Error interno del servidor'
        });
    }
};
