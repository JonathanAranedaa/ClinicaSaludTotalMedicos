import { getPacientesController } from "../controllers/paciente.controller.js";

import { Router } from "express";

const router = Router();


// Rutas para Paciente
router.get("/", getPacientesController);

export default router;