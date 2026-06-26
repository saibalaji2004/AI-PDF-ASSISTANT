import { useState } from "react";

import { useNavigate } from "react-router-dom";

import API from "../services/api";

import "../styles/auth.css";

function Login() {

    const navigate = useNavigate();

    const [email, setEmail] =
        useState("");

    const [password, setPassword] =
        useState("");

    const [message, setMessage] =
        useState("");

    // =========================
    // Handle Login
    // =========================

    const handleLogin = async () => {

        try {

            const response =
                await API.post(

                    "/login",

                    {
                        email,
                        password
                    }
                );

            // =====================
            // Save Token
            // =====================

            localStorage.setItem(

                "token",

                response.data.token
            );

            localStorage.setItem(

                "user",

                JSON.stringify(
                    response.data.user
                )
            );

            setMessage(
                "Login successful"
            );

            // =====================
            // Redirect
            // =====================

            navigate("/chat");

        } catch (error) {

            console.log(error);

            setMessage(
                "Invalid credentials"
            );
        }
    };

    return (

        <div className="auth-container">

            <div className="auth-card">

                <h1>

                    Login

                </h1>

                <input

                    type="email"

                    placeholder="Email"

                    value={email}

                    onChange={(e) =>

                        setEmail(
                            e.target.value
                        )
                    }
                />

                <input

                    type="password"

                    placeholder="Password"

                    value={password}

                    onChange={(e) =>

                        setPassword(
                            e.target.value
                        )
                    }
                />

                <button
                    onClick={handleLogin}
                >

                    Login

                </button>

                <p>

                    {message}

                </p>

                <p>

                    Don't have account?

                    {" "}

                    <span
                        className="auth-link"
                        onClick={() =>
                            navigate("/signup")
                        }
                    >

                        Signup

                    </span>

                </p>

            </div>

        </div>
    );
}

export default Login;