async function handleAuth(url, data, isRegister = false) {
    const msgDiv = document.getElementById('msg');
    const btn = document.querySelector('.cta-btn');
    
    // Reset
    msgDiv.textContent = "";
    msgDiv.className = "message";
    btn.disabled = true;
    btn.textContent = "Processing...";

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();

        if (response.ok) {
            msgDiv.textContent = result.message;
            msgDiv.className = "message success";
            
            setTimeout(() => {
                if (isRegister) {
                    window.location.href = "/login"; // Go to login after sign up
                } else {
                    alert("Login Successful! Redirecting to Dashboard...");
                    window.location.href = "/dashboard";
                }
            }, 1500);
        } else {
            msgDiv.textContent = result.message;
            msgDiv.className = "message error";
            btn.disabled = false;
            btn.textContent = isRegister ? "Sign Up" : "Log In";
        }
    } catch (error) {
        console.error(error);
        msgDiv.textContent = "Server error. Please try again.";
        msgDiv.className = "message error";
        btn.disabled = false;
        btn.textContent = isRegister ? "Sign Up" : "Log In";
    }
}