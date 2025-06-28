import { Router } from "express";
import { getMedicoController, getMedicoByRutController, horarioMedicoController, getMedicoByIdEspecialidadController } from "../controllers/medico.controller.js";

const router = Router();

router.get("/", getMedicoController)
router.get("/:rut", getMedicoByRutController)
router.get("/horario/:id", horarioMedicoController)
router.get("/especialidad/:idEspecialidad", getMedicoByIdEspecialidadController)

export default router;