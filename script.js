document.querySelector(".booking form").addEventListener("submit", async function(event) {
    event.preventDefault();

    const name = document.querySelector("#name").value;
    const service = document.querySelector("#service").value;
    const date = document.querySelector("#date").value;
    const time = document.querySelector("#time").value;

    const response = await fetch("/book", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name: name,
            service: service,
            date: date,
            time: time
        })
    });

    const result = await response.json();

    alert(result.message);

    this.reset();
});