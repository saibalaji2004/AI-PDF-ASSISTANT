import {

    BrowserRouter,

    Routes,

    Route,

    Navigate

} from "react-router-dom";

import Login from "./pages/Login";

import Signup from "./pages/Signup";

import ChatPage from "./pages/ChatPage";


// =====================================
// Protected Route
// =====================================

function ProtectedRoute({

    children
}) {

    const token = localStorage.getItem(
        "token"
    );

    if (!token) {

        return <Navigate to="/" />;
    }

    return children;
}


// =====================================
// App
// =====================================

function App() {

    return (

        <BrowserRouter>

            <Routes>

                {/* =====================
                    Login
                ====================== */}

                <Route

                    path="/"

                    element={<Login />}
                />

                {/* =====================
                    Signup
                ====================== */}

                <Route

                    path="/signup"

                    element={<Signup />}
                />

                {/* =====================
                    Protected Chat
                ====================== */}

                <Route

                    path="/chat"

                    element={

                        <ProtectedRoute>

                            <ChatPage />

                        </ProtectedRoute>
                    }
                />

            </Routes>

        </BrowserRouter>
    );
}

export default App;