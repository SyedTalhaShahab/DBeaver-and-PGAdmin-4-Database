window.onload = function () {
    create_the_database();
    loadInitialEntries();
};

function handleResponse(responseData, isDeleteOperation = false) {
    console.log('Backend says:', responseData);
    const outputElement = document.getElementById();
    outputElement.textContent = JSON.stringify(responseData);
    outputElement.style.display = 'block'; // Ensure the element is visible
    if (isDeleteOperation) {
        const outputElementTop = document.getElementById("response-output-hidden-top");
        outputElementTop.style.display = 'none'; // Hide the top response element
        const outputElementBottom = document.getElementById("response-output-hidden-bottom");
        outputElementBottom.style.display = 'none'; // Hide the top response element
    }
}
async function create_the_database() {
    try {
        const response = await fetch('http://localhost:5000/api/create_database', {
            method: 'GET',
        });
        const responseData = await response.json();
        console.log('Backend says:', responseData);

        // Display the response in the message box
        const messageBox = document.getElementById('message_box');
        messageBox.textContent = JSON.stringify(responseData);
        messageBox.style.display = 'block';

        // Hide the top response element
        const outputElementTop = document.getElementById('response-output-hidden-top');
        outputElementTop.style.display = "block";

        // Hide the bottom response element
        const outputElementBottom = document.getElementById('response-output-hidden-bottom');
        outputElementBottom.style.display = 'none';

        // Display movies if received data exists
        if (responseData && responseData.received_data) {
            displayMovies(responseData.received_data, 'response-output-hidden-top');
        }
    } catch (error) {
        console.log('   *Error on GET request for create_database:', error);
    }
}

async function delete_the_database() {
    try {
        const response = await fetch('http://localhost:5000/api/delete_database', {
            method: 'GET',
        });
        const responseData = await response.json();
        console.log('Backend says:', responseData);

        // Display the response in the message box
        const messageBox = document.getElementById('message_box');
        messageBox.textContent = JSON.stringify(responseData);
        messageBox.style.display = 'block';

        // Hide the top response element
        const outputElementTop = document.getElementById('response-output-hidden-top');
        outputElementTop.style.display = 'none';

        // Hide the bottom response element
        const outputElementBottom = document.getElementById('response-output-hidden-bottom');
        outputElementBottom.style.display = 'none';
    } catch (error) {
        console.log('   *Error on GET request for delete_database:', error);
    }
}


async function loadInitialEntries() {
    const data = {
        title: '',
        major_genre: '',
        alphabetSort: 'ascending',
        releaseDate: '',
        Number_of_Items: 10,
        rotten_tomatoes_rating: 90,
    };
    try {
        // This should be a POST request
        const response = await fetch('http://localhost:5000/api/filters_endpoint', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),  // Send the data in the body as JSON
        });
        const responseData = await response.json();
        console.log('Backend says:', responseData);
        // Display the response data in both HTML elements
        const outputElement1 = document.getElementById('response-output-hidden-top');
        outputElement1.textContent = JSON.stringify(responseData);
        // Show both output elements
        outputElement1.style.display = 'block';
        // Call the displayMovies function with the received data
        if (responseData && responseData.received_data) {
            displayMovies(responseData.received_data, 'response-output-hidden-top');
        }
    } catch (error) {
        console.log('   *Error on GET request for loadInitialEntries:', error);
    }
}


async function submit_button() {
    const title = document.getElementById("title").value;
    const major_genre = document.getElementById("major_genre").value;
    const alphabetSort = document.getElementById("alphabetSort").value;
    const releaseDate = document.getElementById("release_date").value;
    const Number_of_Items = document.getElementById("Number_of_Items").value;
    const rotten_tomatoes_rating = document.getElementById("rotten_tomatoes_rating").value;
    if (rotten_tomatoes_rating.toLowerCase() === "nan" || isNaN(rotten_tomatoes_rating)) {
        rotten_tomatoes_rating = 0;
    }
    const data = {
        title: title,
        major_genre: major_genre,
        alphabetSort: alphabetSort,
        releaseDate: releaseDate,
        Number_of_Items: Number_of_Items,
        rotten_tomatoes_rating: parseFloat(rotten_tomatoes_rating), // Ensure it's a number
    };
    try {
        const response = await fetch('http://localhost:5000/api/filters_endpoint', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),  // Send the data in the body as JSON
        });
        const responseData = await response.json();
        console.log('Backend says:', responseData);

        if (responseData === "Create the database before searching.") {
            const messageBox = document.getElementById('message_box');
            messageBox.textContent = JSON.stringify(responseData);
            messageBox.style.display = 'block';
        }
        else if (responseData === "No entries found.") {
            const messageBox = document.getElementById('message_box');
            messageBox.textContent = JSON.stringify(responseData);
            messageBox.style.display = 'block';
        }
        else {
            if (responseData && responseData.received_data) {
                console.log('Backend says received_data.received_data:', responseData.received_data);
                console.log("works");
                document.getElementById("response-output-hidden-bottom").style.display = 'block'; // Show bottom element
                displayMovies(responseData.received_data, 'response-output-hidden-bottom'); // Use the displayMovies function to render the movies

            }
        }

    } catch (error) {
        console.log('   *Error on GET request for submit_button:', error);
    }
}

function displayMovies(movies, elementId) {
    const outputElement = document.getElementById(elementId);
    outputElement.textContent = ''; // Clear raw output
    movies.forEach(movie => {
        const button = document.createElement('button');
        button.type = 'button'; // Prevents the button from submitting a form

        // Set initial button text (movie title)
        button.textContent = movie.title || 'N/A';
        // Add a click event listener to toggle detailed info
        button.addEventListener('click', () => {
            if (button.getAttribute('data-expanded') === 'true') {
                // Collapse back to title
                button.textContent = movie.title || 'N/A';
                button.setAttribute('data-expanded', 'false');
            } else {
                // Expand to show details
                button.textContent = `
                    ${movie.title || 'N/A'}
                    Major Genre: ${movie.major_genre || 'N/A'}
                    Director: ${movie.director || 'N/A'}
                    Release Date: ${movie.release_date || 'N/A'}
                    IMDb Rating: ${movie.imdb_rating || 'N/A'}
                    Creative Type: ${movie.creative_type || 'N/A'}
                    Distributor: ${movie.distributor || 'N/A'}
                    ID: ${movie.id || 'N/A'}
                    IMDB Votes: ${movie.imdb_votes || 'N/A'}
                    Production Budget: ${movie.production_budget || 'N/A'}
                    Rotten Tomatoes Rating: ${movie.rotten_tomatoes_rating || 'N/A'}
                    Source: ${movie.source || 'N/A'}
                    US Gross: ${movie.us_gross || 'N/A'}
                    Worldwide Gross: ${movie.worldwide_gross || 'N/A'}
                `.trim();
                button.setAttribute('data-expanded', 'true');
            }
        });
        outputElement.appendChild(button);
    });
}