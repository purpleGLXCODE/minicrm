const state = {
    leads: [],
    tags: [],
    filter: "all",
    editingId: null,
    selectedTags: []
};

const DEFAULT_TAGS = ["🔥 Горячий", "🆕 Новый", "🤖 AI"];

document.addEventListener("DOMContentLoaded", async () => {
    document.getElementById("leadForm").addEventListener("submit", saveLead);
    await loadTags();
    await ensureDefaultTags();
    await loadTags();
    await loadLeads();
});

async function loadLeads() {
    const response = await fetch("/api/leads");

    if (!response.ok) {
        return;
    }

    state.leads = await response.json();
    renderToolbar();
    renderLeads();
}

async function loadTags() {
    const response = await fetch("/api/tags");

    if (!response.ok) {
        return;
    }

    state.tags = await response.json();
}

async function ensureDefaultTags() {
    for (const name of DEFAULT_TAGS) {
        await fetch("/api/tags", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({name})
        });
    }
}

function openAddLead() {
    state.editingId = null;
    state.selectedTags = [];

    const button = document.getElementById("addButton");
    button.disabled = true;
    document.getElementById("addButtonText").textContent = "";
    button.insertAdjacentHTML("afterbegin", '<span class="button-spinner"></span>');

    setTimeout(() => {
        button.querySelector(".button-spinner")?.remove();
        document.getElementById("addButtonText").textContent = "+ Добавить лид";
        button.disabled = false;

        document.getElementById("drawerTitle").textContent = "Новый лид";
        document.getElementById("saveButtonText").textContent = "Добавить";
        document.getElementById("leadForm").reset();
        document.getElementById("formError").style.display = "none";
        document.getElementById("addTagRow").style.display = "none";
        renderTagPicker();

        document.body.classList.add("drawer-open");
        document.getElementById("leadDrawer").classList.add("open");
        document.getElementById("leadName").focus();
    }, 180);
}

function openEditLead(leadId) {
    const lead = state.leads.find(item => item.id === leadId);

    if (!lead) {
        return;
    }

    state.editingId = leadId;
    state.selectedTags = [...(lead.tags || [])];

    document.getElementById("drawerTitle").textContent = "Редактировать лид";
    document.getElementById("saveButtonText").textContent = "Сохранить";
    document.getElementById("leadName").value = lead.name;
    document.getElementById("leadContact").value = lead.contact;
    document.getElementById("leadRequest").value = lead.request;
    document.getElementById("leadSource").value = lead.source;
    document.getElementById("formError").style.display = "none";
    document.getElementById("addTagRow").style.display = "none";
    renderTagPicker();

    document.body.classList.add("drawer-open");
    document.getElementById("leadDrawer").classList.add("open");
    document.getElementById("leadName").focus();
}

function closeDrawer() {
    document.body.classList.remove("drawer-open");
    document.getElementById("leadDrawer").classList.remove("open");
    document.getElementById("leadForm").reset();
    document.getElementById("formError").style.display = "none";
    document.getElementById("addTagRow").style.display = "none";
    state.editingId = null;
    state.selectedTags = [];
}

function renderTagPicker() {
    const picker = document.getElementById("tagsPicker");
    picker.innerHTML = "";

    state.tags.forEach(tag => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "tag-choice" + (state.selectedTags.includes(tag.name) ? " selected" : "");
        button.textContent = tag.name;
        button.onclick = () => toggleTag(tag.name);
        picker.appendChild(button);
    });
}

function toggleTag(name) {
    if (state.selectedTags.includes(name)) {
        state.selectedTags = state.selectedTags.filter(tag => tag !== name);
    } else {
        state.selectedTags.push(name);
    }

    renderTagPicker();
}

function showNewTag() {
    const row = document.getElementById("addTagRow");
    row.style.display = "flex";
    document.getElementById("newTagName").focus();
}

async function createTag() {
    const input = document.getElementById("newTagName");
    const name = input.value.trim();

    if (!name) {
        return;
    }

    const response = await fetch("/api/tags", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({name})
    });

    if (!response.ok) {
        return;
    }

    const tag = await response.json();
    await loadTags();

    if (!state.selectedTags.includes(tag.name)) {
        state.selectedTags.push(tag.name);
    }

    input.value = "";
    document.getElementById("addTagRow").style.display = "none";
    renderTagPicker();
}

async function saveLead(event) {
    event.preventDefault();

    const form = new FormData(event.target);
    const data = {
        name: form.get("name").trim(),
        contact: form.get("contact").trim(),
        request: form.get("request").trim(),
        source: form.get("source"),
        tags: state.selectedTags
    };

    const saveButton = document.getElementById("saveButton");
    const spinner = document.getElementById("formSpinner");
    const error = document.getElementById("formError");

    saveButton.disabled = true;
    spinner.style.display = "block";
    error.style.display = "none";

    try {
        const url = state.editingId
            ? "/api/leads/" + state.editingId
            : "/api/leads";

        const response = await fetch(url, {
            method: state.editingId ? "PUT" : "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error("Не удалось сохранить лид");
        }

        closeDrawer();
        await loadLeads();
    } catch (e) {
        error.textContent = e.message;
        error.style.display = "block";
    } finally {
        saveButton.disabled = false;
        spinner.style.display = "none";
    }
}

async function deleteLead(leadId) {
    const response = await fetch("/api/leads/" + leadId, {
        method: "DELETE"
    });

    if (!response.ok) {
        return;
    }

    await loadLeads();
}

function renderToolbar() {
    const toolbar = document.getElementById("toolbar");
    toolbar.innerHTML = "";

    addFilterButton(toolbar, "all", "Все");
    addFilterButton(toolbar, "telegram", "Telegram");

    state.tags.forEach(tag => {
        addFilterButton(toolbar, "tag:" + tag.name, tag.name);
    });
}

function addFilterButton(toolbar, value, label) {
    const button = document.createElement("button");
    button.className = "filter" + (state.filter === value ? " active" : "");
    button.textContent = label;
    button.onclick = () => filterLeads(value);
    toolbar.appendChild(button);
}

function filterLeads(filter) {
    state.filter = filter;
    renderToolbar();
    renderLeads();
}

function renderLeads() {
    const table = document.getElementById("leadsTable");
    const empty = document.getElementById("empty");

    table.innerHTML = "";

    const visible = state.leads.filter(lead => {
        if (state.filter === "all") {
            return true;
        }

        if (state.filter === "telegram") {
            return lead.source === "telegram";
        }

        if (state.filter.startsWith("tag:")) {
            return (lead.tags || []).includes(state.filter.slice(4));
        }

        return true;
    });

    visible.forEach(lead => {
        const row = document.createElement("tr");

        const tagsHtml = (lead.tags || [])
            .map(tag => '<span class="tag ' + tagClass(tag) + '">' + escapeHtml(tag) + '</span>')
            .join("");

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
            <td><div class="tags">${tagsHtml}</div></td>
            <td>
                <div class="actions">
                    <button class="row-action edit">✎</button>
                    <button class="row-action delete">×</button>
                </div>
            </td>
        `;

        row.querySelector(".edit").onclick = () => openEditLead(lead.id);
        row.querySelector(".delete").onclick = () => deleteLead(lead.id);

        table.appendChild(row);
    });

    empty.style.display = visible.length ? "none" : "block";
    document.getElementById("totalCount").textContent = state.leads.length;
    document.getElementById("telegramCount").textContent =
        state.leads.filter(lead => lead.source === "telegram").length;
}

function tagClass(tag) {
    const value = tag.toLowerCase();

    if (value.includes("горяч")) return "hot";
    if (value.includes("ai")) return "ai";
    if (value.includes("telegram")) return "telegram";
    if (value.includes("нов")) return "new";

    return "";
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
