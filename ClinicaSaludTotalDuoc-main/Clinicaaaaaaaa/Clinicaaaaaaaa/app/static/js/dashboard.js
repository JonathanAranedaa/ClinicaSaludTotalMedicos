// Función para manejar la generación automática de correo y contraseña
function initMedicoForm() {
    // Generar contraseña cuando cambia el RUT
    const rutInput = document.querySelector('input[name="rut"]');
    const contrasenaInput = document.querySelector('input[name="contrasena"]');
    
    // Prevenir entrada de puntos en el RUT
    rutInput.addEventListener('keydown', function(event) {
        if (event.key === '.') {
            event.preventDefault();
        }
    });

    rutInput.addEventListener('input', function() {
        // Eliminar puntos si existen
        rutInput.value = rutInput.value.replace(/[.]/g, '');
        
        const rut = rutInput.value;
        // Eliminar el dígito verificador (últimos 2 caracteres)
        const rutSinDv = rut.length > 2 ? rut.slice(0, -2) : rut;
        contrasenaInput.value = rutSinDv;
    });

    // Generar correo cuando cambian nombre y apellido paterno
    const nombreInput = document.querySelector('input[name="nombre"]');
    const apPaternoInput = document.querySelector('input[name="apPaterno"]');
    const apMaternoInput = document.querySelector('input[name="apMaterno"]');
    const correoInput = document.querySelector('input[name="correo"]');

    function generarCorreo() {
        const nombre = nombreInput.value;
        const apPaterno = apPaternoInput.value;
        const apMaterno = apMaternoInput.value;
        
        if (nombre && apPaterno) {
            const nombrePart = nombre.slice(0, 2).toLowerCase();
            const apPaternoLower = apPaterno.toLowerCase();
            const apMaternoFirst = apMaterno ? apMaterno[0].toLowerCase() : '';
            correoInput.value = `${nombrePart}.${apPaternoLower}${apMaternoFirst}@saludtotal.com`;
        }
    }

    nombreInput.addEventListener('input', generarCorreo);
    apPaternoInput.addEventListener('input', generarCorreo);
    apMaternoInput.addEventListener('input', generarCorreo);

    // Deshabilitar edición de correo y contraseña
    contrasenaInput.readOnly = true;
    correoInput.readOnly = true;
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initMedicoForm);
