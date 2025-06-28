import { getPacientes } from "../models/paciente.model.js";

export const getPacientesController = async (req, res, next) => {
    try {
        const result = await getPacientes();
        res.json(result);
    } catch (error) {
        next(error);
        res.status(500).json({ message: "Error fetching data" });
    }
}