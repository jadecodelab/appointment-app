const form = document.querySelector("#appointment-form");
const submitButton = document.querySelector("#submit-button");
const message = document.querySelector("#form-message");
const list = document.querySelector("#appointment-list");
const emptyState = document.querySelector("#empty-state");
const count = document.querySelector("#appointment-count");
const refreshButton = document.querySelector("#refresh-button");

function setMessage(text, type = "") {
    message.textContent = text;
    message.dataset.type = type;
}

function formatAppointmentDate(value) {
    const date = new Date(`${value}T00:00:00`);
    return new Intl.DateTimeFormat(undefined, {
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

function renderAppointments(appointments) {
    list.replaceChildren();
    count.textContent = appointments.length;
    emptyState.hidden = appointments.length > 0;

    appointments.forEach((appointment) => {
        const item = document.createElement("article");
        item.className = "appointment-item";

        const details = document.createElement("div");
        details.className = "appointment-details";

        const name = document.createElement("h3");
        name.textContent = appointment.name;

        const schedule = document.createElement("p");
        schedule.textContent = `${formatAppointmentDate(appointment.date)} at ${formatAppointmentTime(appointment.time)}`;

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.className = "delete-button";
        deleteButton.textContent = "\u00d7";
        deleteButton.setAttribute("aria-label", `Delete appointment for ${appointment.name}`);
        deleteButton.title = "Delete appointment";
        deleteButton.addEventListener("click", () => deleteAppointment(appointment.id));

        details.append(name, schedule);
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
        const appointments = await requestJson("/appointments");
        renderAppointments(appointments);
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
        date: formData.get("date"),
        time: formData.get("time")
    };

    try {
        await requestJson("/appointments", {
            method: "POST",
            body: JSON.stringify(appointment)
        });

        form.reset();
        await loadAppointments();
        setMessage("Appointment booked.", "success");
    } catch (error) {
        setMessage(error.message, "error");
    } finally {
        submitButton.disabled = false;
    }
});

refreshButton.addEventListener("click", loadAppointments);
loadAppointments();
