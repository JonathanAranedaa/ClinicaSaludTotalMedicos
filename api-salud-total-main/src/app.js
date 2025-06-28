//Lbrary imports
import express from 'express';
import morgan from 'morgan';
import cors from 'cors';
import cookieParser from 'cookie-parser';
import { rateLimit } from 'express-rate-limit';


//Import routes
import especialidadRoutes from './routes/especialidad.routes.js';
import medicoRoutes from './routes/medico.routes.js';
import pacienteRoutes from './routes/paciente.routes.js';
import citaRoutes from './routes/cita.routes.js';

const app = express();

//Rate limiting middleware
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 500,
    message: "Demasiadas peticiones desde esta IP, por favor intente más tarde",
    standardHeaders: true,
    legacyHeaders: false,
});

// Middlewares
app.use(cors({
    origin: ['https://nicodia.dev',
        'http://localhost:4200',
        'http://127.0.0.1:5000',
        '*'],
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
}));
app.use(morgan('dev'));
app.use(cookieParser());
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.set('view engine', 'ejs');
app.set('views', './src/views'); // necesario para renderizar vistas con EJS ya que no toma la carpeta src por defecto

//Routes
app.use('/', limiter);
app.use('/especialidades', limiter, especialidadRoutes);
app.use('/medicos', limiter, medicoRoutes);
app.use('/pacientes', limiter, pacienteRoutes);
app.use('/citas', citaRoutes);

//Route that returns a message in /
app.get('/', (req, res) => {
    res.render('index', {name: 'API de Gestión de Citas Médicas'});
});

//Error handling
app.use((err, req, res, next) => {
    res.status(500).json({
        "message": "Algo salió mal",
        "error": err.message
    });
});

export default app;