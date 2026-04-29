const form = document.querySelector("#appointment-form");
const submitButton = document.querySelector("#submit-button");
const message = document.querySelector("#form-message");
const list = document.querySelector("#appointment-list");
const emptyState = document.querySelector("#empty-state");
const count = document.querySelector("#appointment-count");
const refreshButton = document.querySelector("#refresh-button");
const dateInput = document.querySelector("#date");
const timeSelect = document.querySelector("#time");

const weekdaySlots = [
    "08:00", "08:30", "09:00", "09:30",
    "10:00", "10:30", "11:00", "11:30",
    "12:00", "12:30", "13:00", "13:30",
    "14:00", "14:30", "15:00", "15:30",
    "16:00", "16:30"
];

const saturdaySlots = [
    "09:00", "09:30", "10:00", "10:30",
    "11:00", "11:30", "12:00", "12:30"
];

let currentAppointments = [];

function setMessage(text, type = "") {
    message.textContent = text;
    message.dataset.type = type;
}

function formatAppointmentDate(value) {
    const date = new Date(`${value}T00:00:00`);
    return new Intl.DateTimeFormat(undefined, {
        weekday: "short",
        month: "short",
        day: "numeric",
        year: "numeric"
    }).format(date);
}

function formatAppointmentTime(value) {
    const [hour, minute] = value.split(":").map(Number);
    const date = new Date();
    date.setHours(hour, minute, 0, 0);

    return new Intl.DateTimeFormat(undefined, {
        hour: "numeric",
        minute: "2-digit"
    }).format(date);
}

function getSlotsForDate(value) {
    if (!value) {
        return [];
    }

    const date = new Date(`${value}T00:00:00`);
    const weekday = date.getDay();

    if (weekday >= 1 && weekday <= 5) {
        return weekdaySlots;
    }

    if (weekday === 6) {
        return saturdaySlots;
    }

    return [];
}

function setTodayMinimumDate() {
    const today = new Date();
    const offset = today.getTimezoneOffset() * 60000;
    const localDate = new Date(today.getTime() - offset).toISOString().slice(0, 10);
    dateInput.min = localDate;
}

function getBookedSlots(dateValue) {
    return new Set(
        currentAppointments
            .filter((appointment) => appointment.date === dateValue)
            .map((appointment) => appointment.time)
    );
}

function populateTimeSlots() {
    const selectedDate = dateInput.value;
    const slots = getSlotsForDate(selectedDate);
    const bookedSlots = getBookedSlots(selectedDate);

    timeSelect.replaceChildren();

    if (!selectedDate) {
        timeSelect.disabled = true;
        timeSelect.append(new Option("Choose a date first", ""));
        return;
    }

    if (slots.length === 0) {
        timeSelect.disabled = true;
        timeSelect.append(new Option("Clinic closed", ""));
        return;
    }

    timeSelect.disabled = false;
    timeSelect.append(new Option("Select a time", ""));

    slots.forEach((slot) => {
        const label = bookedSlots.has(slot)
            ? `${formatAppointmentTime(slot)} - booked`
            : formatAppointmentTime(slot);
        const option = new Option(label, slot);
        option.disabled = bookedSlots.has(slot);
        timeSelect.append(option);
    });
}

function formatPatientContact(appointment) {
    return [appointment.phone, appointment.email]
        .filter(Boolean)
        .join(" | ");
}

function getServiceClass(service) {
    const serviceGroups = {
        "Primary Care Visit": "service-general",
        "Follow-Up Visit": "service-general",
        "Annual Wellness Exam": "service-preventive",
        "Vaccination Appointment": "service-preventive",
        "Pediatric Checkup": "service-family",
        "Sick Visit": "service-sick",
        "Lab Results Review": "service-review"
    };

    return serviceGroups[service] || "service-general";
}

function renderAppointments(appointments) {
    list.replaceChildren();
    count.textContent = appointments.length;
    emptyState.hidden = appointments.length > 0;

    appointments.forEach((appointment) => {
        const item = document.createElement("article");
        item.className = "appointment-item";

        const details = document.createElement("div");
        details.className = "appointment-details";

        const patientName = document.createElement("h3");
        patientName.className = "patient-name";
        patientName.textContent = appointment.name;

        const service = document.createElement("span");
        service.className = `service-title ${getServiceClass(appointment.service)}`;
        service.textContent = appointment.service;

        const schedule = document.createElement("p");
        schedule.className = "appointment-time";
        schedule.textContent = `${formatAppointmentDate(appointment.date)} at ${formatAppointmentTime(appointment.time)}`;

        const patient = document.createElement("p");
        patient.textContent = formatPatientContact(appointment);

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.className = "delete-button";
        deleteButton.textContent = "\u00d7";
        deleteButton.setAttribute("aria-label", `Delete appointment for ${appointment.name}`);
        deleteButton.title = "Delete appointment";
        deleteButton.addEventListener("click", () => deleteAppointment(appointment.id));

        details.append(patientName, service, schedule);

        if (patient.textContent) {
            details.append(patient);
        }

        if (appointment.reason) {
            const reason = document.createElement("p");
            reason.className = "visit-reason";
            reason.textContent = appointment.reason;
            details.append(reason);
        }

        item.append(details, deleteButton);
        list.append(item);
    });
}

async function requestJson(url, options = {}) {
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            ...options.headers
        },
        ...options
    });

    const payload = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(payload.error || "Something went wrong");
    }

    return payload;
}

async function loadAppointments() {
    refreshButton.disabled = true;

    try {
        currentAppointments = await requestJson("/appointments");
        renderAppointments(currentAppointments);
        populateTimeSlots();
    } catch (error) {
        setMessage(error.message, "error");
    } finally {
        refreshButton.disabled = false;
    }
}

async function deleteAppointment(id) {
    setMessage("");

    try {
        await requestJson(`/appointments/${id}`, { method: "DELETE" });
        await loadAppointments();
        setMessage("Appointment deleted.", "success");
    } catch (error) {
        setMessage(error.message, "error");
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    setMessage("");
    submitButton.disabled = true;

    const formData = new FormData(form);
    const appointment = {
        name: formData.get("name").trim(),
        phone: formData.get("phone").trim(),
        email: formData.get("email").trim(),
        service: formData.get("service"),
        date: formData.get("date"),
        time: formData.get("time") || "",
        reason: formData.get("reason").trim()
    };

    try {
        await requestJson("/appointments", {
            method: "POST",
            body: JSON.stringify(appointment)
        });

        form.reset();
        populateTimeSlots();
        await loadAppointments();
        setMessage("Visit booked.", "success");
    } catch (error) {
        setMessage(error.message, "error");
    } finally {
        submitButton.disabled = false;
    }
});

dateInput.addEventListener("change", populateTimeSlots);
refreshButton.addEventListener("click", loadAppointments);

setTodayMinimumDate();
populateTimeSlots();
loadAppointments();
