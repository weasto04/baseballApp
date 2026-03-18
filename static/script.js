const yearSelect = document.getElementById("year-select");
const statusText = document.getElementById("status-text");

function setStatus(message, isError = false) {
	statusText.textContent = message;
	statusText.classList.toggle("error", isError);
}

async function loadYears() {
	setStatus("Fetching seasons...");

	try {
		const response = await fetch("/years");

		if (!response.ok) {
			throw new Error(`Request failed with status ${response.status}`);
		}

		const years = await response.json();

		if (!Array.isArray(years) || years.length === 0) {
			yearSelect.innerHTML = "<option>No years available</option>";
			yearSelect.disabled = true;
			setStatus("No season years were found in the database.");
			return;
		}

		yearSelect.innerHTML = years
			.map((year) => `<option value="${year}">${year}</option>`)
			.join("");

		yearSelect.disabled = false;
		setStatus(`Loaded ${years.length} seasons.`);
	} catch (error) {
		yearSelect.innerHTML = "<option>Unable to load years</option>";
		yearSelect.disabled = true;
		setStatus("Could not load years. Please try again.", true);
		console.error(error);
	}
}

loadYears();
