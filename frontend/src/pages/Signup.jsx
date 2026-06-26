import { useState } from "react";

import { useNavigate } from "react-router-dom";

import API from "../services/api";

import "../styles/auth.css";

function Signup() {

    const navigate = useNavigate();

    const [username, setUsername] =
        useState("");

    const [email, setEmail] =
        useState("");

    const [password, setPassword] =
        useState("");

    const [message, setMessage] =
        useState("");

    // =========================
    // Handle Signup
    // =========================

    const handleSignup = async () => {

        try {

            const response =
                await API.post(

                    "/signup",

                    {
                        username,
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
                "Signup successful"
            );

            // =====================
            // Redirect
            // =====================

            navigate("/chat");

        } catch (error) {

            console.log(error);

            setMessage(
                "Signup failed"
            );
        }
    };

    return (

        <div className="auth-container">

            <div className="auth-card">

                <h1>

                    Signup

                </h1>

                <input

                    type="text"

                    placeholder="Username"

                    value={username}

                    onChange={(e) =>

                        setUsername(
                            e.target.value
                        )
                    }
                />

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
                    onClick={handleSignup}
                >

                    Signup

                </button>

                <p>

                    {message}

                </p>

                <p>

                    Already have account?

                    {" "}

                    <span
                        className="auth-link"
                        onClick={() =>
                            navigate("/")
                        }
                    >

                        Login

                    </span>

                </p>

            </div>

        </div>
    );
}

export default Signup;