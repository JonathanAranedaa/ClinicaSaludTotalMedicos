// Variables globales
let currentYear = new Date().getFullYear();
let currentMonth = new Date().getMonth();
let currentWeekStart = null; // Inicialmente null
let currentView = 'month';
let selectedDates = new Set();
const daysOfWeek = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
const hours = Array.from({ length: 24 }, (_, i) => i.toString().padStart(2, '0') + ':00');
const defaultHours = {
    inicio: '00:00',
    fin: '23:59'
};

// Función para actualizar el título del mes
function updateMonthTitle() {
    const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    const monthName = monthNames[currentMonth];
    $('#currentDate').text(`${monthName} ${currentYear}`);
}

// Función para navegar al mes siguiente
function nextMonth() {
    currentMonth++;
    if (currentMonth > 11) {
        currentMonth = 0;
        currentYear++;
    }
    updateMonthTitle();
    renderMonthlyCalendar();
}

// Función para navegar al mes anterior
function previousMonth() {
    currentMonth--;
    if (currentMonth < 0) {
        currentMonth = 11;
        currentYear--;
    }
    updateMonthTitle();
    renderMonthlyCalendar();
}

// Inicializar el título del mes al cargar la página
$(document).ready(function() {
    updateMonthTitle();
    
    // Configurar eventos de navegación
    $('#nextMonth').click(nextMonth);
    $('#prevMonth').click(previousMonth);
});

// Funciones principales
function renderMonthlyCalendar() {
    const container = $('#calendarMonthly .calendar-monthly-body');
    container.empty();

    // Crear la tabla del calendario
    const table = $('<table class="calendar-monthly-table">');
    const thead = $('<thead>');
    const tbody = $('<tbody>');

    // Crear encabezados de días
    const headerRow = $('<tr>');
    daysOfWeek.forEach(day => {
        headerRow.append($('<th>').text(day));
    });
    thead.append(headerRow);

    // Crear días del mes
    const firstDay = new Date(currentYear, currentMonth, 1);
    const lastDay = new Date(currentYear, currentMonth + 1, 0);
    const startDate = new Date(currentYear, currentMonth, 1 - firstDay.getDay());
    const endDate = new Date(currentYear, currentMonth + 1, 7 - lastDay.getDay());

    let currentDay = startDate;
    let row = $('<tr>');

    while (currentDay <= endDate) {
        const dayCell = $('<td>');
        
        // Estilizar días fuera del mes
        if (currentDay.getMonth() !== currentMonth) {
            dayCell.addClass('outside-month');
        }

        // Agregar número del día
        dayCell.text(currentDay.getDate());

        // Manejar clic en el día
        dayCell.click(function() {
            const date = new Date(currentDay);
            const dayOfWeek = date.getDay();
            const dayNumber = date.getDate();
            
            // Limpiar selección anterior
            $('.calendar-monthly-day').removeClass('selected');
            
            // Seleccionar el día actual
            $(this).addClass('selected');
            
            // Actualizar campos del formulario
            const formattedDate = date.toLocaleDateString('es-ES', {
                weekday: 'long',
                day: 'numeric',
                month: 'long',
                year: 'numeric'
            });
            
            $('#fecha').val(formattedDate);
            $('#diaSemana').val(daysOfWeek[dayOfWeek]);
            $('#dia').val(dayNumber);
            
            // Actualizar vista semanal
            currentWeekStart = new Date(date.getFullYear(), date.getMonth(), date.getDate() - date.getDay());
            renderWeeklyCalendar();
            
            // Actualizar display de fechas seleccionadas
            // Formato YYYY-MM-DD para PostgreSQL DATE
            const dateStr = date.getFullYear() + '-' + 
                           (date.getMonth() + 1).toString().padStart(2, '0') + '-' +
                           date.getDate().toString().padStart(2, '0');
            
            // Obtener el texto actual y actualizarlo
            let currentText = $('#selectedDatesList').text();
            if (currentText === 'Seleccione una fecha') {
                $('#selectedDatesList').text(dateStr);
            } else {
                // Si ya hay fechas, agregar la nueva
                $('#selectedDatesList').text(currentText + ', ' + dateStr);
            }
            
            // Actualizar el valor oculto con todas las fechas seleccionadas
            selectedDates.add(date.toISOString());
            $('#diaSemana').val(Array.from(selectedDates).join(','));
        });

        row.append(dayCell);

        // Si es el último día del mes o el último día de la semana, crear una nueva fila
        if (currentDay.getDate() === lastDay.getDate() || currentDay.getDay() === 6) {
            tbody.append(row);
            row = $('<tr>');
        }

        currentDay.setDate(currentDay.getDate() + 1);
    }

    table.append(thead, tbody);
    container.append(table);

    // Actualizar el título del calendario
    const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    const monthName = monthNames[currentMonth];
    $('.calendar-monthly-header').text(`${monthName} ${currentYear}`);
}

// Variables para selección múltiple
let lastSelectedDate = null;
let lastSelectedHour = null;

// Función para obtener la semana actual
function getCurrentWeek() {
    const now = new Date();
    const day = now.getDay();
    const diff = now.getDate() - day + (day === 0 ? -6 : 1); // Ajuste para que el lunes sea el primer día
    const weekStart = new Date(now.setDate(diff));
    return weekStart;
}

// Función para manejar selección de día en vista semanal
function toggleSelection(event, date, hour, selected, dayOfWeek) {
    // Obtener el elemento que disparó el evento
    const hourCell = $(event.currentTarget);
    const dayContainer = hourCell.closest('.calendar-weekly-day');
    const currentHour = parseInt(hour); // La hora ya viene como número
    const currentDate = dayContainer.data('date');
    const currentDayOfWeek = dayContainer.data('dayOfWeek');

    // Si se hace clic en una hora no seleccionada
    if (!selected) {
        // Limpiar selección anterior si es un nuevo día
        if (lastSelectedDate && !currentDate.toISOString().startsWith(lastSelectedDate.toISOString().split('T')[0])) {
            selectedDates.clear();
            $('.calendar-weekly-time').removeClass('selected');
            clearFormFields();
        }

        // Seleccionar la hora actual
        hourCell.addClass('selected');
        selectedDates.add(currentDate.toISOString() + currentHour);
        lastSelectedHour = currentHour;
        lastSelectedDate = currentDate;
        updateFormFields(currentDate, hour, null);
        actualizarListaFechas();
    } else {
        // Si se hace clic en una hora ya seleccionada
        hourCell.removeClass('selected');
        selectedDates.delete(currentDate.toISOString() + currentHour);
        
        // Si se hace clic en la última hora seleccionada, limpiar selección
        if (currentHour === lastSelectedHour && currentDate.toISOString() === lastSelectedDate.toISOString()) {
            lastSelectedHour = null;
            lastSelectedDate = null;
            clearFormFields();
        }
        actualizarListaFechas();
    }

    // Manejar selección múltiple con Shift
    if (event && event.shiftKey && lastSelectedDate) {
        const startHour = Math.min(lastSelectedHour, currentHour);
        const endHour = Math.max(lastSelectedHour, currentHour);
        
        // Seleccionar/deseleccionar todas las horas entre startHour y endHour
        for (let h = startHour; h <= endHour; h++) {
            const hourId = currentDate.toISOString() + h;
            const hourCell = dayContainer.find(`[data-hour="${h}"]`);
            
            if (selectedDates.has(hourId)) {
                hourCell.removeClass('selected');
                selectedDates.delete(hourId);
            } else {
                hourCell.addClass('selected');
                selectedDates.add(hourId);
            }
        }
        
        // Actualizar la última hora seleccionada
        lastSelectedHour = currentHour;
        actualizarListaFechas();
    }
}

// Función para obtener la siguiente semana
function getNextWeek() {
    const nextWeek = new Date(currentWeekStart);
    nextWeek.setDate(currentWeekStart.getDate() + 7);
    return nextWeek;
}

// Función para obtener la semana anterior
function getPreviousWeek() {
    const prevWeek = new Date(currentWeekStart);
    prevWeek.setDate(currentWeekStart.getDate() - 7);
    return prevWeek;
}

// Función para manejar selección de día en vista semanal
function toggleSelection(event, date, hour, selected, dayOfWeek) {
    // Obtener el elemento que disparó el evento
    const hourCell = $(event.currentTarget);
    const dayContainer = hourCell.closest('.calendar-weekly-day');
    const currentHour = parseInt(hour); // La hora ya viene como número
    const currentDate = dayContainer.data('date');
    const currentDayOfWeek = dayContainer.data('dayOfWeek');

    // Si se hace clic en una hora no seleccionada
    if (!selected) {
        // Limpiar selección anterior si es un nuevo día
        if (lastSelectedDate && !currentDate.toISOString().startsWith(lastSelectedDate.toISOString().split('T')[0])) {
            selectedDates.clear();
            $('.calendar-weekly-time').removeClass('selected');
            clearFormFields();
        }

        // Seleccionar la hora actual
        hourCell.addClass('selected');
        selectedDates.add(currentDate.toISOString() + currentHour);
        lastSelectedHour = currentHour;
        lastSelectedDate = currentDate;
        updateFormFields(currentDate, hour, null);
        actualizarListaFechas();
    } else {
        // Si se hace clic en una hora ya seleccionada
        hourCell.removeClass('selected');
        selectedDates.delete(currentDate.toISOString() + currentHour);
        
        // Si se hace clic en la última hora seleccionada, limpiar selección
        if (currentHour === lastSelectedHour && currentDate.toISOString() === lastSelectedDate.toISOString()) {
            lastSelectedHour = null;
            lastSelectedDate = null;
            clearFormFields();
        }
        actualizarListaFechas();
    }

    // Manejar selección múltiple con Shift
    if (event && event.shiftKey && lastSelectedDate) {
        const startHour = Math.min(lastSelectedHour, currentHour);
        const endHour = Math.max(lastSelectedHour, currentHour);
        
        // Seleccionar/deseleccionar todas las horas entre startHour y endHour
        for (let h = startHour; h <= endHour; h++) {
            const hourId = currentDate.toISOString() + h;
            const hourCell = dayContainer.find(`[data-hour="${h}"]`);
            
            if (selectedDates.has(hourId)) {
                hourCell.removeClass('selected');
                selectedDates.delete(hourId);
            } else {
                hourCell.addClass('selected');
                selectedDates.add(hourId);
            }
        }
        
        // Actualizar la última hora seleccionada
        lastSelectedHour = currentHour;
        actualizarListaFechas();
    }
}

// Función para actualizar la lista de fechas seleccionadas
function actualizarListaFechas() {
    const selectedDatesList = $('#selectedDatesList');
    selectedDatesList.empty();
    


    // Obtener todas las fechas seleccionadas y ordenarlas
    const sortedDates = Array.from(selectedDates)
        .map(dateStr => new Date(dateStr))
        .sort((a, b) => a - b);

    // Crear lista de fechas en formato YYYY-MM-DD
    const formattedDates = sortedDates.map(date => {
        return date.getFullYear() + '-' + 
               (date.getMonth() + 1).toString().padStart(2, '0') + '-' +
               date.getDate().toString().padStart(2, '0');
    });

    // Mostrar las fechas en el display
    if (formattedDates.length === 0) {
        selectedDatesList.text('Seleccione una fecha');
    } else {
        selectedDatesList.text(formattedDates.join(', '));
    }
}

// Función para obtener la fecha formateada para la vista semanal
function getWeekRange() {
    const startDate = new Date(currentWeekStart);
    const endDate = new Date(currentWeekStart);
    endDate.setDate(endDate.getDate() + 6);
    
    return startDate.toLocaleDateString('es-ES', { 
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    }) + ' - ' + 
    endDate.toLocaleDateString('es-ES', { 
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
}

// Función para renderizar el calendario semanal
function renderWeeklyCalendar() {
    const container = $('#calendarWeekly .calendar-weekly-body');
    container.empty();

    // Obtener el rango de fechas para la semana
    const weekStart = currentWeekStart;
    const weekEnd = new Date(weekStart.getTime() + 6 * 24 * 60 * 60 * 1000);

    // Crear nombres de días si no existen
    if ($('#calendarWeekly .calendar-weekly-days-header').length === 0) {
        const daysHeader = $('<div class="calendar-weekly-days-header">');
        daysOfWeek.forEach(day => {
            daysHeader.append(`<div class="day-name">${day}</div>`);
        });
        $('#calendarWeekly').prepend(daysHeader);
    }

    // Crear contenedor para cada día
    for (let i = 0; i < 7; i++) {
        const day = new Date(weekStart.getTime() + i * 24 * 60 * 60 * 1000);
        const dayContainer = $('<div class="calendar-weekly-day">');
        dayContainer.data('date', day);
        dayContainer.data('dayOfWeek', day.getDay());

        // Agregar número del día
        const dayNumber = $('<div class="day-number">').text(day.getDate());
        dayContainer.append(dayNumber);

        // Agregar horas
        const hoursContainer = $('<div class="calendar-weekly-hours">');
        for (let hour = 8; hour <= 20; hour++) { // Horas de 8:00 a 20:00
            const hourCell = $('<div class="calendar-weekly-time">');
            hourCell.data('hour', hour);
            hourCell.text(hour + ':00');

            // Verificar si está seleccionado
            if (selectedDates.has(day.toISOString() + hour)) {
                hourCell.addClass('selected');
            }

            // Manejar selección de día
            hourCell.click(function(e) {
                e.preventDefault();
                const date = dayContainer.data('date');
                const hour = $(this).data('hour');
                const selected = $(this).hasClass('selected');
                const dayOfWeek = dayContainer.data('dayOfWeek');
                
                // Si se hace clic con Shift, seleccionar múltiples horas
                if (e.shiftKey) {
                    // Si no hay una hora seleccionada previamente, seleccionar solo esta
                    if (!lastSelectedDate || !lastSelectedHour) {
                        toggleSelection(e, date, hour, selected, dayOfWeek);
                        return;
                    }

                    // Obtener el día actual
                    const currentDate = dayContainer.data('date');
                    
                    // Si es el mismo día, seleccionar/deseleccionar el rango
                    if (currentDate.toISOString() === lastSelectedDate.toISOString()) {
                        const startHour = Math.min(lastSelectedHour, parseInt(hour));
                        const endHour = Math.max(lastSelectedHour, parseInt(hour));
                        
                        // Seleccionar/deseleccionar todas las horas entre startHour y endHour
                        for (let h = startHour; h <= endHour; h++) {
                            const hourId = currentDate.toISOString() + h;
                            const hourCell = dayContainer.find(`[data-hour="${h}"]`);
                            
                            if (selected) {
                                hourCell.removeClass('selected');
                                selectedDates.delete(hourId);
                            } else {
                                hourCell.addClass('selected');
                                selectedDates.add(hourId);
                            }
                        }
                        
                        // Actualizar la última hora seleccionada
                        lastSelectedHour = parseInt(hour);
                        actualizarListaFechas();
                    }
                } else {
                    // Selección normal
                    toggleSelection(e, date, hour, selected, dayOfWeek);
                }
            });

            hoursContainer.append(hourCell);
        }
        dayContainer.append(hoursContainer);

        container.append(dayContainer);
    }

    // Actualizar el rango de fechas en el encabezado principal
    const weekRange = getWeekRange();
    $('#currentDate').text(weekRange);
}

// Función para renderizar el calendario mensual
function renderMonthlyCalendar() {
    const container = $('#calendarMonthly .calendar-monthly-body');
    container.empty();

    // Solo agregar el header si no existe
    if ($('#calendarMonthly .calendar-monthly-header').length === 0) {
        const header = $('<div class="calendar-monthly-header">');
        daysOfWeek.forEach(day => {
            header.append($('<div>').text(day));
        });
        container.before(header);
    }

    // Calcular el primer día del mes
    const firstDay = new Date(currentYear, currentMonth, 1);
    const lastDay = new Date(currentYear, currentMonth + 1, 0);
    const startDay = firstDay.getDay();
    const daysInMonth = lastDay.getDate();

    // Crear contenedor para cada día
    let day = 1;
    for (let i = 0; i < Math.ceil((startDay + daysInMonth) / 7); i++) {
        for (let j = 0; j < 7; j++) {
            if (i === 0 && j < startDay || day > daysInMonth) {
                container.append($('<div class="calendar-monthly-day empty">'));
            } else {
                const dayContainer = $('<div class="calendar-monthly-day">');
                dayContainer.data('date', new Date(currentYear, currentMonth, day));
                dayContainer.data('dayOfWeek', j);
                dayContainer.append($('<div class="day-number">').text(day));

                // Estilos para el día actual
                if (dayContainer.data('date').getTime() === new Date().getTime()) {
                    dayContainer.addClass('current');
                }

                // Estilos para fines de semana
                if (j === 0 || j === 6) {
                    dayContainer.addClass('weekend');
                }

                // Evento de clic
                dayContainer.click(function() {
                    const date = $(this).data('date');
                    const selected = $(this).hasClass('selected');
                    const dayOfWeek = $(this).data('dayOfWeek');

                    // Toggle selection
                    if (selected) {
                        $(this).removeClass('selected');
                        selectedDates.delete(date.toISOString());
                        clearFormFields();
                        actualizarListaFechas();
                    } else {
                        $(this).addClass('selected');
                        selectedDates.add(date.toISOString());
                        updateFormFields(date, null, null);
                        actualizarListaFechas();
                    }
                });

                container.append(dayContainer);
                day++;
            }
        }
    }
}

// Función para cambiar la vista
function changeView(view) {
    currentView = view;
    updateDateDisplay();

    // Ocultar ambas vistas primero
    $('#calendarMonthly').hide();
    $('#calendarWeekly').hide();

    // Mostrar y renderizar la vista seleccionada
    if (view === 'month') {
        $('#calendarMonthly').show();
        renderMonthlyCalendar();
    } else {
        $('#calendarWeekly').show();
        renderWeeklyCalendar();
    }
}

// Función para manejar eventos de navegación
function handleNavigationEvents() {
    $('#prevMonth').click(function() {
        if (currentView === 'month') {
            currentMonth--;
            if (currentMonth < 0) {
                currentMonth = 11;
                currentYear--;
            }
            updateDateDisplay();
            renderMonthlyCalendar();
        } else {
            currentWeekStart = getPreviousWeek();
            updateDateDisplay();
            renderWeeklyCalendar();
        }
    });

    $('#nextMonth').click(function() {
        if (currentView === 'month') {
            currentMonth++;
            if (currentMonth > 11) {
                currentMonth = 0;
                currentYear++;
            }
            updateDateDisplay();
            renderMonthlyCalendar();
        } else {
            currentWeekStart = getNextWeek();
            updateDateDisplay();
            renderWeeklyCalendar();
        }
    });
}

// Evento para cambiar entre vistas
function handleViewChange() {
    $('#viewSelector').change(function() {
        const view = $(this).val();
        changeView(view);
    });
}

// Función para actualizar la fecha actual
function updateDateDisplay() {
    if (currentView === 'month') {
        $('#currentDate').text(new Date(currentYear, currentMonth).toLocaleDateString('es-ES', { 
            month: 'long',
            year: 'numeric'
        }));
    } else {
        $('#currentDate').text(currentWeekStart.toLocaleDateString('es-ES', { 
            weekday: 'long',
            month: 'long',
            day: 'numeric',
            year: 'numeric'
        }) + ' - ' + 
        new Date(currentWeekStart.getTime() + 6 * 24 * 60 * 60 * 1000).toLocaleDateString('es-ES', { 
            weekday: 'long',
            month: 'long',
            day: 'numeric',
            year: 'numeric'
        }));
    }
}

let selectedStartHour = null;
let selectedEndHour = null;
let dragging = false;
let currentSelectedDay = null;

// Función para limpiar los campos del formulario
function clearFormFields() {
    $('#selectedDatesList').empty().append(
        $('<span class="fecha-seleccionada">').text('Seleccione un día')
    );
    $('#diaSemana').val('');
    $('#horaInicio').val(defaultHours.inicio);
    $('#horaFin').val(defaultHours.fin);
    $('#medico').val('');
}

// Función para actualizar los campos del formulario
function updateFormFields(date, startHour, endHour) {
    const selectedDate = new Date(date);
    const dayOfWeek = selectedDate.getDay();
    const formattedDate = selectedDate.toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    
    // Formatear las horas en HH:mm
    const formatHour = (hour) => {
        if (hour === null) return '';
        return hour.toString().padStart(2, '0') + ':00';
    };
    
    // Actualizar campos del formulario
    $('#fecha').val(formattedDate);
    
    if (startHour !== null) {
        $('#hora_inicio').val(formatHour(startHour));
        $('#hora_fin').val(endHour !== null ? formatHour(endHour) : formatHour(startHour));
    } else {
        $('#hora_inicio').val('');
        $('#hora_fin').val('');
    }
}

function formatDayName(dayOfWeek) {
    const days = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
    return days[dayOfWeek];
}

function formatSelectedDates() {
    const selectedDatesList = Array.from(selectedDates).map(id => {
        const [dateStr, hour] = id.split('T');
        const date = new Date(dateStr);
        return date.toLocaleDateString('es-ES', {
            weekday: 'long',
            day: 'numeric',
            month: 'long',
            year: 'numeric'
        });
    });
    return selectedDatesList.join(', ');
}

function updateSelectedDatesDisplay() {
    const selectedDatesDisplay = formatSelectedDates();
    $('#selectedDatesDisplay').html(selectedDatesDisplay || '<span class="fecha-seleccionada">Seleccione un día</span>');
    $('#diaSemana').val(Array.from(selectedDates).join(','));
}

function toggleSelection(event, date, hour, selected, dayOfWeek) {
    // Obtener el elemento que disparó el evento
    const hourCell = $(event.currentTarget);
    const dayContainer = hourCell.closest('.calendar-weekly-day');
    const currentHour = hour; // Ya es un número
    const currentDate = dayContainer.data('date');
    const currentDayOfWeek = dayContainer.data('dayOfWeek');
    const hourId = currentDate.toISOString() + currentHour;

    // Si se hace clic en una hora no seleccionada
    if (!selected) {
        // Limpiar selección anterior si es un nuevo día
        if (lastSelectedDate && !currentDate.toISOString().startsWith(lastSelectedDate.toISOString().split('T')[0])) {
            selectedDates.clear();
            $('.calendar-weekly-time').removeClass('selected');
            clearFormFields();
        }

        // Seleccionar la hora actual
        hourCell.addClass('selected');
        selectedDates.add(hourId);
        lastSelectedDate = currentDate;
        lastSelectedHour = currentHour;
        actualizarListaFechas();
    } else {
        // Deseleccionar la hora
        hourCell.removeClass('selected');
        selectedDates.delete(hourId);
        if (selectedDates.size === 0) {
            lastSelectedDate = null;
            lastSelectedHour = null;
            clearFormFields();
        } else {
            actualizarListaFechas();
        }
    }

    // Manejar selección múltiple con Shift
    if (event && event.shiftKey && lastSelectedDate) {
        const startHour = Math.min(lastSelectedHour, currentHour);
        const endHour = Math.max(lastSelectedHour, currentHour);
        
        // Seleccionar/deseleccionar todas las horas entre startHour y endHour
        for (let h = startHour; h <= endHour; h++) {
            const hourId = currentDate.toISOString() + h;
            const hourCell = dayContainer.find(`[data-hour="${h}"]`);
            
            if (selectedDates.has(hourId)) {
                hourCell.removeClass('selected');
                selectedDates.delete(hourId);
            } else {
                hourCell.addClass('selected');
                selectedDates.add(hourId);
            }
        }
        
        // Actualizar la última hora seleccionada
        lastSelectedHour = currentHour;
        actualizarListaFechas();
    }
}

// Manejar eventos de arrastre
$(document).on('mousedown', '.calendar-weekly-time', function(e) {
    if (e.button === 0) { // Solo el botón izquierdo
        dragging = true;
        currentSelectedDay = $(this).closest('.calendar-weekly-day');
        selectedStartHour = $(this).data('hour');
        selectedEndHour = selectedStartHour;
        
        // Actualizar el formulario
        updateFormFields(currentSelectedDay.data('date'), selectedStartHour, selectedEndHour);
    }
});

$(document).on('mousemove', '.calendar-weekly-time', function(e) {
    if (!dragging) return;
    
    const currentHour = $(this).data('hour');
    const currentDay = $(this).closest('.calendar-weekly-day');
    
    if (currentDay[0] === currentSelectedDay[0]) {
        // Solo permitir selección dentro del mismo día
        selectedEndHour = currentHour;
        
        // Ordenar las horas
        const hours = [selectedStartHour, selectedEndHour].sort();
        selectedStartHour = hours[0];
        selectedEndHour = hours[1];
        
        // Actualizar el formulario
        updateFormFields(currentSelectedDay.data('date'), selectedStartHour, selectedEndHour);
    }
});

$(document).on('mouseup', function() {
    dragging = false;
    currentSelectedDay = null;
    selectedStartHour = null;
    selectedEndHour = null;
});

// Limpiar selección cuando se hace clic fuera del calendario
$(document).on('click', function(e) {
    if (!$(e.target).closest('.calendar-weekly-grid').length) {
        $('.calendar-weekly-time').removeClass('selected');
        selectedDates.clear();
        selectedStartHour = null;
        selectedEndHour = null;
        clearFormFields();
        actualizarListaFechas();
    }
});

// Inicialización
$(document).ready(function() {
    currentWeekStart = getCurrentWeek();
    
    if (currentView === 'month') {
        renderMonthlyCalendar();
    } else {
        renderWeeklyCalendar();
    }
    
    handleNavigationEvents();
    handleViewChange();
    
    // Manejar selección de día
    $(document).on('click', '.calendar-weekly-time', function(e) {
        e.preventDefault();
        const date = $(this).closest('.calendar-weekly-day').data('date');
        const hour = $(this).data('hour');
        const selected = $(this).hasClass('selected');
        const dayOfWeek = $(this).closest('.calendar-weekly-day').data('dayOfWeek');
        
        // Pasar la hora tal cual está en el data-hour
        toggleSelection(e, date, hour, selected, dayOfWeek);
    });
});
