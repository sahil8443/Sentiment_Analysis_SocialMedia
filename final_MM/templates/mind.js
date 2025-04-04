document.addEventListener("DOMContentLoaded", async function () {
    const ctx = document.getElementById("sentimentChart").getContext("2d");
    const errorMessage = document.getElementById("error-message");
    const notificationContainer = document.querySelector(".card-body"); // Right sidebar notification area

    try {
        // ✅ Fetch Data from Flask API
        let response = await fetch("http://127.0.0.1:5000/analyze"); // Ensure Flask is running!
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        let data = await response.json();

        if (data.length < 2) {
            throw new Error("Not enough data to compare sentiment levels.");
        }

        // ✅ Extract Labels (Dates) & Sentiment Scores
        let labels = data.map(post => new Date(post.timestamp).toLocaleDateString()); // Convert timestamp to readable date
        let sentimentData = data.map(post => post.sentiment_score);

        // ✅ Determine Alert Message
        let latestSentiment = sentimentData[0]; // Most recent sentiment
        let previousSentiment = sentimentData[1]; // Second most recent sentiment
        let threshold = 0.2; // Adjust this threshold for sensitivity

        // Clear previous notifications
        notificationContainer.innerHTML = "";

        if (latestSentiment - previousSentiment > threshold) {
            // 🔴 ALERT IF SENTIMENT INCREASED SIGNIFICANTLY
            notificationContainer.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    ⚠️ Alert: Sudden increase in sentiment level detected!
                </div>`;
        } else if (previousSentiment - latestSentiment > threshold) {
            // 🔵 ALERT IF SENTIMENT DECREASED SIGNIFICANTLY
            notificationContainer.innerHTML = `
                <div class="alert alert-warning" role="alert">
                    ⚠️ Warning: Sentiment level dropped significantly.
                </div>`;
        } else {
            // 🟢 STABLE SENTIMENT
            notificationContainer.innerHTML = `
                <div class="alert alert-info" role="alert">
                    ℹ️ Sentiment level is stable.
                </div>`;
        }

        // ✅ Create Line Chart
        new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "Sentiment Score",
                    data: sentimentData,
                    backgroundColor: "rgba(75, 192, 192, 0.2)",
                    borderColor: "rgba(75, 192, 192, 1)",
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: false // Allow positive & negative values
                    }
                }
            }
        });

    } catch (error) {
        console.error("⚠️ Error: Unable to load sentiment data.", error);
        notificationContainer.innerHTML = `<div class="alert alert-danger">⚠️ Error fetching sentiment data.</div>`;
        errorMessage.textContent = "⚠️ Error: Unable to load sentiment data.";
    }
});
