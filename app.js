const state = {
    leads: [],
    filter: "all"
};

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("leadForm").addEventListener("submit", saveLead);
    loadLeads();
});

async function loadLeads() {
    const response = await fetch("/api/leads");

    if (!response.ok) {
        return;
    }

    state.leads = await response.json();
    renderLeads();
}

function addLead() {
    const button = document.getElementById("addButton");

    button.disabled = true;
    document.getElementById("addButtonText").textContent = "";
    button.insertAdjacentHTML("afterbegin", '<span class="button-spinner"></span>');

    setTimeout(() => {
        button.querySelector(".button-spinner")?.remove();
        document.getElementById("addButtonText").textContent = "+ Добавить лид";
        button.disabled = false;

        document.body.classList.add("drawer-open");
        document.getElementById("addDrawer").classList.add("open");
        document.getElementById("leadName").focus();
    }, 180);
}

function closeAddLead() {
    document.body.classList.remove("drawer-open");
    document.getElementById("addDrawer").classList.remove("open");
    document.getElementById("leadForm").reset();
    document.getElementById("formError").style.display = "none";
}

async function saveLead(event) {
    event.preventDefault();

    const form = new FormData(event.target);
    const data = {
        name: form.get("name").trim(),
        contact: form.get("contact").trim(),
        request: form.get("request").trim(),
        source: form.get("source")
    };

    const saveButton = document.getElementById("saveButton");
    const spinner = document.getElementById("formSpinner");
    const error = document.getElementById("formError");

    saveButton.disabled = true;
    spinner.style.display = "block";
    error.style.display = "none";

    try {
        const response = await fetch("/api/leads", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error("Не удалось добавить лид");
        }

        closeAddLead();
        await loadLeads();
    } catch (e) {
        error.textContent = e.message;
        error.style.display = "block";
    } finally {
        saveButton.disabled = false;
        spinner.style.display = "none";
    }
}

function renderLeads() {
    const table = document.getElementById("leadsTable");
    const empty = document.getElementById("empty");

    table.innerHTML = "";

    const visible = state.leads.filter(lead => {
        if (state.filter === "all") {
            return true;
        }

        return lead.source.toLowerCase() === state.filter;
    });

    visible.forEach(lead => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td class="id">#${lead.id}</td>
            <td class="name">${escapeHtml(lead.name)}</td>
            <td class="contact">${escapeHtml(lead.contact)}</td>
            <td class="request">${escapeHtml(lead.request)}</td>
            <td>
                <span class="source ${lead.source === "manual" ? "manual" : ""}">
                    <span class="source-dot"></span>${escapeHtml(lead.source)}
                </span>
            </td>
            <td>${formatDate(lead.created_at)}</td>
            <td><div class="tags"></div></td>
        `;

        table.appendChild(row);
    });

    empty.style.display = visible.length ? "none" : "block";
    document.getElementById("totalCount").textContent = state.leads.length;
    document.getElementById("telegramCount").textContent =
        state.leads.filter(lead => lead.source === "telegram").length;
}

function filterLeads(filter, button) {
    state.filter = filter;

    document.querySelectorAll(".filter").forEach(item => {
        item.classList.remove("active");
    });

    button.classList.add("active");
    renderLeads();
}

function formatDate(timestamp) {
    return new Date(timestamp * 1000).toLocaleString("ru-RU", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit"
    });
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}
