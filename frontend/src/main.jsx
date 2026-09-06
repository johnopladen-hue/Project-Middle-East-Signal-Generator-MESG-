import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import App from "./App.jsx";
import { ToastProvider } from "./components/primitives/Toast";
import "./index.css";
import { Gallery } from "./routes/Gallery.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <ToastProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/_gallery" element={<Gallery />} />
          <Route path="/" element={<App />} />
        </Routes>
      </BrowserRouter>
    </ToastProvider>
  </StrictMode>,
);
