document.addEventListener('DOMContentLoaded', function() {
    const captureButton = document.getElementById('captureButton');
    const countdownDisplay = document.getElementById('captureCountdown');
    const wineInputForm = document.getElementById('wineInputForm');

    captureButton.addEventListener('click', function(event) {
        event.preventDefault(); // Prevent the default form submission


    


    //    // Function to check if all required fields are filled
    //function areFieldsFilled() {
       // const requiredInputs = wineInputForm.querySelectorAll('input[required]');
      //  const characteristicsInputs = wineInputForm.querySelectorAll('input[name="light"], input[name="bold"], input[name="smooth"], input[name="dry"], input[name="soft"], input[name="acidic"], input[name="tannic"], input[name="sweet"]');

        // Check if all required inputs are filled
       // return Array.from(requiredInputs).every(input => input.value.trim() !== '') &&
      //         Array.from(characteristicsInputs).every(input => input.value.trim() !== '');
    //}


        // Check if all required fields are filled
        const requiredFields = wineInputForm.querySelectorAll('input[required]');
        let allFieldsFilled = true;
        
        requiredFields.forEach(function(field) {
            if (!field.value) {
                allFieldsFilled = false;
            }
        });

        if (!allFieldsFilled) {
            alert("Please fill all required fields.");
            return; // Exit if not all required fields are filled
        }

        // Start the countdown
        let countdown = 10;
        countdownDisplay.innerText = countdown;

        const countdownInterval = setInterval(function() {
            countdown--;
            countdownDisplay.innerText = countdown;

            // If countdown reaches 0, clear the interval
            if (countdown <= 0) {
                clearInterval(countdownInterval);
                // Submit the form here
                wineInputForm.submit(); // Submit the form when countdown ends
            }
        }, 1000); // Decrease countdown every second

        // Submit the form immediately
        wineInputForm.submit(); // This triggers the sensor capture immediately
    });
});
