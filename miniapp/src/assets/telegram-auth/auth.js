function onTelergamAuth(user){
    fetch("http://localhost:8000", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(user)
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("user-info").innerHTML = `
          <p>ID: ${data.id}</p>
          <p>Username: ${data.username}</p>
          <p>First Name: ${data.first_name}</p>
          <img src="${data.photo_url}" alt="User Photo" />
        `;
    })
}

const tgScript = document.createElement("script")
    tgScript.src = "https://telegram.org/js/telegram-widget.js?7";
    tgScript.setAttribute("data-telegram-login", "temalal_bot");
    tgScript.setAttribute("data-userpic", "false");
    tgScript.setAttribute("data-auth-url", "javascript:onTelegramAuth");
    tgScript.setAttribute("data-request-access", "write");
    tgScript.async = true;
    document.body.appendChild(tgScript);