// ================= SIGNUP =================
function signupUser(event){
    event.preventDefault();

    const name = document.getElementById("signup-name").value.trim();
    const email = document.getElementById("signup-email").value.trim();
    const password = document.getElementById("signup-password").value;

    const signupMessage = document.getElementById("signup-message");

    if(!name || !email || !password){
        signupMessage.textContent = "All fields are required!";
        signupMessage.style.color = "red";
        return;
    }

    const users = JSON.parse(localStorage.getItem("users") || "{}");

    if(users[email]){
        signupMessage.textContent = "Email already registered!";
        signupMessage.style.color = "red";
        return;
    }

    users[email] = { name, email, password };
    localStorage.setItem("users", JSON.stringify(users));

    signupMessage.textContent = "Account created successfully! Redirecting to login...";
    signupMessage.style.color = "green";

    setTimeout(() => {
        window.location.href = "login.html";
    }, 1500);
}

// ================= LOGIN =================
function loginUser(event){
    event.preventDefault();

    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;

    const loginMessage = document.getElementById("login-message");
    const users = JSON.parse(localStorage.getItem("users") || "{}");

    if(!users[email] || users[email].password !== password){
        loginMessage.textContent = "Invalid email or password!";
        loginMessage.style.color = "red";
        return;
    }

    // ✅ SAVE LOGGED IN USER
    localStorage.setItem("loggedInUser", JSON.stringify(users[email]));

    // ✅ REDIRECT TO PREDICTION PAGE
    window.location.href = "predict.html";
}

// ================= LOGOUT =================
function logoutUser(){
    localStorage.removeItem("loggedInUser");
    window.location.href = "login.html";
}

// ================= PREDICT PAGE ACCESS =================
function handlePredictPage() {
    const user = JSON.parse(localStorage.getItem("loggedInUser"));

    const predictContainer = document.getElementById("predictContainer");
    const welcomeBox = document.getElementById("welcomeBox");

    if(user){
        welcomeBox.innerHTML = `🌿 Welcome, <b>${user.name}</b>`;
        predictContainer.style.display = "block";
    } else {
        welcomeBox.innerHTML = `🔒 Please <a href="login.html">Login</a> to predict plant disease`;
        predictContainer.style.display = "none";
    }
}

// ================= PREDICTION =================
async function predictDisease(event) {
    event.preventDefault();

    const fileInput = document.getElementById("leaf-image");
    const resultDiv = document.getElementById("result");
    const preview = document.getElementById("preview");

    if (!fileInput.files.length) {
        resultDiv.innerHTML = "❌ Please select an image";
        return;
    }

    const file = fileInput.files[0];

    preview.src = URL.createObjectURL(file);
    preview.style.display = "block";
    resultDiv.innerHTML = "";
    resultDiv.innerHTML = "<p>⏳ Analyzing image...</p>";


  

    const formData = new FormData();
    formData.append("file", file); // 🔥 MUST be "file"

    try {
        const response = await fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Server error");
        }

        const data = await response.json();
        console.log("Prediction response:", data);

        // FORCE RESULT VISIBLE
        resultDiv.style.display = "block";
        resultDiv.style.opacity = "1";
        resultDiv.style.visibility = "visible";

        resultDiv.innerHTML = `
        <h2>✅ Prediction Result</h2>
        <p><b>Plant:</b> ${data.plant}</p>
        <p><b>Disease:</b> ${data.disease}</p>
        <p><b>Confidence:</b> ${data.confidence}</p>
        <p><b>Cause:</b> ${data.cause}</p>
        <p><b>Remedy:</b> ${data.remedy}</p>
    `;

        resultDiv.scrollIntoView({ behavior: "smooth" });


    } catch (error) {
        console.error(error);
        resultDiv.innerHTML = "❌ Prediction failed. Check backend.";
    }
}
