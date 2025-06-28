import { Router } from "express";
import { getAllEspecialidadesController, getEspecialidadByIdController } from "../controllers/especialidad.controller.js";



const router = Router();

//Rutas
router.get("/", getAllEspecialidadesController);
router.get("/:id", getEspecialidadByIdController);
export default router;