import { QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import App from "./App.jsx";
import { AppShell } from "./app/AppShell";
import { AuthProvider } from "./app/AuthContext";
import { ProtectedRoute } from "./app/ProtectedRoute";
import { queryClient } from "./app/queryClient";
import { ToastProvider } from "./components/primitives/Toast";
import "./index.css";
import { ComingSoon } from "./routes/ComingSoon.jsx";
import { Gallery } from "./routes/Gallery.jsx";
import { Login } from "./routes/Login.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <BrowserRouter>
          <AuthProvider>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/_gallery" element={<Gallery />} />
              <Route
                element={
                  <ProtectedRoute>
                    <AppShell />
                  </ProtectedRoute>
                }
              >
                <Route path="/" element={<App />} />
                <Route path="/briefs/:id" element={<ComingSoon title="Brief" />} />
                <Route path="/stories/:id" element={<ComingSoon title="Story detail" />} />
                <Route path="/alerts" element={<ComingSoon title="Alerts" />} />
                <Route path="/alerts/:id" element={<ComingSoon title="Signal detail" />} />
                <Route path="/weekly" element={<ComingSoon title="Weekly" />} />
                <Route path="/weekly/:id" element={<ComingSoon title="Weekly detail" />} />
                <Route
                  path="/admin/sources"
                  element={
                    <ProtectedRoute requireRole="admin">
                      <ComingSoon title="Admin — Sources" />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/recipients"
                  element={
                    <ProtectedRoute requireRole="admin">
                      <ComingSoon title="Admin — Recipients" />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/settings"
                  element={
                    <ProtectedRoute requireRole="admin">
                      <ComingSoon title="Admin — Settings" />
                    </ProtectedRoute>
                  }
                />
              </Route>
            </Routes>
          </AuthProvider>
        </BrowserRouter>
      </ToastProvider>
    </QueryClientProvider>
  </StrictMode>,
);
