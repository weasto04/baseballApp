const LEAGUE_NAMES = {
    AL: "American League",
    NL: "National League",
    AA: "American Association",
    UA: "Union Association",
    PL: "Players' League",
    FL: "Federal League",
    NA: "National Association",
};

const DIVISION_NAMES = {
    E: "East",
    C: "Central",
    W: "West",
};

function leagueName(code) {
    return LEAGUE_NAMES[code] || code || "Other";
}

function divisionName(code) {
    return DIVISION_NAMES[code] || code || "";
}

function buildRosterHTML(players) {
    const container = document.getElementById("roster-container");

    if (!players.length) {
        container.innerHTML = '<p class="loading">No players found for this team.</p>';
        return;
    }

    const list = document.createElement("ul");
    list.className = "roster-list";

    for (const player of players) {
        const li = document.createElement("li");
        const first = player.first_name || "";
        const last = player.last_name || "";
        li.textContent = `${first} ${last}`.trim() || "Unknown Player";
        list.appendChild(li);
    }

    container.innerHTML = "";
    container.appendChild(list);
}

async function loadRoster(year, teamId, teamName) {
    const rosterSection = document.getElementById("roster-section");
    const rosterHeading = document.getElementById("roster-heading");
    const rosterContainer = document.getElementById("roster-container");

    rosterHeading.textContent = `${year} ${teamName} Roster`;
    rosterContainer.innerHTML = '<p class="loading">Loading roster...</p>';
    rosterSection.hidden = false;

    try {
        const response = await fetch(`/roster?year=${year}&team_id=${encodeURIComponent(teamId)}`);
        const players = await response.json();
        buildRosterHTML(players);
    } catch {
        rosterContainer.innerHTML = '<p class="loading">Failed to load roster</p>';
    }
}

function buildTeamsHTML(teams, year) {
    // Group by league, then division
    const grouped = {};
    for (const t of teams) {
        const lg = t.league || "Other";
        const div = t.division || "";
        if (!grouped[lg]) grouped[lg] = {};
        if (!grouped[lg][div]) grouped[lg][div] = [];
        grouped[lg][div].push(t);
    }

    const container = document.getElementById("teams-container");
    container.innerHTML = "";

    const leagues = Object.keys(grouped).sort();

    for (const lg of leagues) {
        const leagueDiv = document.createElement("div");
        leagueDiv.className = "league-group";

        const lgHeader = document.createElement("h3");
        lgHeader.className = "league-header";
        lgHeader.textContent = leagueName(lg);
        leagueDiv.appendChild(lgHeader);

        const divisions = Object.keys(grouped[lg]).sort();
        const hasDivisions = !(divisions.length === 1 && divisions[0] === "");

        const divisionsRow = document.createElement("div");
        divisionsRow.className = "divisions-row";

        for (const div of divisions) {
            const divBlock = document.createElement("div");
            divBlock.className = "division-block";

            if (hasDivisions) {
                const divHeader = document.createElement("h4");
                divHeader.className = "division-header";
                divHeader.textContent = divisionName(div);
                divBlock.appendChild(divHeader);
            }

            const ul = document.createElement("ul");
            const teamsInDivision = grouped[lg][div].sort((a, b) => a.name.localeCompare(b.name));
            for (const team of teamsInDivision) {
                const li = document.createElement("li");
                li.className = "team-item";
                li.textContent = team.name;
                li.dataset.teamId = team.team_id;
                li.addEventListener("click", () => {
                    document
                        .querySelectorAll(".team-item.active")
                        .forEach((item) => item.classList.remove("active"));
                    li.classList.add("active");
                    loadRoster(year, team.team_id, team.name);
                });
                ul.appendChild(li);
            }
            divBlock.appendChild(ul);
            divisionsRow.appendChild(divBlock);
        }

        leagueDiv.appendChild(divisionsRow);
        container.appendChild(leagueDiv);
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    const select = document.getElementById("year-select");

    try {
        const response = await fetch("/years");
        const years = await response.json();

        select.innerHTML = '<option value="">-- Choose a season --</option>';
        years.forEach((year) => {
            const option = document.createElement("option");
            option.value = year;
            option.textContent = year;
            select.appendChild(option);
        });
        select.disabled = false;
    } catch {
        select.innerHTML = '<option value="">Failed to load seasons</option>';
    }

    select.addEventListener("change", async () => {
        const year = select.value;
        const section = document.getElementById("teams-section");
        const container = document.getElementById("teams-container");
        const heading = document.getElementById("teams-heading");
        const rosterSection = document.getElementById("roster-section");

        if (!year) {
            section.hidden = true;
            rosterSection.hidden = true;
            return;
        }

        container.innerHTML = '<p class="loading">Loading...</p>';
        heading.textContent = `${year} Season`;
        section.hidden = false;
        rosterSection.hidden = true;

        try {
            const response = await fetch(`/teams?year=${year}`);
            const teams = await response.json();
            buildTeamsHTML(teams, year);
        } catch {
            container.innerHTML = '<p class="loading">Failed to load teams</p>';
        }
    });
});
