document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // Trip Planning Form
    // ==========================================

    const tripForm = document.querySelector(".trip-form");

    if (!tripForm) {
        return;
    }


    // ==========================================
    // Date Elements
    // ==========================================

    const startDate = document.querySelector("#start_date");
    const endDate = document.querySelector("#end_date");
    const tripDaysDisplay = document.querySelector("#trip-days");


    // ==========================================
    // Set Minimum Start Date
    // ==========================================

    const today = new Date();

    const year = today.getFullYear();
    const month = String(
        today.getMonth() + 1
    ).padStart(2, "0");

    const day = String(
        today.getDate()
    ).padStart(2, "0");

    const todayString =
        `${year}-${month}-${day}`;

    if (startDate) {
        startDate.min = todayString;
    }


    // ==========================================
    // Update End Date
    // ==========================================

    function updateEndDate() {

        if (!startDate || !endDate) {
            return;
        }

        if (!startDate.value) {
            endDate.min = todayString;
            return;
        }

        endDate.min = startDate.value;

        if (
            endDate.value &&
            endDate.value < startDate.value
        ) {
            endDate.value = "";
        }

        updateTripDays();
    }


    // ==========================================
    // Calculate Trip Days
    // ==========================================

    function updateTripDays() {

        if (
            !startDate ||
            !endDate ||
            !tripDaysDisplay
        ) {
            return;
        }

        if (
            !startDate.value ||
            !endDate.value
        ) {
            tripDaysDisplay.textContent = "";
            return;
        }

        const start = new Date(
            startDate.value
        );

        const end = new Date(
            endDate.value
        );

        const difference =
            end.getTime() - start.getTime();

        const days =
            Math.floor(
                difference / (1000 * 60 * 60 * 24)
            ) + 1;

        if (days <= 0) {
            tripDaysDisplay.textContent = "";
            return;
        }

        if (days > 30) {
            tripDaysDisplay.textContent =
                "Maximum trip duration is 30 days.";
            tripDaysDisplay.classList.add(
                "trip-days-error"
            );
            return;
        }

        tripDaysDisplay.classList.remove(
            "trip-days-error"
        );

        tripDaysDisplay.textContent =
            `${days} day${days === 1 ? "" : "s"} trip`;
    }


    // ==========================================
    // Date Events
    // ==========================================

    if (startDate) {
        startDate.addEventListener(
            "change",
            updateEndDate
        );
    }

    if (endDate) {
        endDate.addEventListener(
            "change",
            updateTripDays
        );
    }


    // ==========================================
    // Interest Cards
    // ==========================================

    const interestCards =
        document.querySelectorAll(
            ".interest-card"
        );

    interestCards.forEach(function (card) {

        card.addEventListener(
            "click",
            function () {

                const checkbox =
                    card.querySelector(
                        'input[type="checkbox"]'
                    );

                if (!checkbox) {
                    return;
                }

                checkbox.checked =
                    !checkbox.checked;

                card.classList.toggle(
                    "selected",
                    checkbox.checked
                );
            }
        );


        // Keyboard Support

        card.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Enter" ||
                    event.key === " "
                ) {

                    event.preventDefault();

                    const checkbox =
                        card.querySelector(
                            'input[type="checkbox"]'
                        );

                    if (!checkbox) {
                        return;
                    }

                    checkbox.checked =
                        !checkbox.checked;

                    card.classList.toggle(
                        "selected",
                        checkbox.checked
                    );
                }

            }
        );

    });


    // ==========================================
    // Form Validation
    // ==========================================

    tripForm.addEventListener(
        "submit",
        function (event) {

            let isValid = true;

            const source =
                document.querySelector("#source");

            const destination =
                document.querySelector("#destination");

            const travellers =
                document.querySelector("#travellers");

            const budget =
                document.querySelector("#budget");


            // Source

            if (
                !source ||
                !source.value.trim()
            ) {
                isValid = false;

                showValidationMessage(
                    source,
                    "Please enter your starting location."
                );
            }


            // Destination

            if (
                !destination ||
                !destination.value
            ) {
                isValid = false;

                showValidationMessage(
                    destination,
                    "Please select a destination."
                );
            }


            // Start Date

            if (
                !startDate ||
                !startDate.value
            ) {
                isValid = false;

                showValidationMessage(
                    startDate,
                    "Please select a start date."
                );
            }


            // End Date

            if (
                !endDate ||
                !endDate.value
            ) {
                isValid = false;

                showValidationMessage(
                    endDate,
                    "Please select an end date."
                );
            }


            // Date Range

            if (
                startDate &&
                endDate &&
                startDate.value &&
                endDate.value &&
                endDate.value < startDate.value
            ) {
                isValid = false;

                showValidationMessage(
                    endDate,
                    "End date cannot be before start date."
                );
            }


            // Maximum Trip Duration

            if (
                startDate &&
                endDate &&
                startDate.value &&
                endDate.value
            ) {

                const start =
                    new Date(startDate.value);

                const end =
                    new Date(endDate.value);

                const difference =
                    end.getTime() - start.getTime();

                const days =
                    Math.floor(
                        difference /
                        (1000 * 60 * 60 * 24)
                    ) + 1;

                if (days > 30) {

                    isValid = false;

                    showValidationMessage(
                        endDate,
                        "Trip cannot be longer than 30 days."
                    );
                }
            }


            // Travellers

            if (
                !travellers ||
                parseInt(travellers.value, 10) <= 0
            ) {
                isValid = false;

                showValidationMessage(
                    travellers,
                    "Number of travellers must be at least 1."
                );
            }


            // Budget

            if (
                !budget ||
                parseFloat(budget.value) <= 0
            ) {
                isValid = false;

                showValidationMessage(
                    budget,
                    "Please enter a valid budget."
                );
            }


            // Stop Submission

            if (!isValid) {
                event.preventDefault();

                const firstInvalid =
                    tripForm.querySelector(
                        ".input-error"
                    );

                if (firstInvalid) {
                    firstInvalid.focus();
                }

                return;
            }


            // Loading State

            const submitButton =
                tripForm.querySelector(
                    'button[type="submit"]'
                );

            if (submitButton) {

                submitButton.disabled = true;

                submitButton.dataset.originalText =
                    submitButton.textContent;

                submitButton.textContent =
                    "Creating Your Trip...";
            }

        }
    );


    // ==========================================
    // Validation Message
    // ==========================================

    function showValidationMessage(
        element,
        message
    ) {

        if (!element) {
            return;
        }

        element.classList.add(
            "input-error"
        );

        element.setAttribute(
            "aria-invalid",
            "true"
        );

        let messageElement =
            element.parentElement.querySelector(
                ".field-error"
            );

        if (!messageElement) {

            messageElement =
                document.createElement("small");

            messageElement.className =
                "field-error";

            element.parentElement.appendChild(
                messageElement
            );
        }

        messageElement.textContent =
            message;


        // Remove error when user changes input

        element.addEventListener(
            "input",
            function clearError() {

                element.classList.remove(
                    "input-error"
                );

                element.removeAttribute(
                    "aria-invalid"
                );

                if (messageElement) {
                    messageElement.remove();
                }

                element.removeEventListener(
                    "input",
                    clearError
                );

            }
        );

    }


    // ==========================================
    // Initial Setup
    // ==========================================

    updateEndDate();
    updateTripDays();

    console.log(
        "Safar Setu Trip Planner initialized."
    );

});