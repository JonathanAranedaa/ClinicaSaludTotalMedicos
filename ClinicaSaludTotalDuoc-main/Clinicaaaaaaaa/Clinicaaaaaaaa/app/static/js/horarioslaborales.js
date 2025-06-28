// Controlador de Horarios Laborales
$(document).ready(function() {
    // Modelo
    class CalendarModel {
        constructor() {
            this.currentYear = new Date().getFullYear();
            this.currentMonth = new Date().getMonth();
            this.currentView = 'month';
            this.selectedDates = new Set();
            this.isDragging = false;
            this.dragStart = null;
            this.currentWeekStart = null;
            
            // Variables de tiempo
            this.timeSlots = {
                '00:00': '00:00 - 01:00',
                '01:00': '01:00 - 02:00',
                '02:00': '02:00 - 03:00',
                '03:00': '03:00 - 04:00',
                '04:00': '04:00 - 05:00',
                '05:00': '05:00 - 06:00',
                '06:00': '06:00 - 07:00',
                '07:00': '07:00 - 08:00',
                '08:00': '08:00 - 09:00',
                '09:00': '09:00 - 10:00',
                '10:00': '10:00 - 11:00',
                '11:00': '11:00 - 12:00',
                '12:00': '12:00 - 13:00',
                '13:00': '13:00 - 14:00',
                '14:00': '14:00 - 15:00',
                '15:00': '15:00 - 16:00',
                '16:00': '16:00 - 17:00',
                '17:00': '17:00 - 18:00',
                '18:00': '18:00 - 19:00',
                '19:00': '19:00 - 20:00',
                '20:00': '20:00 - 21:00',
                '21:00': '21:00 - 22:00',
                '22:00': '22:00 - 23:00',
                '23:00': '23:00 - 24:00'
            };
        }

        getWeekStart(date) {
            const day = date.getDay();
            const diff = date.getDate() - day + (day === 0 ? -6 : 1);
            return new Date(date.setDate(diff));
        }

        getNextWeekStart() {
            const date = new Date(this.currentWeekStart);
            date.setDate(date.getDate() + 7);
            return date;
        }

        getPreviousWeekStart() {
            const date = new Date(this.currentWeekStart);
            date.setDate(date.getDate() - 7);
            return date;
        }
    }

    // Vista
    class CalendarView {
        constructor() {
            this.$calendarGrid = $('#calendarGrid');
            this.$currentDate = $('#currentDate');
            this.$viewMode = $('#viewMode');
            this.$prevMonth = $('#prevMonth');
            this.$nextMonth = $('#nextMonth');
        }

        updateDateDisplay(currentView, currentWeekStart, currentMonth, currentYear) {
            if (currentView === 'week') {
                if (currentWeekStart) {
                    const currentDate = new Date(currentWeekStart);
                    const weekEnd = new Date(currentWeekStart);
                    weekEnd.setDate(currentWeekStart.getDate() + 6);
                    
                    const options = { weekday: 'long', month: 'long', day: 'numeric' };
                    const startText = currentDate.toLocaleDateString('es-ES', options);
                    const endText = weekEnd.toLocaleDateString('es-ES', options);
                    
                    this.$currentDate.text(`Semana del ${startText} al ${endText}`);
                }
            } else {
                const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
                this.$currentDate.text(`${monthNames[currentMonth]} ${currentYear}`);
            }
        }

        renderWeekView(currentWeekStart, selectedDates, today) {
            this.$calendarGrid.empty();
            
            // Headers
            const daysOfWeek = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
            daysOfWeek.forEach(day => {
                $('<div class="calendar-week-day-header">')
                    .text(day)
                    .appendTo(this.$calendarGrid);
            });

            // Days of the week
            for (let i = 0; i < 7; i++) {
                const date = new Date(currentWeekStart);
                date.setDate(date.getDate() + i);
                const dateStr = date.toISOString().split('T')[0];
                const isToday = date.toDateString() === today.toDateString();
                
                const dayContainer = $('<div class="calendar-week-day">')
                    .toggleClass('current', isToday)
                    .appendTo(this.$calendarGrid);

                // Day number
                $('<div class="day-number">')
                    .text(date.getDate())
                    .appendTo(dayContainer);
            }
        }
    }

    // Controlador
    class CalendarController {
        constructor() {
            this.model = new CalendarModel();
            this.view = new CalendarView();
            this.initialize();
            this.render();
        }

        initialize() {
            this.setupEventListeners();
        }

        setupEventListeners() {
            $('#viewMode').on('change', (e) => {
                this.model.currentView = e.target.value;
                this.render();
            });

            $('#prevMonth').on('click', () => {
                if (this.model.currentView === 'week') {
                    this.model.currentWeekStart = this.model.getPreviousWeekStart();
                } else {
                    this.model.currentMonth--;
                    if (this.model.currentMonth < 0) {
                        this.model.currentMonth = 11;
                        this.model.currentYear--;
                    }
                }
                this.render();
            });

            $('#nextMonth').on('click', () => {
                if (this.model.currentView === 'week') {
                    this.model.currentWeekStart = this.model.getNextWeekStart();
                } else {
                    this.model.currentMonth++;
                    if (this.model.currentMonth > 11) {
                        this.model.currentMonth = 0;
                        this.model.currentYear++;
                    }
                }
                this.render();
            });
        }

        render() {
            if (this.model.currentView === 'week') {
                this.view.renderWeekView(
                    this.model.currentWeekStart,
                    this.model.selectedDates,
                    new Date()
                );
            }
        }
    }

    // Inicializar la aplicación
    new CalendarController();
});
