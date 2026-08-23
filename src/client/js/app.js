
const message = document.getElementById("message");
const nameInput = document.getElementById("name");
const sendButton = document.getElementById("send");
const result = document.getElementById("result");

fetch("http://localhost:3000/api/health")
    .then(response => response.json())
    .then(data => {
        message.textContent = `Server status: ${data.status}`;
    })
    .catch(error => {
        console.error(error);
        message.textContent = "Server connection failed.";
    });

sendButton.addEventListener("click", () => {
    fetch("http://localhost:3000/api/hello", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name: nameInput.value
        })
    })
        .then(response => response.json())
        .then(data => {
            result.textContent = data.message;
        })
        .catch(error => {
            console.error(error);
            result.textContent = "Request failed.";
        });
});