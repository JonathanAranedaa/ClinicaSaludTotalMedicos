import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);

export const sendEmailCita = async (datos) => {
    const { fecha, hora, nombre_medico, especialidad, token, nombre_paciente, correo } = datos;
    const textHTML = `
    <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reserva de cita médica</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 20px;
                }
                .container {
                    max-width: 600px;
                    margin: auto;
                    background: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }
                h1 {
                    color: #333;
                }
                p {
                    color: #555;
                }
                .button-container {
                    display: flex;
                    gap: 10px;
                    margin-top: 20px;
                }
                .button-link {
                    text-decoration: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    color: white;
                    font-weight: bold;
                    display: inline-block;
                }
                .confirm {
                    background-color: #4CAF50;
                }
                .cancel {
                    background-color: #f44336;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Reserva de cita médica</h1>
                <p>Hola, ${nombre_paciente}</p>
                <p>Gracias por reservar una cita médica con nosotros. A continuación, encontrarás los detalles de tu cita:</p>
                <ul>
                    <li><strong>Fecha:</strong> ${fecha}</li>
                    <li><strong>Hora:</strong> ${hora}</li>
                    <li><strong>Médico:</strong> ${nombre_medico}</li>
                    <li><strong>Especialidad:</strong> ${especialidad}</li>
                </ul>
                <p>Si tienes alguna pregunta o necesitas reprogramar tu cita, no dudes en contactarnos.</p>
                <p>Saludos,<br/>El equipo de Salud Total</p>

                <div class="button-container">
                    <a class="button-link confirm" href="http://localhost:4000/citas/confirmar?token=${token}">Confirmar Cita</a>
                    <a class="button-link cancel" href="http://localhost:4000/citas/cancelar?token=${token}">Cancelar Cita</a>
                </div>
            </div>
        </body>
    </html>
    `;
    // Enviar el correo electrónico
    try {
        const data = await resend.emails.send({
            from: "saludtotal@nicodia.dev",
            to: correo,
            subject: "Reserva de cita médica",
            html: textHTML
        })
        return data;
    }
    catch (error) {
        console.error("Error sending email:", error);
    }
}

export const sendEmailUpdateCita = async (datos) => {
    const { fecha, hora, nombre_medico, especialidad, token, nombre_paciente, correo } = datos;
    const textHTML = `
    <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reprogramación de cita médica</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 20px;
                }
                .container {
                    max-width: 600px;
                    margin: auto;
                    background: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }
                h1 {
                    color: #333;
                }
                p {
                    color: #555;
                }
                .button-container {
                    display: flex;
                    gap: 10px;
                    margin-top: 20px;
                }
                .button-link {
                    text-decoration: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    color: white;
                    font-weight: bold;
                    display: inline-block;
                }
                .confirm {
                    background-color: #4CAF50;
                }
                .cancel {
                    background-color: #f44336;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Reprogramación de cita médica</h1>
                <p>Hola, ${nombre_paciente}</p>
                <p>Tu cita médica ha sido reprogramada. A continuación, encontrarás los nuevos detalles de tu cita:</p>
                <ul>
                    <li><strong>Fecha:</strong> ${fecha}</li>
                    <li><strong>Hora:</strong> ${hora}</li>
                    <li><strong>Médico:</strong> ${nombre_medico}</li>
                    <li><strong>Especialidad:</strong> ${especialidad}</li>
                </ul>
                <p>Por favor, confirma si puedes asistir a la nueva fecha y hora o cancela si no te es posible.</p>
                <p>Saludos,<br/>El equipo de Salud Total</p>

                <div class="button-container">
                    <a class="button-link confirm" href="http://localhost:4000/citas/confirmar?token=${token}">Confirmar Nueva Cita</a>
                    <a class="button-link cancel" href="http://localhost:4000/citas/cancelar?token=${token}">Cancelar Cita</a>
                </div>
            </div>
        </body>
    </html>
    `;
    // Enviar el correo electrónico
    try {
        const data = await resend.emails.send({
            from: "saludtotal@nicodia.dev",
            to: correo,
            subject: "Reprogramación de cita médica",
            html: textHTML
        })
        return data
    }
    catch (error) {
        console.error("Error sending email:", error);
    }
}