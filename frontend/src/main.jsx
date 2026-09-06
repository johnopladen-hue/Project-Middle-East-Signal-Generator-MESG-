import { QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AppShell } from "./app/AppShell";
import { AuthProvider } from "./app/AuthContext";
import { ProtectedRoute } from "./app/ProtectedRoute";
import { queryClient } from "./app/queryClient";
import { ToastProvider } from "./components/primitives/Toast";
import "./index.css";
import { Alerts } from "./routes/Alerts.jsx";
import { ComingSoon } from "./routes/ComingSoon.jsx";
import { Dashboard } from "./routes/Dashboard.jsx";
import { Gallery } from "./routes/Gallery.jsx";
import { Login } from "./routes/Login.jsx";
import { SignalDetail } from "./routes/SignalDetail.jsx";
import { Story } from "./routes/Story.jsx";
import { Weekly } from "./routes/Weekly.jsx";

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
                <Route path="/" element={<Dashboard />} />
                <Route path="/briefs/:id" element={<ComingSoon title="Brief" />} />
                <Route path="/stories/:id" element={<Story />} />
                <Route path="/alerts" element={<Alerts />} />
                <Route path="/alerts/:id" element={<SignalDetail />} />
                <Route path="/weekly" element={<Weekly />} />
                <Route path="/weekly/:id" element={<Weekly />} />
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
