import { Router } from "express";
import {
    createCita,
    confirmCita,
    getCitas,
    cancelCita,
    getCitasByRut,
    updateCita,
    getCitaById,
    getCitaByToken,
    getCitasByMedico
} from "../controllers/cita.controller.js";

const router = Router();

router.get("/", getCitas);

router.get("/rut/:rut", getCitasByRut);

router.get("/id/:id_cita", getCitaById);

router.put("/actualizar/:id_cita", updateCita);

router.post("/create", createCita);

router.get("/medico/:id_medico", getCitasByMedico);

router.get("/:token", getCitaByToken);

router.get("/:token", getCitaByToken);

router.get("/confirmar/:token", confirmCita);

router.get("/cancelar/:token", cancelCita);


export default router;
