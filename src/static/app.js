document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Build participants list with delete buttons
        const participantsHtml = details.participants
          .map(
            (participant) =>
              `<li data-activity="${encodeURIComponent(name)}" data-email="${encodeURIComponent(
                participant
              )}" class="participants-list-item"><span class="participant">${participant}</span><button class="delete-btn" title="Unregister">&times;</button></li>`
          )
          .join("");

        activityCard.innerHTML = `
            <h4>${name}</h4>
            <p>${details.description}</p>
            <p><strong>Schedule:</strong> ${details.schedule}</p>
            <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
            <p><strong>Participants:</strong></p>
            <ul class="participants-list">
              ${participantsHtml}
            </ul>
          `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Delegate click events for delete buttons to the activitiesList container
  activitiesList.addEventListener("click", async (e) => {
    const btn = e.target.closest(".delete-btn");
    if (!btn) return;

    const li = btn.closest("li");
    if (!li) return;

    const activityName = decodeURIComponent(li.getAttribute("data-activity"));
    const email = decodeURIComponent(li.getAttribute("data-email"));

    if (!activityName || !email) return;

    // Ask for confirmation
    const ok = confirm(`Unregister ${email} from ${activityName}?`);
    if (!ok) return;

    try {
      const response = await fetch(`/activities/${encodeURIComponent(activityName)}/participants`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      const result = await response.json();

      if (response.ok) {
        // Remove the participant list item from the DOM
        li.remove();
        // Optionally update availability text - simple approach: refetch activities
        // For now, just show a small success message
        messageDiv.textContent = result.message || `Unregistered ${email} from ${activityName}`;
        messageDiv.className = "success";
        messageDiv.classList.remove("hidden");
        setTimeout(() => messageDiv.classList.add("hidden"), 4000);
      } else {
        messageDiv.textContent = result.detail || result.message || "Failed to unregister participant.";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
      }
    } catch (error) {
      console.error("Error unregistering participant:", error);
      messageDiv.textContent = "Failed to unregister participant. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
    }
  });

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh activities so the UI reflects the newly-registered participant
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
