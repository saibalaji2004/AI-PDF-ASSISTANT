import {

    useState,

    useEffect

} from "react";

import { useNavigate } from "react-router-dom";

import API from "../services/api";

import "../styles/app.css";

function ChatPage() {

    const navigate = useNavigate();

    // =========================
    // States
    // =========================

    const [file, setFile] =
        useState(null);

    const [uploadMessage, setUploadMessage] =
        useState("");

    const [question, setQuestion] =
        useState("");

    const [messages, setMessages] =
        useState([]);

    const [loading, setLoading] =
        useState(false);

    // =========================
    // Session State
    // =========================

    const [sessionId, setSessionId] =
        useState(null);

    const [chatSessions, setChatSessions] =
        useState([]);

    const [searchText, setSearchText] =
    useState("");

    const [sidebarOpen, setSidebarOpen] =
        useState(true);
    
    const [activeMenu, setActiveMenu] =
        useState(null);

    const [showRenameDialog, setShowRenameDialog] =
        useState(false);

    const [renameSessionId, setRenameSessionId] =
        useState(null);

    const [renameTitle, setRenameTitle] =
        useState("");

    // =========================
    // PDF Management
    // =========================

    const [uploadedPDFs, setUploadedPDFs] =
        useState([]);

    const [selectedPDF, setSelectedPDF] =
        useState("");

    // =========================
    // Load Sessions
    // =========================

    useEffect(() => {

        loadChatSessions();

    }, []);

    // =========================
    // Close Menu on Outside Click
    // =========================

    useEffect(() => {

        const closeMenu = (e) => {

            if (

                !e.target.closest(
                    ".chat-menu"
                )

            ) {

                setActiveMenu(null);

            }

        };

        document.addEventListener(
            "click",
            closeMenu
        );

        return () => {

            document.removeEventListener(
                "click",
                closeMenu
            );

        };

    }, []);

    // =========================
    // Fetch Sessions
    // =========================

    const loadChatSessions = async () => {

        try {

            const response =
                await API.get(
                    "/chat-sessions"
                );

            setChatSessions(
                response.data
            );

        } catch (error) {

            console.log(error);
        }
    };

    // =========================
    // Load Chat History
    // =========================

    const loadChatHistory = async (

        session
    ) => {

        try {

            const response =
                await API.get(

                    `/chat-history/${session.id}`
                );

            setMessages(

                response.data.messages
            );

            setSessionId(
                session.id
            );

            setSelectedPDF(
                session.pdf_name
            );

        } catch (error) {

            console.log(error);
        }
    };

    // =========================
    // Upload PDF
    // =========================

    const handleUpload = async () => {

        if (!file) {

            alert("Select PDF");

            return;
        }

        const formData = new FormData();

        formData.append(
            "file",
            file
        );

        try {

            setLoading(true);

            const response =
                await API.post(

                    "/upload",

                    formData,

                    {
                        headers: {
                            "Content-Type":
                            "multipart/form-data"
                        }
                    }
                );

            setUploadMessage(
                response.data.message
            );

            const uploadedPDF =
                response.data.uploaded_pdf;

            setUploadedPDFs((prev) => {

                if (
                    prev.includes(uploadedPDF)
                ) {

                    return prev;
                }

                return [

                    ...prev,

                    uploadedPDF
                ];
            });

            setSelectedPDF(
                uploadedPDF
            );

            setMessages([]);

            setSessionId(null);

            loadChatSessions();

        } catch (error) {

            console.log(error);

            setUploadMessage(
                "Upload failed"
            );

        } finally {

            setLoading(false);
        }
    };

    // =========================
    // Ask Question
    // =========================

    const handleAsk = async () => {

        if (!question.trim()) {

            return;
        }

        if (!selectedPDF) {

            alert(
                "Select PDF first"
            );

            return;
        }

        const userMessage = {

            role: "user",

            text: question
        };

        const updatedMessages = [

            ...messages,

            userMessage
        ];

        setMessages(
            updatedMessages
        );

        const aiMessage = {

            role: "ai",

            text: "",

            sources: []
        };

        setMessages((prev) => [

            ...prev,

            aiMessage
        ]);

        try {

            setLoading(true);

            // =====================
            // JWT TOKEN
            // =====================

            const token = localStorage.getItem(
                "token"
            );

            // =====================
            // STREAM REQUEST
            // =====================

            const response = await fetch(

                "http://127.0.0.1:8000/ask-stream",

                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                        "application/json",

                        "Authorization":
                        `Bearer ${token}`
                    },

                    body: JSON.stringify({

                        question:
                        question,

                        selected_pdf:
                        selectedPDF,

                        chat_history:
                        updatedMessages,

                        session_id:
                        sessionId
                    })
                }
            );

            const reader =
                response.body.getReader();

            const decoder =
                new TextDecoder();

            let streamedText = "";

            while (true) {

                const {

                    done,

                    value

                } = await reader.read();

                if (done) {

                    break;
                }

                streamedText +=
                    decoder.decode(value);

                setMessages((prev) => {

                    const updated = [...prev];

                    updated[
                        updated.length - 1
                    ] = {

                        role: "ai",

                        text: streamedText,

                        sources: []
                    };

                    return updated;
                });
            }

            // =====================
            // FETCH SOURCES
            // =====================

            const sourceResponse =
                await API.post(

                    "/ask",

                    {

                        question:
                        question,

                        selected_pdf:
                        selectedPDF,

                        chat_history:
                        updatedMessages,

                        session_id:
                        sessionId
                    }
                );

            if (

                sourceResponse.data.session_id
            ) {

                setSessionId(

                    sourceResponse.data.session_id
                );
            }

            loadChatSessions();

            // =====================
            // ATTACH SOURCES
            // =====================

            setMessages((prev) => {

                const updated = [...prev];

                updated[
                    updated.length - 1
                ] = {

                    role: "ai",

                    text: streamedText,

                    sources:
                    sourceResponse.data.sources
                };

                return updated;
            });

        } catch (error) {

            console.log(error);

        } finally {

            setLoading(false);

            setQuestion("");
        }
    };

    // =========================
    // Summarize PDF
    // =========================

    const handleSummarize = async () => {

        if (!selectedPDF) {

            alert(
                "Select PDF first"
            );

            return;
        }

        try {

            setLoading(true);

            const response =
                await API.post(

                    "/summarize",

                    {

                        question:
                        "summarize",

                        selected_pdf:
                        selectedPDF,

                        chat_history: [],

                        session_id:
                        sessionId
                    }
                );

            const summaryMessage = {

                role: "ai",

                text:
                response.data.summary,

                sources: []
            };

            setMessages((prev) => [

                ...prev,

                summaryMessage
            ]);

        } catch (error) {

            console.log(error);

        } finally {

            setLoading(false);
        }
    };

    // =========================
    // Logout
    // =========================

    const handleLogout = () => {

        localStorage.removeItem(
            "token"
        );

        localStorage.removeItem(
            "user"
        );

        navigate("/");
    };

    // =========================
    // UI
    // =========================

    return (

        <div
            style={{
                display: "flex",
                position: "relative"
            }}
        >

        <button

    onClick={() =>

        setSidebarOpen(
            !sidebarOpen
        )
    }

    style={{

        position: "fixed",

        top: "20px",

        left: sidebarOpen
            ? "250px"
            : "20px",

        zIndex: 1000,

        background: "#222",

        color: "white",

        border: "none",

        borderRadius: "5px",

        padding: "8px 12px",

        cursor: "pointer",

        transition: "0.3s"
    }}
> 
                {

                    sidebarOpen

                    ?

                    "☰ Hide"

                    :

                    "☰ Show"
                }

            </button>

            {/* SIDEBAR */}

            {
                sidebarOpen && (

                    <div
                        style={{
                    width: "300px",
                    padding: "20px",
                    borderRight:
                    "1px solid #333",
                    height: "100vh",
                    overflowY: "auto",
                    background: "#111"
                }}
            >

                <h2>

                    Previous Chats

                </h2>

                <input

    type="text"

    placeholder="🔍 Search chats..."

    value={searchText}

    onChange={(e) =>

        setSearchText(
            e.target.value
        )
    }

    style={{

        width: "100%",

        padding: "8px",

        marginBottom: "15px",

        borderRadius: "5px",

        border: "1px solid #555",

        background: "#222",

        color: "white"
    }}
/>

                <button
                    onClick={handleLogout}
                    style={{
                        marginBottom: "20px",
                        width: "100%"
                    }}
                >

                    Logout

                </button>

                {

                   chatSessions

.sort(

    (a, b) => {

        if (

            a.is_pinned === b.is_pinned

        ) {

            return b.id - a.id;

        }

        return b.is_pinned - a.is_pinned;

    }

)

.filter((session) => {

    const title =

        (session.title || "").toLowerCase();

    const pdf =

        (session.pdf_name || "").toLowerCase();

    const content =

        (session.search_text || "").toLowerCase();

    const search =

        searchText.toLowerCase();

    return (

        title.includes(search)

        ||

        pdf.includes(search)

        ||

        content.includes(search)
    );

})
                        .map(

                        (session) => (

                            <div

                                key={session.id}

                                onClick={() =>

                                    loadChatHistory(
                                        session
                                    )
                                }

                                style={{

    padding: "10px",

    marginBottom: "10px",

    background:

        session.id === sessionId

        ?

        "#2952cc"

        :

        "#1f1f1f",

    cursor: "pointer",

    borderRadius: "8px",

    position: "relative",

    transition: "0.2s ease"
}}
                            >

                                <div

style={{

display:"flex",

justifyContent:"space-between",

alignItems:"center",

width:"100%"

}}
>

                                    <strong>

                                        {

                                            session.title

                                            ||

                                            session.pdf_name

                                        }

                                    </strong>

                                    <button

                                        className="chat-menu"

                                        onClick={(e) => {

                                            e.stopPropagation();

                                            setActiveMenu(

                                                activeMenu === session.id

                                                ?

                                                null

                                                :

                                                session.id

                                            );

                                        }}

                                        style={{

                                            background: "transparent",

                                            border: "none",

                                            color: "#ddd",

                                            fontSize: "22px",

                                            cursor: "pointer",

                                            borderRadius: "5px",

                                            padding: "2px 8px",

                                            transition: "0.2s"

                                        }}

                                    >

                                        ⋮

                                    </button>

                                </div>

                                <small
                                    style={{
                                        color: "#aaa"
                                    }}
                                >

                                    {

                                        session.pdf_name

                                    }

                                </small>

                                <br/>

                                <small
                                    style={{
                                        color: "#777"
                                    }}
                                >

                                    Session #

                                    {

                                        session.id

                                    }

                                </small>

                        {

                            activeMenu === session.id && (

                                <div

                                    className="chat-menu"

                                    style={{

position:"absolute",

top:"28px",

right:"0px",

minWidth:"160px",

background:"#333",

border:"1px solid #555",

borderRadius:"8px",

boxShadow:"0 6px 18px rgba(0,0,0,0.5)",

zIndex:999,

padding:"6px"

                                    }}

                                >

                                    <button

                                        onClick={async (e) => {

                                            e.stopPropagation();

                                            const token =
                                                localStorage.getItem(
                                                    "token"
                                                );

                                            await fetch(

                                                `http://127.0.0.1:8000/pin-session/${session.id}`,

                                                {

                                                    method: "PUT",

                                                    headers: {

                                                        Authorization:
                                                        `Bearer ${token}`

                                                    }

                                                }

                                            );

                                            loadChatSessions();

                                            setActiveMenu(null);

                                        }}

                                        style={{

                                            display: "block",

                                            width: "100%",

                                            background: "transparent",

                                            color: "white",

                                            border: "none",

                                            cursor: "pointer",

                                            padding: "5px 10px",

                                            textAlign: "left"

                                        }}

                                    >

                                        {

                                            session.is_pinned

                                            ?

                                            "📌 Unpin"

                                            :

                                            "📌 Pin"

                                        }

                                    </button>

                                    <button

                                        onClick={(e) => {

                                            e.stopPropagation();

                                            setRenameSessionId(
                                                session.id
                                            );

                                            setRenameTitle(
                                                session.title || ""
                                            );

                                            setShowRenameDialog(true);

                                            setActiveMenu(null);

                                        }}

                                        style={{

                                            display: "block",

                                            width: "100%",

                                            background: "transparent",

                                            color: "white",

                                            border: "none",

                                            cursor: "pointer",

                                            padding: "5px 10px",

                                            textAlign: "left"

                                        }}

                                    >

                                        ✏ Rename

                                    </button>

                                    <button

                                        onClick={async (e) => {

                                            e.stopPropagation();

                                            if (

                                                !window.confirm(
                                                    "Delete chat?"
                                                )

                                            ) return;

                                            const token =
                                                localStorage.getItem(
                                                    "token"
                                                );

                                            await fetch(

                                                `http://127.0.0.1:8000/chat-session/${session.id}`,

                                                {

                                                    method: "DELETE",

                                                    headers: {

                                                        Authorization:
                                                        `Bearer ${token}`

                                                    }

                                                }

                                            );

                                            loadChatSessions();

                                            setActiveMenu(null);

                                        }}

                                        style={{

                                            display: "block",

                                            width: "100%",

                                            background: "transparent",

                                            color: "#ff6666",

                                            border: "none",

                                            cursor: "pointer",

                                            padding: "5px 10px",

                                            textAlign: "left"

                                        }}

                                    >

                                        🗑 Delete

                                    </button>

                                </div>

                            )

                        }

                            </div>
                        )
                    )
                }

            </div>

                )

            }

            {/* MAIN APP */}

            <div
                className="app"
                style={{
                    flex: 1
                }}
            >

                <h1 className="title">

                    AI PDF Assistant

                </h1>

                {/* Upload */}

                <div className="card">

                    <h2>

                        Upload PDF

                    </h2>

                    <input

                        type="file"

                        accept=".pdf"

                        onChange={(e) =>

                            setFile(
                                e.target.files[0]
                            )
                        }
                    />

                    <br />

                    <button
                        onClick={handleUpload}
                    >

                        Upload PDF

                    </button>

                    <p>

                        {uploadMessage}

                    </p>

                </div>

                {/* PDF Selector */}

                <div className="card">

                    <h2>

                        Select Active PDF

                    </h2>

                    <select

                        value={selectedPDF}

                        onChange={(e) => {

                            setSelectedPDF(
                                e.target.value
                            );

                            setMessages([]);

                            setSessionId(null);
                        }}
                    >

                        <option value="">

                            Select PDF

                        </option>

                        {

                            uploadedPDFs.map(

                                (
                                    pdf,
                                    index
                                ) => (

                                    <option
                                        key={index}
                                        value={pdf}
                                    >

                                        {pdf}

                                    </option>
                                )
                            )
                        }

                    </select>

                    <p>

                        Active PDF:

                        {" "}

                        <strong>

                            {
                                selectedPDF
                            }

                        </strong>

                    </p>

                </div>

                {/* Chat */}

                <div className="card">

                    <h2>

                        Chat with PDF

                    </h2>

                    <div className="chat-container">

                        {

                            messages.map(

                                (
                                    message,
                                    index
                                ) => (

                                    <div

                                        key={index}

                                        className={

                                            message.role ===
                                            "user"

                                            ? "user-message"

                                            : "ai-message"
                                        }
                                    >

                                        <p>

                                            {message.text}

                                        </p>

                                        {

                                            message.sources && (

                                                <div
                                                    style={{
                                                        marginTop: "10px",
                                                        fontSize: "13px"
                                                    }}
                                                >

                                                    <strong>

                                                        Sources:

                                                    </strong>

                                                    {

                                                        message.sources.map(

                                                            (
                                                                source,
                                                                sourceIndex
                                                            ) => (

                                                                <div
                                                                    key={sourceIndex}
                                                                >

                                                                    <a

                                                                        href={
                                                                            `http://127.0.0.1:8000/view-pdf/${source.pdf_file}`
                                                                        }

                                                                        target="_blank"

                                                                        rel="noreferrer"

                                                                        style={{
                                                                            color: "#4da6ff"
                                                                        }}
                                                                    >

                                                                        {

                                                                            source.pdf_file
                                                                        }

                                                                    </a>

                                                                    {" | "}

                                                                    Page:

                                                                    {

                                                                        source.page_number
                                                                    }

                                                                    {" | "}

                                                                    Chunk:

                                                                    {

                                                                        source.chunk_number
                                                                    }

                                                                </div>
                                                            )
                                                        )
                                                    }

                                                </div>
                                            )
                                        }

                                    </div>
                                )
                            )
                        }

                    </div>

                    {/* INPUT */}

                    <input

                        type="text"

                        placeholder="Ask something..."

                        value={question}

                        onChange={(e) =>

                            setQuestion(
                                e.target.value
                            )
                        }
                        onKeyDown={(e) => {

                            if (
                                e.key === "Enter"
                            &&
                            !loading

                            ) {
                                handleAsk();
                            }
                        }}
                    />

                    <div
                        style={{
                            display: "flex",
                            gap: "10px",
                            marginTop: "10px"
                        }}
                    >

                        <button
                            onClick={handleAsk}
                        >

                            Send

                        </button>

                        <button
                            onClick={handleSummarize}
                        >

                            Summarize PDF

                        </button>

                    <button
                        onClick={async () => {

                            if (!sessionId) {

                                alert(
                                    "Open a chat session first"
                                );

                                return;
                            }

                            try {

                                const token =
                                    localStorage.getItem(
                                        "token"
                                    );

                                const response =
                                    await fetch(

                                        `http://127.0.0.1:8000/export-chat/${sessionId}`,

                                        {
                                            headers: {

                                                Authorization:
                                                `Bearer ${token}`
                                            }
                                        }
                                    );

                                if (!response.ok) {

                                    throw new Error(
                                        "Export failed"
                                    );
                                }

                                const blob =
                                    await response.blob();

                                const url =
                                    window.URL.createObjectURL(
                                        blob
                                    );

                                const a =
                                    document.createElement(
                                        "a"
                                    );

                                a.href = url;

                                a.download =
                                    `chat_session_${sessionId}.pdf`;

                                document.body.appendChild(
                                    a
                                );

                                a.click();

                                a.remove();

                                window.URL.revokeObjectURL(
                                    url
                                );

                            } catch (error) {

                                console.error(error);

                                alert(
                                    "Export failed"
                                );
                            }
                        }}
                    >

                        Export Chat

                    </button>

                    </div>

                </div>

            </div>

            {

                showRenameDialog && (

                    <div

                        style={{

                            position: "fixed",

                            top: "0",

                            left: "0",

                            width: "100%",

                            height: "100%",

                            background: "rgba(0,0,0,0.5)",

                            display: "flex",

                            justifyContent: "center",

                            alignItems: "center",

                            zIndex: 2000

                        }}

                    >

                        <div

                            style={{

                                background: "#1f1f1f",

                                color: "white",

                                border: "1px solid #444",

                                padding: "20px",

                                borderRadius: "8px",

                                minWidth: "300px"

                            }}

                        >

                            <h3>

                                Rename Chat

                            </h3>

                            <input

                                value={renameTitle}

                                onChange={(e) =>

                                    setRenameTitle(
                                        e.target.value
                                    )
                                }

                                style={{

                                    width: "100%",

                                    padding: "8px",

                                    borderRadius: "5px",

                                    border: "1px solid #555",

                                    background: "#2a2a2a",

                                    color: "white"

                                }}

                            />

                            <br/><br/>

                            <button

                                onClick={() => {

                                    setShowRenameDialog(false);

                                    setRenameSessionId(null);

                                    setRenameTitle("");

                                }}

                            >

                                Cancel

                            </button>

                            <button

                                onClick={async () => {

                                    const token =
                                        localStorage.getItem(
                                            "token"
                                        );

                                    await fetch(

                                        `http://127.0.0.1:8000/rename-session/${renameSessionId}`,

                                        {

                                            method: "PUT",

                                            headers: {

                                                "Content-Type":
                                                "application/json",

                                                Authorization:
                                                `Bearer ${token}`

                                            },

                                            body: JSON.stringify({

                                                title: renameTitle

                                            })

                                        }

                                    );

                                    loadChatSessions();

                                    setChatSessions((prev) =>

                                        prev.map((chat) =>

                                            chat.id === renameSessionId

                                                ? {

                                                    ...chat,

                                                    title: renameTitle

                                                }

                                                : chat
                                        )

                                    );

                                    setShowRenameDialog(false);

                                    setRenameSessionId(null);

                                    setRenameTitle("");

                                }}

                                style={{

                                    marginLeft: "10px"

                                }}

                            >

                                Save

                            </button>

                        </div>

                    </div>

                )

            }

        </div>
    );
}

export default ChatPage;